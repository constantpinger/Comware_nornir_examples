# ================================================================== #
# Ask all comware 5130 switches in a group their uptime
# then builds a message to be sent to Slack/email/screen
# ================================================================== #
# TODO add more switches type

from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks.networking import netmiko_send_command
from getpass import getpass

nr = InitNornir(
    core={"num_workers": 1000},
    inventory={
        "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
        "options": {
            "host_file": "hosts.yaml",
            "group_file": "groups.yaml",
        },
    }
)

def set_u_p(username=None, password=None):
    for host_obj in nr.inventory.hosts.values():
        host_obj.username = username
        host_obj.password = password

def GetComwareDCUptime():
    #  hostlist = nr.filter(F(hostname="slb1st1") | F(hostname="slb1st2"))    OR
    #  hostlist = nr.filter(F(hostname="slb1st1") & F(hostname="slb1st2"))    AND
    #  hostlist = nr.filter(F(groups__contains="edge5130") & ~F(hostname="slb1st2"))    NEGATE
    hostlist = nr.filter(F(groups__contains="DCswtich")).filter(platform="hp_comware")
    #hostlist = nr.filter(hostname="slb1st2")
    result = []
    r = hostlist.run(
        task=netmiko_send_command,
        use_textfsm=True,
        command_string="display version | i uptime" )
    for host in hostlist.inventory.hosts:
        if (host not in r.failed_hosts)   :  # only take action if switch responded
            stripped_string = (r[host][0].result).partition('uptime is')[2]
            stripped_string2 = stripped_string.partition('day')[0]
            stripped_string_days = stripped_string2.partition(',')[2]
            stripped_string_weeks = stripped_string2.partition('week')[0]
            total_days = int(stripped_string_weeks)*7 + int(stripped_string_days)
            result.append([host,total_days])
    return result

username=input("username?")
password=getpass()
set_u_p(username , password)  

msg1=""
fetch = GetComwareDCUptime()
if len(fetch) > 0:    # check if there are an entries to print
    for i in fetch:
        if i[1] > 365:   #if up for more than one year
            msg1 = msg1 + '\n' + i[0] + '   ' + str(i[1]) + ' days  ** MORE THAN 1 YEAR  **'
        else:
            msg1 = msg1 + '\n' + i[0] + '   ' + str(i[1]) + ' days'
else:
    print("There was a problem fetching data")
print(msg1)
