#!/usr/bin/python2

'''
=== PREREQUISITES ===
Run in Python 2

Install requests library, via macOS terminal:
sudo pip install requests

dash_vars.py has these two lines, with the API key from your Dashboard profile (upper-right email login > API access), and organization ID to call (https://dashboard.meraki.com/api/v0/organizations); separated into different file for security.
api_key = '[API_KEY]'
org_id = '[ORG_ID]'

Usage:
python bps.py

=== DESCRIPTION ===
Finds all MS switchports that match a specified port tag, and changes the access policy for those ports.

'''

import getopt
import json
import requests
import sys
from datetime import datetime

def printusertext(p_message):
    # prints a line of text that is meant for the user to read
    print('@ %s' % p_message)

def printhelp():
    # prints help text
    printusertext('This script finds all MS switchports that match a specified port tag,')
    printusertext('and changes the access policy for those ports.')
    printusertext('')
    printusertext('Usage:')
    printusertext('python bps.py -k <key> -o <org> -p <policy> [-t <tag>]')
    printusertext('')
    printusertext('The option -p will be the number (1 or 2) for the access policy.')
    printusertext('If option -t is not defined, the "cart" tag will be used by default.')
    printusertext('')
    printusertext('Use double quotes ("") in Windows to pass arguments containing spaces.')

def list_networks(api_key, org_id):
    url = 'https://dashboard.meraki.com/api/v0/organizations/{}/networks'.format(org_id)
    try:
        response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
        if response.status_code == 400:
            print response.text
        else:
            return json.loads(response.text)
    except Exception, e:
        print ("Error: {}".format(str(e)))

def get_inventory(api_key, org_id):
    url = 'https://dashboard.meraki.com/api/v0/organizations/{}/inventory'.format(org_id)
    try:
        response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
        if response.status_code == 400:
            print response.text
        else:
            return json.loads(response.text)
    except Exception, e:
        print ("Error: {}".format(str(e)))

def list_switch_ports(api_key, serial):
        url = 'https://dashboard.meraki.com/api/v0/devices/{}/switchPorts'.format(serial)
        try:
            response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
            if response.status_code == 400:
                print response.text
            else:
                return json.loads(response.text)
        except Exception, e:
            print ("Error: {}".format(str(e)))

def get_port_details(api_key, serial, number):
    url = 'https://dashboard.meraki.com/api/v0/devices/{}/switchPorts/{}'.format(serial, number)
    try:
        response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
        if response.status_code == 400:
            print response.text
        else:
            return json.loads(response.text)
    except Exception, e:
        print ("Error: {}".format(str(e)))

def update_switch_port(api_key, serial, number, data):
    url = 'https://dashboard.meraki.com/api/v0/devices/{}/switchPorts/{}'.format(serial, number)
    try:
        response = requests.put(url=url, data=data, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
        if response.status_code == 400:
            print response.text
        else:
            return json.loads(response.text)
    except Exception, e:
        print ("Error: {}".format(str(e)))

def list_clients(api_key, serial, timestamp=86400): # timestamp in seconds
    url = 'https://dashboard.meraki.com/api/v0/devices/{}/clients?timespan={}'.format(serial, timestamp)
    try:
        response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
        return json.loads(response.text)
    except Exception,e:
        print ("Error: {}".format(str(e)))


def main(argv):
    # Set default values for command line arguments
    API_KEY = 'null'
    ORG_ID = 'null'
    ARG_POLICY = 'null'
    ARG_TAG = 'cart'

    # Get command line arguments
    try:
        opts, args = getopt.getopt(argv, 'hk:o:p:t:')
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt == '-k':
            API_KEY = arg
        elif opt == '-o':
            ORG_ID = arg
        elif opt == '-p':
            ARG_POLICY = arg
        elif opt == '-t':
            ARG_TAG = arg

    # Check if all parameters are required parameters have been given
    if API_KEY == 'null' or ORG_ID == 'null': # or ARG_POLICY == 'null':
        printhelp()
        sys.exit(2)

    # Input list of wired MAC addresses to check
    file = open('wired_macs.txt')
    macs = file.read().split('\n')
    macs = [mac.upper() for mac in macs]
    print('Comparing against list of %d wired MAC addresses, first and last in list are %s and %s, respectively.\n' % (len(macs), macs[0], macs[-1]))

    # Find all MS networks
    session = requests.session()
    inventory = get_inventory(API_KEY, ORG_ID)
    switches = [device for device in inventory if device['model'][:2] in ('MS') and device['networkId'] is not None]
    switch_networks = []
    for switch in switches:
        if switch['networkId'] not in switch_networks:
            switch_networks.append(switch['networkId'])
    print('Found a total of %d switches configured across %d networks in this organization.\n' % (len(switches), len(switch_networks)))

    '''
    # Find all ports matching user-specified tag
    tagged_switchports = {}
    count_switchports = 0
    for switch in switches:
        ports = list_switch_ports(API_KEY, switch['serial'])
        tagged_ports = [port for port in ports if port['tags'] != None and ARG_TAG in port['tags']]
        if len(tagged_ports) > 0:
            count_switchports += len(tagged_ports)
            tagged_switchports[switch['serial']] = tagged_ports
    print('Found a total of %d ports tagged "%s".\n' % (count_switchports, ARG_TAG))
    '''

    # Find all clients per switch that match list
    for switch in switches:
        # Find clients that were connected in last 15 minutes
        clients = list_clients(API_KEY, switch['serial'], 60*15)
        print('Found %d total clients connected behind switch %s' % (len(clients), switch['serial']))
        
        # Helper variable that is a list of all MAC addresses, in upper-case to compare with master input list
        clients_macs = [client['mac'].upper() for client in clients]

        # Helper variable that is a dict of MAC address keys to client information values
        matching_dict = {}
        for (mac, client) in zip(clients_macs, clients):
            matching_dict[mac] = client

        # Find matches between clients on switch to master input list
        matches = set(clients_macs).intersection(macs)

        # Find ports of matched clients
        if len(matches) > 0:
            matched_ports = {}
            for match in matches:
                port = matching_dict[match]['switchport']
                if port not in matched_ports:
                    matched_ports[port] = 1
                else:
                    matched_ports[port] += 1
            print('There are %d matched MAC addresses on this switch' % (len(matches)))
            for port in matched_ports.keys():
                print('On port %s, found %d matches' % (port, matched_ports[port]))
            print('\n')
    
    '''
    # Change access policy for all tagged ports
    for switch in tagged_switchports.keys():
        count_already_set = 0
        count_newly_set = 0
        for port in tagged_switchports[switch]:
            if port['accessPolicyNumber'] == int(ARG_POLICY):
                count_already_set += 1
                continue
            else:
                count_newly_set += 1
                port['accessPolicyNumber'] = int(ARG_POLICY)
                update_switch_port(API_KEY, switch, port['number'], json.dumps(port))
        print('Updated switch %s on %d ports (%d ports already configured for policy %s)\n' % (switch, count_newly_set, count_already_set, ARG_POLICY))
    print('Script complete!')
    '''

if __name__ == '__main__':
    startTime = datetime.now()
    main(sys.argv[1:])
    print('Total run time: ' + str(datetime.now() - startTime))
