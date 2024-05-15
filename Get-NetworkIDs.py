import meraki

#Implement your own API key here. Use API_Key=os.environ["MERAKI_DASHBOARD_API_KEY"] to use an envionment variable. Replace the quoted text with your environment variable name. 
API_Key='UPDATE this to either an environment variable, or your api key.'

#Edit the org ID with the company you want to pull the networks for.
org_id = 'UPDATE this to either an environment variable, or your org ID value'

dashboard = meraki.DashboardAPI(API_Key)
response = dashboard.organizations.getOrganizationNetworks(org_id)

print(response)
