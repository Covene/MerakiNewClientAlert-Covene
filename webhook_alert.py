#!/usr/bin/env python3
import meraki
import json
import requests
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
import schedule
import time


# Insert the api key where noted if you do not want to use an environment variable. 
api_key = os.environ["MERAKI_DASHBOARD_api_key"] 
# Destination for our events.
webhook_url = 'https://example.com/webhook'
# Create a Meraki Dashboard API session.
dashboard = meraki.DashboardAPI(api_key)
# Set the environment variable for the org ID, or paste it below.
org_id = os.environ["MERAKI_DASHBOARD_org_id"]


def get_network_ids(dashboard, org_id):
    # Get the networks for the specified organization.
    networks = dashboard.organizations.getOrganizationNetworks(org_id)
    # Create a list of dictionaries for network data.
    network_data = []

    for network in networks:
        network_info = {
            'id': network['id'],
            'timeZone': network['timeZone'],
            'name': network['name']
        }
        network_data.append(network_info)

    return network_data


def get_new_clients(dashboard, network_id, reference_time):
    # Get the clients for the specified network.
    clients = dashboard.networks.getNetworkClients(network_id, timespan=86400, perPage=5000)
    # Create a list of dictionaries for client data.
    client_data = []

    for client in clients:
        first_seen = client['firstSeen']
        if first_seen > reference_time:
            client_info = {
                'mac': client['mac'],
                'description': client.get('description', ''),
                'ip': client.get('ip', ''),
                'connectionType': client.get('recentDeviceConnection', ''),
                'connectedTo': client.get('recentDeviceName', ''),
                'ssid': client.get('ssid', ''),
                'switchport': client.get('switchport', ''),
                'firstSeen': datetime.fromtimestamp(first_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            }
            client_data.append(client_info)

    return client_data


def send_to_webhook(webhook_url, data):
    # Convert the data to JSON format
    json_data = json.dumps(data, indent=4)
    
    # Print the data that would be sent to the webhook
    print("Data to be sent to webhook:", json_data)

    # For now, just return the json_data for testing purposes
    return json_data

    # When ready to send data to the webhook, uncomment the following section...
    # headers = {
    #     'Content-Type': 'application/json'
    # }

    # # Send the POST request with the JSON data
    # response = requests.post(webhook_url, headers=headers, data=json_data)

    # # Check the response
    # if response.status_code == 200:
    #     print('Success:', response.json())
    # else:
    #     print('Failed:', response.status_code, response.text)

    # return response.status_code, response.json()


def job():
    try:
        # Reference time for determining new clients in the last 24 hours.
        reference_time = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Get network data
        network_data = get_network_ids(dashboard, org_id)

        all_new_clients = []
        for network in network_data:
            network_id = network['id']
            new_clients = get_new_clients(dashboard, network_id, reference_time)
            all_new_clients.extend(new_clients)

        if all_new_clients:
            # Convert the list of dictionaries to a Pandas DataFrame
            df = pd.DataFrame(all_new_clients)

            # Print the DataFrame to verify the data
            print(df)

            # Convert the DataFrame to JSON format
            json_data = df.to_json(orient='records')

            # Send the data to the webhook endpoint
            send_to_webhook(webhook_url, json_data)
        else:
            print("No new clients found")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Schedule the job every 15 minutes
    schedule.every(15).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
