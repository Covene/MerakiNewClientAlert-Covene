import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, timezone
import pandas as pd
import json

# Import the functions from webhook_alert.py
from webhook_alert import get_network_ids, get_new_clients, send_to_webhook

class TestMerakiScript(unittest.TestCase):

    @patch('webhook_alert.dashboard')
    def test_get_network_ids(self, mock_dashboard):
        mock_dashboard.organizations.getOrganizationNetworks.return_value = [
            {'id': '123', 'timeZone': 'America/Los_Angeles', 'name': 'Network 1'},
            {'id': '456', 'timeZone': 'America/New_York', 'name': 'Network 2'}
        ]
        org_id = 'test_org_id'
        networks = get_network_ids(mock_dashboard, org_id)
        expected = [
            {'id': '123', 'timeZone': 'America/Los_Angeles', 'name': 'Network 1'},
            {'id': '456', 'timeZone': 'America/New_York', 'name': 'Network 2'}
        ]
        self.assertEqual(networks, expected)

    @patch('webhook_alert.dashboard')
    def test_get_new_clients(self, mock_dashboard):
        mock_dashboard.networks.getNetworkClients.return_value = [
            {'mac': '00:11:22:33:44:55', 'description': 'Client 1', 'ip': '192.168.1.1',
             'recentDeviceConnection': 'WiFi', 'recentDeviceName': 'AP1', 'ssid': 'SSID1',
             'switchport': '1', 'firstSeen': datetime(2024, 7, 15, 15, 0, tzinfo=timezone.utc).timestamp()},
            {'mac': '66:77:88:99:AA:BB', 'description': 'Client 2', 'ip': '192.168.1.2',
             'recentDeviceConnection': 'Ethernet', 'recentDeviceName': 'Switch1', 'ssid': 'SSID2',
             'switchport': '2', 'firstSeen': datetime(2024, 7, 14, 9, 0, tzinfo=timezone.utc).timestamp()}
        ]
        network_id = 'test_network_id'
        reference_time = datetime(2024, 7, 15, 0, 0, tzinfo=timezone.utc).timestamp()  # fixed reference time for consistency
        clients = get_new_clients(mock_dashboard, network_id, reference_time)
        expected = [
            {'mac': '00:11:22:33:44:55', 'description': 'Client 1', 'ip': '192.168.1.1',
             'connectionType': 'WiFi', 'connectedTo': 'AP1', 'ssid': 'SSID1', 'switchport': '1',
             'firstSeen': '2024-07-15 15:00:00'}
        ]
        self.assertEqual(clients, expected)

    def test_send_to_webhook(self):
        webhook_url = 'https://example.com/webhook'
        data = [{'mac': '00:11:22:33:44:55', 'description': 'Client 1', 'ip': '192.168.1.1',
                 'connectionType': 'WiFi', 'connectedTo': 'AP1', 'ssid': 'SSID1', 'switchport': '1',
                 'firstSeen': '2024-07-15 10:00:00'}]
        expected_json_data = json.dumps(data, indent=4)
        json_data = send_to_webhook(webhook_url, data)
        self.assertEqual(json_data, expected_json_data)

    def test_dataframe_conversion(self):
        data = [
            {'mac': '00:11:22:33:44:55', 'description': 'Client 1', 'ip': '192.168.1.1',
             'connectionType': 'WiFi', 'connectedTo': 'AP1', 'ssid': 'SSID1', 'switchport': '1',
             'firstSeen': '2024-07-15 10:00:00'},
            {'mac': '66:77:88:99:AA:BB', 'description': 'Client 2', 'ip': '192.168.1.2',
             'connectionType': 'Ethernet', 'connectedTo': 'Switch1', 'ssid': 'SSID2', 'switchport': '2',
             'firstSeen': '2024-07-14 09:00:00'}
        ]
        df = pd.DataFrame(data)
        json_data = df.to_json(orient='records')
        expected_json_data = json.dumps(data)
        self.assertEqual(json.loads(json_data), json.loads(expected_json_data))

if __name__ == '__main__':
    unittest.main()
