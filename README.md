#  Meraki - New Client Joined The Network Email Alert - Covene
## Script
For more detailed instructions, see the two blog posts at [Covene.com](https://covene.com/gather-network-clients-pt-1/). This will help setup Python, your virtual environment, and getting the required data and files.

This script will utilize the Meraki API to pull network client data, then sorts the data to find clients that have a first connected date that matches todays date. It then will create a .csv file and add entries to the file each time a new client connects to the network. The script checks if the new clients csv file has increased in size (aka a new client was found), and if so it utilizes Microsoft Azure to send an email notifying you that a new client was detected. It attaches the updated .csv file. 

## Assumptions

- Email Integration setup with Microsoft Azure.
    - This requires a paid account with microsoft.
    - Other third-party email servers would also be acceptable but will not be covered in this script. 
    - See reference guides below for instructions on how to configure the Azure integration.
- You want to re-run the get network clients check every x minutes. (change the variable Sleeptime=x to change how long to wait between re-tries.) 
- You have [environment variables](https://www.freecodecamp.org/news/python-env-vars-how-to-get-an-environment-variable-in-python/) configured, that store your Meraki API Key, and Azure communication resource string. 

## Instructions
 To use this script, you will  need to configure the following in Azure:
- Communication Resource
- Email Communication Resource
- A Verified Domain or free azure domain.
- Obtain and store your Azure Communication Resource URL in the script.

See the references at the bottom of this file to review instructions on creating azure communication resources and setting up a domain. 

You may also use another Email solution, such as [Google's Gmail](https://mailtrap.io/blog/python-send-email-gmail/).


 You will need to edit a few sections of this script for it to run, including:
- API_Key=
- Email Settings
    - Your connection string is obtained from Azure- see Azure communication services email doc below.
        - connection_string=os.environ["Azure Communication Resource"] 
    - Edit your sender address- replace DoNotReply@DOMAIN.com
    - "to": [{"address": "ENTER EMAIL YOU WANT TO SEND TO HERE" }],


### Organizations
If your API key has access to more than one organization, this script will by default choose the first returned Organization. 

In the GetOrgID function, see the following section:

    if orgresponse:
            OrganizationID = orgresponse[0]["id"]
            OrgName = orgresponse[0]["name"]

To Change the ORG ID, run the script and you will be presented with the full list of ORG's available. Example:

    The Script will continue for the following ORG: ORG0 with organization ID: 697526.


    2024-07-19 14:17:59,630 - INFO - Other Possible ORGs returned from API Call include:
    2024-07-19 14:17:59,630 - INFO - 1: ORG0
    2024-07-19 14:17:59,630 - INFO - 2: ORG1
    2024-07-19 14:17:59,630 - INFO - 3: ORG2
    2024-07-19 14:17:59,631 - INFO - 4: ORG3
    2024-07-19 14:17:59,631 - INFO - 5: ORG4
    2024-07-19 14:17:59,631 - INFO - 6: ORG5
    2024-07-19 14:17:59,631 - INFO - 7: ORG6
    2024-07-19 14:17:59,631 - INFO - 8: ORG7
    2024-07-19 14:17:59,631 - INFO - 9: ORG8
    2024-07-19 14:17:59,632 - INFO - 10: ORG9


From the example above, the script will default to running the API request against Org0. If you wish to run the API call against Org7 for example, update the code as follows: 

    if orgresponse:
            OrganizationID = orgresponse[7]["id"]
            OrgName = orgresponse[7]["name"]

If you only have access to 1 organization, the script will not show the above messaging and proceed with the Organization.

### Networks
The GetNetworkIDs function will show the networks that it is going to pull from. There is currently no mechanism to pick and chose the networks you want to be alerted on. This may change with future updates, but for now all networks are included. 


### Exclude Guest Networks
This cript has an Capibility to exclude clients that connect to guest networks. In the script, search for: 

    if is_today and client.get("ssid") != "GuestNetwork":

Replace the "GuestNetwork" with the name of the wireless guest network you would like to exclude from alerting. You can also exclude more than one guest network name by adding another and statment like so:

    if is_today and client.get("ssid") != "GuestNetwork" and client.get("ssid") != "GuestNetwork2":


### Python Dependencies
**Use pip install -r requirements.txt command to download each Python package**:

Ensure you download the requirements.txt file, and then run pip install -r requirements.txt. Eack required package will be downloaded. The requirements.txt file contains all the packages used by the script. 

Please note that a [virtual environment](https://docs.python.org/3/library/venv.html) will help isolate package dependencies, and ensure each package is found by the IDE.

Also, you may need to change your python interpreter to use the virtual environment with CTRL + SHIFT + P and search Python: Select Interpreter. Ensure the virtual environment is chosen. 

Finally, this script was built on python 3. 

### Improvements To Be Made
The Get Network Clients script was created by a Network Engineer by trade, and not a python developer. As a result, while this code functions, there is room for improvements. Items that may be useful for this script include:
- JSON files are created but not really required. They are there mosyly to provide you with the raw data from the API request. Feel free to tweak and remove the json files from being used. 
- Update Mechanism: Implement a mechanism to check for updates or patches to dependencies, ensuring the script remains compatible with new versions of libraries.
- As stated above, it may be more reliable to utilize windows task scheduler or cron jobs instead of the built in while true loop for continued monitoring of new clients.
- At Times, you will get a random 503 error from Meraki when the dashoard does not respond in time, or if they are having issues. The script provided has no mechanism to re-start itself, or notify you that is has stopped running. 
- There is no option to specify what networks you want to include or exclude. All networks in a meraki org will be included in the API currently. 



### Reference Guides
- [Azure Communication Email client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python/)
- [Overview of Azure Communication Services email](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
- [Quickstart For Azure Communication Service](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/create-email-communication-resource?pivots=platform-azp)
- [Email domains and sender authentication for Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-domain-and-sender-authentication)
- [How to connect a verified email domain](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/connect-email-communication-resource?pivots=azure-portal)
- [Meraki Dashboard API Python Library](https://developer.cisco.com/meraki/api-v1/python/)
- [Get Network Clients - Meraki Dashboard API v1 - Cisco Meraki Developer Hub](https://developer.cisco.com/meraki/api-v1/get-network-clients/)
- [Meraki GitHub](https://github.com/meraki/dashboard-api-python/blob/main/README.md)
