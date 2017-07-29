# update-switchports-policy

=== PREREQUISITES ===
Run in Python 2

Install requests library, via macOS terminal:
sudo pip install requests

=== DESCRIPTION ===
The find_ports.py script finds all MS switchports that match the input search parameter, searching either by clients from a file listing MAC addresses (one per line), a specific tag in Dashboard currently applied to ports, or the specific access policy currently configured. This script does not change configuration; its counterpart script update_ports.py does change the access policy.

=== USAGE ===
python find_ports.py -k <api_key> -o <org_id> -s <search_parameter> [-t <time>]
The -s parameter will be either a local file of MAC addresses (one per line), a currently configured port tag in Dashboard, or the currently configured access policy (number of policy slot) on the Switch > Access policy page. Option -t, if using input list of MACs, to only search for clients that were last seen within t minutes, default is 15.

python update_ports.py -k <api_key> -o <org_id> -s <search_parameter> [-t <time>] -p <policy>
The -s parameter will be either a local file of MAC addresses (one per line), a currently configured port tag in Dashboard, or the currently configured access policy (number of policy slot) on the Switch > Access policy page. Option -t, if using input list of MACs, to only search for clients that were last seen within t minutes, default is 15. -p specifies the slot # of the new access policy to configure on matching ports.