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


## Instructions
 To use this script, you will  need to configure the following in Azure:
- Communication Resource
- Email Communication Resource
- A Verified Domain or free azure domain.
- Obtain and store your Azure Communication Resource URL in the script.


See the references at the bottom of this file to review instructions on creating azure communication resources and setting up a domain. You may also use another Email solution, such as [Google's Gmail](https://mailtrap.io/blog/python-send-email-gmail/).

### Setup
- You will need to have two [environment variables](https://www.freecodecamp.org/news/python-env-vars-how-to-get-an-environment-variable-in-python/) configured, that store your Meraki API Key, and Azure communication resource string. In the script, the API has the following Environment Variables being called:
    -"API_Key"
    -"Azure Communication Resource"
 You will need to edit a few sections of this script for it to run properly. See the app_config file. 
- API_Key=
- Email Settings
    - Your connection string is obtained from Azure- see Azure communication services email doc below. The value should look like: "endpoint=https://{_YourConnectionStringHere_}
        - connection_string=os.environ["Azure Communication Resource"] 
    - Edit your sender address- replace DoNotReply@DOMAIN.com with the domain you verify, or a free azure domain.
    - "to": [{"address": "ENTER EMAIL YOU WANT TO SEND TO HERE" }],


### Organizations
If your API key has access to one organization, this script will by default choose the first returned Organization. 

If your API key has access to more than 1 organization, you will be prompted to select the ORG. Example:

    2024-12-05 14:50:06,932 - GetBSSID - INFO - Fetching organizations...
    2024-12-05 14:50:07,685 - GetBSSID - INFO - Organizations fetched successfully.

    Available Organizations:
    0: Blue Wave Therapy (ID: 123456)
    1: Quantum Dynamics Inc. (ID: 234567)
    2: Apex Legal Partners (ID: 345678)
    3: Orion Tech Solutions (ID: 456789)
    4: GreenLeaf Environmental, LLC (ID: 567890)
    5: NorthStar Brewing Co (ID: 987654321012345678)
    6: Vertex Auto Management (ID: 876543210987654321)
    7: Horizon Medical Logistics (ID: 123123123123123123)
    8: Stellar Legal Associates (ID: 234234234234234234)
    9: Zenith Facility Services (ID: 345345345345345345)
    Enter the number of the organization to proceed: 9
    2024-12-05 14:50:12,634 - GetBSSID - INFO - Getting network IDs for organization: Zenith Facility Services (ID: 345345345345345345)
    2024-12-05 14:50:13,196 - GetBSSID - INFO - Fetched networks successfully.

### Networks
The GetNetworkIDs function will show the networks that it is going to pull from. You will be prompted to select which networks to include in the BSSID output. Select option 1 to include all networks. Select option 2 to select specific networks to include, separated by a comma. For example, 0,2,4,6,8. Example:

    Available Networks:
    0: NY - Albany (ID: L_111111111111111111)
    1: CA - Los Angeles (ID: L_222222222222222222)
    2: TX - Austin (ID: L_333333333333333333)
    3: FL - Miami (ID: L_444444444444444444)
    4: CO - Denver (ID: L_555555555555555555)
    5: IL - Chicago - HQ (ID: L_666666666666666666)
    6: GA - Atlanta (ID: L_777777777777777777)
    7: WA - Seattle (ID: L_888888888888888888)
    8: OH - Cleveland (ID: L_999999999999999999)
    9: WI - Madison (ID: L_000000000000000000)
    10: NV - Las Vegas (ID: L_101010101010101010)
    11: AR - Little Rock - SG360 (ID: L_202020202020202020)
    12: WI - Green Bay - EcoClean (ID: L_303030303030303030)
    13: MI - Detroit - Hi-Tec (ID: L_404040404040404040)
    Options:
    1: Include all networks.
    2: Select specific networks by their indices (e.g., 0,2,4).
    3: Abort.
    Enter your choice (1, 2, or 3): 2
    Enter the indices of the networks to include (comma-separated): 0,2,4,6,8
    2024-12-05 14:50:22,659 - GetBSSID - INFO - Selected networks:
    {
        "L_111111111111111111": "NY - Albany",
        "L_333333333333333333": "TX - Austin",
        "L_555555555555555555": "CO - Denver",
        "L_777777777777777777": "GA - Atlanta",
        "L_999999999999999999": "OH - Cleveland"
    }


### Exclude Guest Networks
This script has an capability to exclude clients that connect to guest networks. Use the app_config file to edit this.


### Python Dependencies
**Use pip install -r requirements.txt command to download each Python package**:

Ensure you download the requirements.txt file, and then run pip install -r requirements.txt. Each required package will be downloaded. The requirements.txt file contains all the packages used by the script. 

Please note that a [virtual environment](https://docs.python.org/3/library/venv.html) will help isolate package dependencies, and ensure each package is found by the IDE.

Also, you may need to change your python interpreter to use the virtual environment with CTRL + SHIFT + P and search Python: Select Interpreter. Ensure the virtual environment is chosen. 

Finally, this script was built on python 3. 

### Improvements To Be Made
The Get Network Clients script was created by a Network Engineer by trade, and not a python developer. As a result, while this code functions, there is room for improvements. Items that may be useful for this script include:
- JSON files are created but not really required. They are there mostly to provide you with the raw data from the API request. Feel free to tweak and remove the json files from being used. 
- Update Mechanism: Implement a mechanism to check for updates or patches to dependencies, ensuring the script remains compatible with new versions of libraries.
- At Times, you will get a random 503 error from Meraki when the dashboard does not respond in time, or if they are having issues. The script provided has no mechanism to re-start itself, or notify you that is has stopped running. 
- It may be more reliable to utilize windows task scheduler or cron jobs instead of the built in while true loop for continued monitoring of new clients.

## Custom Logging
This script now also includes custom logging to track data historically. You must have the custom_logger.py to proceed without errors. You can add the file path to the file name if you want to store this in a specific location.This logging script will rotate automatically, and only store 3 backup files. 

### Reference Guides
- [Azure Communication Email client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python/)
- [Overview of Azure Communication Services email](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
- [Quickstart For Azure Communication Service](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/create-email-communication-resource?pivots=platform-azp)
- [Email domains and sender authentication for Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-domain-and-sender-authentication)
- [How to connect a verified email domain](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/connect-email-communication-resource?pivots=azure-portal)
- [Meraki Dashboard API Python Library](https://developer.cisco.com/meraki/api-v1/python/)
- [Get Network Clients - Meraki Dashboard API v1 - Cisco Meraki Developer Hub](https://developer.cisco.com/meraki/api-v1/get-network-clients/)
- [Meraki GitHub](https://github.com/meraki/dashboard-api-python/blob/main/README.md)
