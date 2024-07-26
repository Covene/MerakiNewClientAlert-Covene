import meraki
import logging
import os
import json
import time
from datetime import datetime
import pytz
from tzlocal import get_localzone
import csv
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
import base64
import urllib3
import custom_logger

logger = custom_logger.setup_logger('Meraki', 'Meraki-API-Logs.log')

# Set up logging
def setup_logger():
    # Setup the logger
    logger = custom_logger.setup_logger('Meraki', 'Meraki-API-Logs.log')
    return logger

#Function that will get the environment variable from the system. This is used to get the API Key and Azure Communication Resource values.
def get_env_variable(var_name,logger):
    try:
        return os.environ[var_name]
    except KeyError:
        logger.error(f"Environment variable '{var_name}' not found. Please see: https://www.twilio.com/en-us/blog/how-to-set-environment-variables-html. Be sure to restart your IDE after adding an environment variable")
        exit(1)


# UPDATE THESE TO MATCH YOUR ENVIRONMENT:
API_Key = get_env_variable("API_Key", logger)
csv_file_path = 'NewClients.csv'




#function that checks if the file size of the .csv has increased. 
def CheckCSVRows(csv_file_path, logger):
    try:
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as file:
                reader = csv.reader(file)
                # Subtract 1 to exclude the header row
                num_entries = sum(1 for row in reader)
            if num_entries > 0:
                num_entries -= 1
                logger.info(f"File has {num_entries} entries.") 
                return num_entries  
            if num_entries == 0:
                logger.info(f"{csv_file_path} File is empty.")
            return num_entries
        else:
            logger.warning(f"The file {csv_file_path} does not exist. Please check the file path.")
            return 0
    except OSError as e:
        logger.error(f"Error accessing file {csv_file_path}: {e}. Please check file permissions and path.")
        return 0


#This function will get the organization ID(s) that the API Key can access. This is required to run the GetNetworkIDs function.
def GetOrgID(api_key,logger):
    dashboard = meraki.DashboardAPI(api_key)
    orgresponse = dashboard.organizations.getOrganizations()
    if orgresponse:
        OrganizationID = orgresponse[2]["id"]
        OrgName = orgresponse[2]["name"]

        logger.info(f"\n\nThe Script will continue for the following ORG: {OrgName} with organization ID: {OrganizationID}.\n\n")
        time.sleep(2)
        if len(orgresponse) > 1:                        #You can remove this section if you are sure of the ORG ID you want to use.
            logger.info("Other Possible ORGs returned from API Call include:") 
            for i, org in enumerate(orgresponse[1:], start=1): 
                logger.info(f"{i}: {org['name']}")
            logger.info("Pausing to confirm. See README.MD for instructions on how to change the ORG. CTRL + C to Abort...")
            time.sleep(8)
        else:
            logger.info("This is the only ORG ID found by the API call.")  #This is the end of the section that can be removed if you are sure of the ORG ID you want to use.
        
        return OrganizationID, OrgName
    else:
        logger.error("No organizations found in the response.")
        return None, None



#Gets the Network ID's for the ORG ID that was returned from the GetOrgID function. This is required to run the GetNetworkClients function.
def GetNetworkIDs(api_key, OrganizationID, OrgName,logger):
    logger.info(f"Getting network IDs for organization: {OrgName} (ID: {OrganizationID})")
    dashboard = meraki.DashboardAPI(api_key)
    networkresponse = dashboard.organizations.getOrganizationNetworks(OrganizationID)
    
    if not networkresponse:
        logger.error("No networks found for the organization.")
        return {}
    
    network_dict = {network.get('id'): network.get('name') for network in networkresponse if network.get('id') and network.get('name')}
    
    logger.info(f"The API will gather network client information for the following Networks:\n {json.dumps(network_dict, indent=4)}\n")
    return network_dict

