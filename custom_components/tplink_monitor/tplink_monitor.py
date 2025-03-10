import requests
import re
import logging
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

# TP-Link Status Mappings
TPstate = {0: 'Disabled', 1: 'Enabled'}
TPlinkStatus = {
    0: "Link Down", 2: "10M Half", 3: "10M Full",
    5: "100M Full", 6: "1000M Full"
}

def fetch_port_statistics(ip, username, password):
    """Fetch and parse port statistics from TP-Link switch web interface."""
    session = requests.Session()
    data = {"logon": "Login", "username": username, "password": password}

    # Login to the switch
    response = session.post(f"http://{ip}/logon.cgi", data=data)
    if response.status_code != 200:
        _LOGGER.error("Login failed! Check username and password.")
        return None

    # Get port statistics page
    response = session.get(f"http://{ip}/PortStatisticsRpm.htm")
    if response.status_code != 200:
        _LOGGER.error("Failed to fetch PortStatisticsRpm.htm")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract JavaScript block containing port statistics
    script_text = soup.find("script")
    if not script_text:
        _LOGGER.error("No script block found in the HTML!")
        return None
    script_text = script_text.string

    # Extract 'pkts' array
    pkts_match = re.search(r"pkts:\[(.*?)\]", script_text)
    if not pkts_match:
        _LOGGER.error("No packet data found!")
        return None
    pkts_values = list(map(int, pkts_match.group(1).split(",")))

    # Extract Port Status (Enabled/Disabled)
    state_match = re.search(r"state:\[(.*?)\]", script_text)
    state_values = list(map(int, state_match.group(1).split(",")))

    # Extract Link Status (Speed or Link Down)
    link_match = re.search(r"link_status:\[(.*?)\]", script_text)
    link_values = list(map(int, link_match.group(1).split(",")))

    # Extract Number of Ports
    max_port_num_match = re.search(r"var max_port_num = (\d+);", script_text)
    if not max_port_num_match:
        _LOGGER.error("Could not find max_port_num!")
        return None
    max_port_num = int(max_port_num_match.group(1))

    # Organize Data by Port
    port_stats = {}
    for i in range(max_port_num):
        port_stats[i + 1] = {
            "state": TPstate.get(state_values[i], "Unknown"),
            "link_status": TPlinkStatus.get(link_values[i], "Unknown"),
            "tx_good": pkts_values[i * 4], 
            "tx_bad": pkts_values[i * 4 + 1], 
            "rx_good": pkts_values[i * 4 + 2], 
            "rx_bad": pkts_values[i * 4 + 3]
        }
    
    return port_stats
