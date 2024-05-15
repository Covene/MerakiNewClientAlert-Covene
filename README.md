# Covene Meraki API Get Network Clients
## Script
This script will utilize the Meraki API to pull network client data, storer it in a .JSON file, then sorts the data to find clients that have a first connected date that matches todays date. It then will create a .csv file and add entries to the file each time a new client connects to the network. The script checks if the new clients csv file has increased in size (aka a new client was found), and if so it utilizes Microsoft Azure to send an email notifying you that a new client was detected. It attaches the updated .csv file. 
## Assumptions

- Email Integration setup with Microsoft Azure.
    - This requires a paid account with microsoft.
    - Other third-party email servers would also be acceptable but will not be covered in this script. 
- Time is formatted to USA Centeral Timezone.
- You want to re-run the get network clients check every 15 minutes.
- This script will loop with the time.sleep function. You could remove this and schedule the script to run with another system, such as task scheduler. 
- You have environment variables configured, that store your Meraki ORG ID, and Meraki API. 
- You have a file named 'NetworkIDresponse.json' created. See blog post at - [Covene.com](https://covene.com/news-blog/)  for information on how to create this. 


## Instructions
You can download the new-clients.csv in this directory, for use to run along with this script. This is the file that gets emailed when a new client is found.

### Python Dependencies
- Use PIP install command to download each Python package:
- meraki
- pytz
- pandas
- azure.communication.email
- azure.identity
- azure.core
- azure.identity

### Reference Guides
[Azure Communication Email client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python/)
[Overview of Azure Communication Services email](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
[Email domains and sender authentication for Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-domain-and-sender-authentication)
[Get Network Clients - Meraki Dashboard API v1 - Cisco Meraki Developer Hub](https://developer.cisco.com/meraki/api-v1/get-network-clients/)
