import meraki
import json
import time
import os
import pytz
import base64
import glob
import re
import csv
import pandas as pd
import azure.communication.email
import azure.identity
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from datetime import datetime

#Creates a loop that the script will repeat after running through all indented code. 
while True:
    #Check the current size of the newclients.csv file before running the API
    with open("New-Clients.csv", "r") as file:
        file_contents = file.read()
    file_path = "New-Clients.csv"
    initial_size = os.path.getsize(file_path)
    
    #Implement your own API key here. Use API_Key=os.environ["MERAKI_DASHBOARD_API_KEY"] to use an envionment variable. Replace the quoted text with your environment variable name. 
    API_Key=os.environ["MERAKI_DASHBOARD_API_KEY"] 

    dashboard = meraki.DashboardAPI(API_Key)

    #Edit the org ID with the company you want to pull the networks for.
    org_id = os.environ["org_id"] 

    #Opens the networkID response from the first blogpost. 
    with open('NetworkIDresponse.json', 'r') as f:
        networks = json.load(f)

    #For each entry in the networkID response .JSON file, run an API get file for each 'name' (IE - each network). 
    for network in networks:
        network_id = network['id']
        Network_Timezone = network['timeZone']
        network_name = network['name']
    
        print(f'[API]*********Deleting contents of {network_name} Files...*********')

        # Specify the file paths
        file_paths = [f'{network_name}-response.json',f'{network_name}-NewClients.csv']

        for file_path in file_paths:
            # Check if the file exists
            if os.path.exists(file_path):
                # If the file exists, clear it by opening it in write mode and closing it
                open(file_path, 'w').close()
            else:
                # If the file doesn't exist, create an empty file by opening it in write mode and closing it
                open(file_path, 'w').close()
                
        print(f'[API]********* {network_name} File conents Erased*********')
        time.sleep(1)

        print(f'[API]*********Running API GET for {network_name}*********')

        response = dashboard.networks.getNetworkClients(
            network_id, timespan =86400, perPage=5000
        )
        
        print(f'[API]*********{network_name} API Request Completed. Please wait while the .CSV output files are created.....*********')
       
        with open(f'{network_name}-response.json', 'w') as f:
            json.dump(response, f, indent=4)        
        # Open the Newly Created JSON file
        with open(f'{network_name}-response.json', 'r') as f:
            data = json.load(f)

        # Open the CSV file in write mode
        with open(f'{network_name}-NewClients.csv', 'w', newline='') as out:
            # Create a CSV writer
            writer = csv.writer(out)
            # Write the header to the CSV file
            writer.writerow(['Network Name', 'MAC', 'Description', 'IP Address', 'Connection Type', 'Connected To', 'SSID', 'Switchport', 'Time'])
            rows = []
            # Iterate over each dictionary in the list
            for d in data:
                timestamp = d['firstSeen']
                # Convert the timestamp string to a datetime object
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                # Set the current timezone to UTC
                dt = dt.replace(tzinfo=pytz.UTC)
                # Convert the datetime object to the Central Time Zone
                central = pytz.timezone('US/Central')
                dt_central = dt.astimezone(central)
                current_date_central = datetime.now(central).date()
                # Format the datetime object to a more readable format
                formatted_dt = dt_central.strftime("%m-%d-%Y %H:%M:%S")
                first_seen = d.get('firstSeen')
                ssid = d.get('ssid')
                #Checks if the first seen date = todays date. If so, add an entry to the .csv file.
                if first_seen:
                    first_seen_date = dt_central.date()
                    if first_seen_date == current_date_central:
                        rows.append([network_name, d['mac'], d['description'], d['ip'], d['recentDeviceConnection'], d['recentDeviceName'], d['ssid'], d['switchport'], formatted_dt])
            #Sorts the data so the newest is at the top of the .csv file, and saves.                        
            rows.sort(key=lambda x: datetime.strptime(x[8], "%m-%d-%Y %H:%M:%S"), reverse=True)
            for row in rows:
                writer.writerow(row)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")

    # Get all csv files in the current directory
    csv_files = [f for f in os.listdir() if f.endswith('.csv') and 'NewClients' in f]

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Iterate over each csv file
    for csv_file in csv_files:
        # Read the csv file
        temp_df = pd.read_csv(csv_file)
        # Append the data to the DataFrame
        df = df._append(temp_df, ignore_index=True)

    # Write the combined data to a new csv file
    df.to_csv('New-Clients.csv', index=False)

    # Open the CSV file in read mode
    with open('New-Clients.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Get the header row
        rows = list(reader)  # Get the rest of the rows

    # Find the index of the 'time' column in the header
    time_index = header.index('Time')

    # Sort the rows based on the 'time' column
    rows.sort(key=lambda x: datetime.strptime(x[time_index], "%m-%d-%Y %H:%M:%S"), reverse=True)

    # Open the CSV file in write mode
    with open('New-Clients.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)  # Write the header row
        writer.writerows(rows)  # Write the sorted rows

    # Print a success message
    print(f"{formatted_time}:[API]All csv files containing 'NewClients.csv' in the name have been combined into 'New-Clients.csv'.")

    print(f"{formatted_time}:[API]Checking if file needs to be emailed...")

    with open("New-Clients.csv", "r") as file:
        file_contents = file.read()

    file_path = "New-Clients.csv"
    initial_mtime = os.path.getmtime(file_path)
    current_time = datetime.now()
    current_size = os.path.getsize(file_path)
    current_mtime = os.path.getmtime(file_path)

    if current_size > initial_size:
        # File size has changed and the last update was within the last 210 seconds, send the email
        with open(file_path, "r") as file:
            file_contents = file.read()
        file_bytes_b64 = base64.b64encode(bytes(file_contents, 'utf-8'))
        print(f'[Email-Section] File change detected at {formatted_time}. Attempting to Send email...')
        def main():
            try:
                connection_string=os.environ["Azure Communication Resource"]
                client = EmailClient.from_connection_string(connection_string)
                message = {
                    "senderAddress": "DoNotReply@DOMAIN.com",
                    "recipients":  {
                        "to": [{"address": "ENTER EMAIL YOU WANT TO SEND TO HERE" }], #UPDATE THIS to the email address you want to send to. 
                    },
                    "content": {
                        "subject": " New Client Connected To The Network",
                        "plainText": f"{file_path} \n Access the Meraki Dashboard here: https://dashboard.meraki.com/ " ,
                        "html": f"""
                            <html>
                                <h1 style='font-size: 0.9em;'>A new client has connected to the network. See the attached file, and review in the <a href='https://dashboard.meraki.com/'>Meraki Dashboard</a></h1>
                            </html>
                        """},
                            "attachments": [
                                {
                                    "name": "New-Clients.csv",
                                    "contentType": "text/html",
                                    "contentInBase64": file_bytes_b64.decode()
                                        }
                                    ]
                                }
                poller = client.begin_send(message)
                result = poller.result()
            except Exception as ex:
                print(ex)
                #Add email of ex here. 
            else:
                current_time = datetime.now()
                formatted_time = current_time.strftime("%H:%M:%S")
                print(f'[Email-Section] Email Sent Successfully at {formatted_time}')
        main()
        initial_size = current_size  # Update the initial size
        initial_mtime = current_mtime  # Update the initial modification time
        print(f"{formatted_time}:[Email-Section] Script waiting 15 minutes before checking database once more....")
        time.sleep(900)
    else:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(f"{formatted_time}:[Email-Section] {file_path} File Size has not changed. Supressing duplicate Email alert notification.")
        print(f"{formatted_time}:[Email-Section] Script waiting 15 Minutes before checking again....")
        time.sleep(900)


