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



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.communication.email').setLevel(logging.WARNING)

def get_env_variable(var_name): #Function that will get the environment variable from the system. This is used to get the API Key and Azure Communication Resource values.
    try:
        return os.environ[var_name]
    except KeyError:
        logging.error(f"Environment variable {var_name} not found. Please see: https://www.twilio.com/en-us/blog/how-to-set-environment-variables-html. Be sure to restart your IDE after adding an environment variable.")
        exit(1)


# UPDATE THESE TO MATCH YOUR ENVIRONMENT:
API_Key = get_env_variable("API_KEY")
csv_file_path = 'NewClients.csv'

# Check file size with improved error handling
try:
    # Check if the file exists to avoid FileNotFoundError
    if os.path.exists(csv_file_path):
        initial_size = os.path.getsize(csv_file_path)
        logging.info(f"The file {csv_file_path} initial size is {initial_size} bytes")
    else:
        logging.warning(f"The file {csv_file_path} does not exist. Please check the file path.")
except OSError as e:
    # Handle other potential errors like permission issues
    logging.error(f"Error accessing file {csv_file_path}: {e}. Please check file permissions and path.")




def GetOrgID(api_key): #This function will get the organization ID(s) that the API Key can access. This is required to run the GetNetworkIDs function.
    dashboard = meraki.DashboardAPI(api_key)
    orgresponse = dashboard.organizations.getOrganizations()
    if orgresponse:
        OrganizationID = orgresponse[0]["id"]
        OrgName = orgresponse[0]["name"]

        logging.info(f"\n\nThe Script will continue for the following ORG: {OrgName} with organization ID: {OrganizationID}.\n\n")
        time.sleep(2)
        if len(orgresponse) > 1:
            logging.info("Other Possible ORGs returned from API Call include:")
            for i, org in enumerate(orgresponse[1:], start=1):
                logging.info(f"{i}: {org['name']}")
            logging.info("Pausing to confirm. CTRL + C to Abort...") #You can remove this line if you are sure of the ORG ID you want to use.
            time.sleep(10)  #You can remove this line if you are sure of the ORG ID you want to use.
        else:
            logging.info("This is the only ORG ID found by the API call.")
        
        return OrganizationID, OrgName
    else:
        logging.error("No organizations found in the response.")
        return None, None



#This function will get all network IDs for the organization. 
# This is required to run the GetNetworkClients function.
def GetNetworkIDs(api_key, OrganizationID, OrgName): 
    logging.info(f"Getting network IDs for organization: {OrgName} (ID: {OrganizationID})")
    dashboard = meraki.DashboardAPI(api_key)
    networkresponse = dashboard.organizations.getOrganizationNetworks(OrganizationID)
    
    if not networkresponse:
        logging.error("No networks found for the organization.")
        return {}
    
    network_dict = {network.get('id'): network.get('name') for network in networkresponse if network.get('id') and network.get('name')}
    
    logging.info(f"The API will gather network client information for the following Networks:\n {json.dumps(network_dict, indent=4)}\n")
    time.sleep(1)
    return network_dict



#This function will get all network clients for the ech network returned in the GetNetworkIDs function.
def GetNetworkClients(network_dict, api_key):
    output_file = "network_clients_data.json"
    dashboard = meraki.DashboardAPI(api_key)
    
    try:
        with open(output_file, 'r') as file:
            network_clients_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        network_clients_data = {}

    for network_id, network_name in network_dict.items():
        logging.info(f"\n\n*********Running API GET for {network_name} (ID: {network_id})*********\n")
        try:
            response = dashboard.networks.getNetworkClients(
                network_id, timespan=86400, perPage=5000
            )

            network_clients_data[network_id] = {
                "network_name": network_name,
                "clients": response
            }

            with open(output_file, 'w') as file:
                json.dump(network_clients_data, file, indent=4)
           
            logging.info(f"Gathering Network clients for {network_name}")

        except meraki.exceptions.APIError as e:
            logging.error(f"API error occurred for network {network_name}: {e}")
        except Exception as e:
            logging.error(f"An error occurred for network {network_name}: {e}")
    return network_clients_data


#This function will convert the UTC time to local time.
def convert_to_local_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    local_tz = get_localzone()
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_time


#This function will filter the new clients that have connected to the network today, for the first time.
def FindNewClients(network_clients_data, csv_file_path):
    FilteredClientData = "Filtered_Client_data.json"
    NewClientInfo = []

    for network_id, network_data in network_clients_data.items():
        network_name = network_data.get("network_name", "Unknown Network")
        clients = network_data.get("clients", [])

        for client in clients:
            first_seen_utc = client.get("firstSeen")
            if first_seen_utc:
                first_seen_local = convert_to_local_time(first_seen_utc)
                readable_first_seen = first_seen_local.strftime("%Y-%m-%d %H:%M:%S")

                today_local = datetime.now(get_localzone()).date()
                is_today = first_seen_local.date() == today_local

                #update your Guest Network(s) Here If you Would Like To Exclude notifications for new  clients on the guest network.
                if is_today and client.get("ssid") != "GuestNetwork":
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

    with open(FilteredClientData, 'w') as file:
        json.dump(NewClientInfo, file, indent=4)
        logging.info(f"Saved Filtered Client Data to {FilteredClientData}")
        logging.info(NewClientInfo)
    
    current_size = 0
    try:
        if NewClientInfo:
            headers = NewClientInfo[0].keys()

            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(NewClientInfo)

            logging.info(f"Data has been written to {csv_file_path}")
            
        else:
            logging.info("No new client data to write.")
        
        if os.path.exists(csv_file_path):
            current_size = os.path.getsize(csv_file_path)
            logging.info(f"The Updated New Client CSV File Size Is: {current_size} bytes")
        else:
            logging.warning(f"The file {csv_file_path} does not exist after writing.")
    
    except Exception as e:
        logging.error(f"Error writing to CSV: {e}")

    return NewClientInfo, current_size



#This function will send an email to the recipient with the new client data attached.
def EmailNewClients(csv_file_path, initial_size, current_size, OrgName):
    if current_size > initial_size:
        with open(csv_file_path, "r") as file:
            file_contents = file.read()

        file_bytes_b64 = base64.b64encode(bytes(file_contents, 'utf-8')).decode()
        logging.info(f'File change detected. Attempting to Send email...')

        try:
            connection_string = get_env_variable("Azure Communication Resource")
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
            logging.info(f'Email Sent Successfully.')
        
        except Exception as ex:
            logging.error(f"Failed to send email: {ex}")
    else:
        logging.info("No new clients detected. No email sent.")


#This is the main function that will run the script. It will call all the functions above.
def main():
    global initial_size
    while True:
        logging.info("Starting script run...")
        
        OrganizationID, OrgName = GetOrgID(API_Key)
        if OrganizationID:
            network_dict = GetNetworkIDs(API_Key, OrganizationID, OrgName)
            if network_dict:
                network_clients_data = GetNetworkClients(network_dict, API_Key)
                NewClientInfo, current_size = FindNewClients(network_clients_data, csv_file_path)
                if NewClientInfo:
                    EmailNewClients(csv_file_path, initial_size, current_size, OrgName)
                    initial_size = current_size
        
        Sleeptime = 120
        logging.info(f"Script run complete. Sleeping for {Sleeptime} seconds...")
        time.sleep(Sleeptime)

if __name__ == "__main__":
    main()
