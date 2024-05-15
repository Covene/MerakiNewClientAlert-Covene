# Covene Meraki API Get Network Clients
## Script
This script will utilize the Meraki API to pull network client data, storer it in a .JSON file, then sorts the data to find clients that have a first connected date that matches todays date. It then will create a .csv file and add entries to the file each time a new client connects to the network. The script checks if the new clients csv file has increased in size (aka a new client was found), and if so it utilizes Microsoft Azure to send an email notifying you that a new client was detected. It attaches the updated .csv file. 
## Assumptions

- Email Integration setup with Microsoft Azure.
    - This requires a paid account wiht microsoft.
- Time is formatted to USA Centeral Timezone.
- You want to re-run the get network clients check every 15 minutes.
- This script will loop with the time.sleep function. You could remove this and schedule the script to run with another system, such as task scheduler. 
- You have environment variables configured, that store your ORG ID, and Meraki API. 
- You have a file named 'NetworkIDresponse.json' created. See blog post at covene.com for information on how to create this. 

## Instructions
You can download the new-clients.csv in this directory, for use to run along with this script. This is the file that gets emailed when a new client is found.




