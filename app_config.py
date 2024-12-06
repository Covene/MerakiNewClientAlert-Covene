"""Update the sender address for email notifications and the recipient address below."""

SenderAddress = 'DoNotReply@domain.com'
SentToAddress = 'UpdateEmailAddressHere@domain.com'


# Update the following variable with the name of the wireless network you want to exclude from alerting on.
#This can be useful if you want to exclude wireless guest networks.
WirelessGuestNetworkToExclude = ['WirelessGuestNetwork1', 'WirelessGuestNetwork2', 'GuestNetwork3']


#How long to pause between checking new clients. This is in seconds.
Sleeptime = 300



"""Environment Configuration:

Please ensure the following environment variables are configured: 

Azure_Communication_Resource
API_Key

"""