#This function will get the network clients for the network ID's that were returned from the GetNetworkIDs function.
def GetNetworkClients(network_dict, api_key,logger):
    output_file = "network_clients_data.json"
    dashboard = meraki.DashboardAPI(api_key)
    
    try:
        with open(output_file, 'r') as file:
            network_clients_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        network_clients_data = {}

    for network_id, network_name in network_dict.items():
        logger.info(f"**Running API GET for {network_name} (ID: {network_id})*")
        try:
            response = dashboard.networks.getNetworkClients(
                network_id, timespan=86400, perPage=5000
            )

            network_clients_data[network_id] = {
                "network_name": network_name,
                "clients": response
            }

            try:
                with open(output_file, 'w') as file:
                    json.dump(network_clients_data, file, indent=4)
                logger.info(f"Gathered Network clients for {network_name}")
            except Exception as e:
                logger.error(f"An error occurred while writing network clients data to file: {e}")

        except meraki.exceptions.APIError as e:
            logger.error(f"API error occurred for network {network_name}: {e}")
        except Exception as e:
            logger.error(f"An error occurred for network {network_name}: {e}")
    return network_clients_data

#This function will convert the UTC time to local time. This is used to convert the first seen time of the client to local time.
def convert_to_local_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    local_tz = get_localzone()
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_time

#This function will filter the client data to only include clients that have connected to the network today and are not on the Guest Network.
def FindNewClients(network_clients_data, csv_file_path,logger):
    FilteredClientData = "Filtered_Client_data.json"
    NewClientInfo = []
    today_local = datetime.now(get_localzone()).date()
    logger.info(f"Todays date: {today_local}")
    try:
        for network_id, network_data in network_clients_data.items():
            network_name = network_data.get("network_name", "Unknown Network")
            clients = network_data.get("clients", [])

            for client in clients:
                first_seen_utc = client.get("firstSeen")
                if first_seen_utc:
                    first_seen_local = convert_to_local_time(first_seen_utc)
                    readable_first_seen = first_seen_local.strftime("%Y-%m-%d %H:%M:%S")
                    
                    is_today = first_seen_local.date() == today_local
                    #update your Guest Network Here
                    if is_today and client.get("ssid") != "Guest!Network":
                        client_info = {
                            "Network Name": network_name,
                            "Client ID": client.get("id"),
                            "Description": client.get("description"),
                            "IP Address": client.get("ip"),
                            "MAC Address": client.get("mac"),
                            "SSID": client.get("ssid"),
                            "VLAN": client.get("vlan"),
                            "Switchport": client.get("switchport"),
                            "First Seen Time(local)": readable_first_seen,
                            "Recent Device": client.get("recentDeviceConnection"),
                            "Recent Device Name": client.get("recentDeviceName"),
                        }
                        NewClientInfo.append(client_info)
                        logger.info(f"New client Detected. First seen time for Client MAC: {client.get('mac')}: {readable_first_seen}")
                        #Uncomment the 2 lines below to see a list of all clients, regardless of first connected date. This is useful for troubleshooting. 
                    #else: 
                        #logger.info(f"Client MAC: {client.get('mac')}First seen on: {readable_first_seen} is not today's date.")    
        with open(FilteredClientData, 'w') as file:
            json.dump(NewClientInfo, file, indent=4)
            logger.info(f"Saved Filtered Client Data to {FilteredClientData}")
            

    except Exception as e:
        logger.error(f"An error occurred while filtering client data: {e}")
    try:
        if NewClientInfo:
            headers = NewClientInfo[0].keys()

            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(NewClientInfo)

            logger.info(f"Data has been written to {csv_file_path}")
            
        else:
            logger.info("No new client data to write.")
        
        
    except Exception as e:
        logger.error(f"Error writing to CSV: {e}")

    return NewClientInfo


