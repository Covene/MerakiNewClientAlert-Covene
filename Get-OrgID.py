import meraki
import json

#Implement your own API key here. Use API_Key=os.environ["MERAKI_DASHBOARD_API_KEY"] to use an envionment variable.
API_Key='UPDATE this to either an environment variable, or your api key.'



dashboard = meraki.DashboardAPI(API_Key)
response = dashboard.organizations.getOrganizations()

print(response)
with open('ORGresponse.json', 'w') as f:
    
    json.dump(response, f, indent=4)