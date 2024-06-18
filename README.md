#  Meraki - New Client Joined The Network Email Alert - Covene
## Script
For more detailed instructions, see the two blog posts at [Covene.com](https://covene.com/gather-network-clients-pt-1/). This will help setup Python, your virtual environment, and getting the required data and files.

This script will utilize the Meraki API to pull network client data, store it in a .JSON file, then sorts the data to find clients that have a first connected date that matches todays date. It then will create a .csv file and add entries to the file each time a new client connects to the network. The script checks if the new clients csv file has increased in size (aka a new client was found), and if so it utilizes Microsoft Azure to send an email notifying you that a new client was detected. It attaches the updated .csv file. 
## Assumptions

- Email Integration setup with Microsoft Azure.
    - This requires a paid account with microsoft.
    - Other third-party email servers would also be acceptable but will not be covered in this script. 
    - See reference guides below for instructions on how to configure the Azure integration.
- Time is formatted to USA Centeral Timezone.
- You want to re-run the get network clients check every 15 minutes.
- This script will loop with the time.sleep function. You could remove this use a cron job, or windows task scheduler- which may be a better long term option. 
- You have [environment variables](https://www.freecodecamp.org/news/python-env-vars-how-to-get-an-environment-variable-in-python/) configured, that store your Meraki ORG ID, and Meraki API. 
- You have a file named **'NetworkIDresponse.json'** created, that contains a list of network IDs. This can be obtained through a get networks API call. See blog post at - [Covene.com](https://covene.com/gather-network-clients-pt-1/)  for information on how to create this. 


## Instructions
You must first obtain your organizations ORG ID, and Network ID. You can use the Get-OrgID.py script to obtain your ORG ID, and the Get-NetworkIDs.py file to get all network IDs in your organization. The Get-NetworkClients python script assumes you have successfully ran the Get-NetworkIDs.py file. See Assumptions above for more information. To use this script, you will also need to configure the following in Azure:
- Communication Resource
- Email Communication Resource
- A Verified Domain or free azure domain.
- Obtain and store your Azure Communication Resource URL in the script.

You may also use another Email solution, such as [Google's Gmail](https://mailtrap.io/blog/python-send-email-gmail/).
Once you have the Get-NetworkIDs.py file ran successfully, you may run the Covene-GetNetworkClients-Email-Alert-Template.py script. You can download the **new-clients.csv** in this repository, for use to run along with the GetNetworkClients script.This is the file that gets emailed when a new client is found. 

 You will need to edit a few sections of this script for it to run, including:
- API_Key=
- ORG ID =
- Timezone Settings
- Email Settings
    - Your connection string is obtained from Azure- see Azure communication services email doc below.
        - connection_string=os.environ["Azure Communication Resource"] 
    - Edit your sender address- replace DoNotReply@DOMAIN.com
    - "to": [{"address": "ENTER EMAIL YOU WANT TO SEND TO HERE" }],

### Python Dependencies
**Use PIP install command to download each Python package**:
- meraki
- pytz
- pandas
- azure.communication.email
- azure.identity
- azure.core
- azure.identity

### Improvements To Be Made
The Get Network Clients script was created by a Network Engineer by trade, and not a python developer. AS a result, while this code functions, there is room for improvements. This script in the current form will work fine for small to medium sized organizations, however it does require many file read/write operations that could be reduced heavily. With a large number of networks for an organization, the read/write operations can be burdensome. Other items that may be useful for this script include:
- Use pandas library more effectively for csv manipulation, such as built-in sorting/filtering.
- Modularization: Break down the script into functions or classes to improve modularity. This makes the code easier to read and maintain.
- Exception Handling: Implement try-except blocks to handle potential exceptions that could occur during API calls or file operations.
- Update Mechanism: Implement a mechanism to check for updates or patches to dependencies, ensuring the script remains compatible with new versions of libraries.
- As stated above, it may be more reliable to utilize windows task scheduler or cron jobs instead of the built in while true loop for continued monitoring of new clients.
- At Times, you will get a random 503 error from Meraki when the dashoard does not respond in time, or if they are having issues. The script provided has no mechanism to re-start itself, or notify you that is has stopped running. 



### Reference Guides
- [Azure Communication Email client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python/)
- [Overview of Azure Communication Services email](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
- [Email domains and sender authentication for Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-domain-and-sender-authentication)
- [How to connect a verified email domain](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/connect-email-communication-resource?pivots=azure-portal)
- [Meraki Dashboard API Python Library](https://developer.cisco.com/meraki/api-v1/python/)
- [Get Network Clients - Meraki Dashboard API v1 - Cisco Meraki Developer Hub](https://developer.cisco.com/meraki/api-v1/get-network-clients/)
- [Meraki GitHub](https://github.com/meraki/dashboard-api-python/blob/main/README.md)