#This function will send an email with the new client data if the file size has increased. This requires an Azure Communication Resource to be set up. See Readme for more information.
def EmailNewClients(csv_file_path, OrgName,logger):
    
    with open(csv_file_path, "r") as file:
        file_contents = file.read()

    file_bytes_b64 = base64.b64encode(bytes(file_contents, 'utf-8')).decode()
    logger.info(f'File change detected. Attempting to Send email...')

    try:
        connection_string = get_env_variable("Azure Communication Resource",logger) #Ensure you have an environment variable called Azure Communication Resource. Restart your IDE after creating this in your environment.
        client = EmailClient.from_connection_string(connection_string)
        message = {         #Update your Sender Email ADdress Below
            "senderAddress": "DoNotReply@domain.com",
            "recipients":  { #Update Your Email Address Below
                "to": [{"address": "UpdateEmailAddressHere@domain.com" }],
            },
            "content": {
                "subject": f"{OrgName} - New Client Connected To The Network",
                "plainText": f"{csv_file_path} \n Access the Meraki Dashboard here: https://dashboard.meraki.com/ ",
                "html": f"""
                    <html>
                        <h1 style='font-size: 0.9em;'>A new client has connected to the {OrgName} network. See the attached file, and review in the <a href='https://dashboard.meraki.com/'>Meraki Dashboard</a></h1>
                    </html>
                """},
            "attachments": [
                {
                    "name": "New-Clients.csv",
                    "contentType": "text/csv",
                    "contentInBase64": file_bytes_b64
                }
            ]
        }
        poller = client.begin_send(message)
        result = poller.result()
        logger.info(f'Email Sent Successfully.')
    
    except Exception as ex:
        logger.error(f"Failed to send email: {ex}")


#This function will clear the contents of the CSV file. This is done at the start of the script run to ensure that the file is empty before writing new data to it.
def ClearCSV(csv_file_path,logger):
    try:
        with open(csv_file_path, 'w') as file:
            pass  # Opening in 'w' mode already truncates the file.
        logger.info(f"Successfully cleared the contents of {csv_file_path}")
    except Exception as e:
        logger.error(f"Error clearing the contents of {csv_file_path}: {e}")

#This function will disable the warnings that are generated when using the verify=False parameter in the requests.get() function. This is used to suppress the warnings that are generated when using the Meraki API.
def disable_warnings(logger):
    try:
        # Suppress only the single InsecureRequestWarning from urllib3 needed for verify=False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception as e:
        logger.error(f'An error occurred while disabling warnings: {e}')        

#Main function that will run the script. This function will run the functions in the correct order to gather the data, filter the data, and send an email if new clients are detected.
def main():
    while True:
        logger = setup_logger()
        disable_warnings(logger)
        csv_file_path = 'NewClients.csv'
        logger.info("Starting script run...")
        
       # Check the file size at the start of the loop
        start_size = CheckCSVRows(csv_file_path,logger)
        logger.info(f"{csv_file_path} file has {start_size} entries.")
        
        # Clear the contents of the CSV file
        ClearCSV(csv_file_path,logger)
        ClearCSV("network_clients_data.json",logger)
        ClearCSV("Filtered_Client_data.json",logger)
        OrganizationID, OrgName = GetOrgID(API_Key,logger)
        if OrganizationID:
            network_dict = GetNetworkIDs(API_Key, OrganizationID, OrgName, logger)
            if network_dict:
                network_clients_data = GetNetworkClients(network_dict, API_Key,logger)
                NewClientInfo = FindNewClients(network_clients_data, csv_file_path,logger)
                
                # Check the file size after the operations
                end_size = CheckCSVRows(csv_file_path,logger)
                
                # Compare the start and end file sizes
                if end_size > start_size:
                    logger.info(f"File size increased. Inital size: {start_size}. End size: {end_size}.")
                    EmailNewClients(csv_file_path, OrgName,logger)
                else:
                    logger.info(f"File size not increased. Inital size: {start_size}. End size: {end_size}")
        #Edit this to change how long the script waits before running again. The default is  800 seconds.
        Sleeptime = 800
        logger.info(f"Script run complete. Sleeping for {Sleeptime} seconds...")
        time.sleep(Sleeptime)

if __name__ == "__main__":
    main()