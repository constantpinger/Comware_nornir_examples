# ================================================================== #
# Asks all comware 5130 switches if
# they have a certificate on the flash
# Could be used to check for any file present
# ================================================================== #
from nornir import InitNornir
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

# sets the username/password for all devices in the nornir class instance
def set_u_p(username=None, password=None):
    for host_obj in nr.inventory.hosts.values():
        host_obj.username = username
        host_obj.password = password


def ComwareCheckCerts():  
    hostlist = nr.filter(typeName="HPE 5130-48G-PoE+-4SFP+(370W)EI")
    #hostlist = nr.filter(hostname="ca2st1")
    BadCertList = []
    CheckedHostCount = 0
    r = hostlist.run(
        task=netmiko_send_command,
        use_textfsm=False,
        command_string="dir")
    for host in hostlist.inventory.hosts:
        CheckedHostCount = CheckedHostCount + 1
        if host not in r.failed_hosts:  # only take action if switch responded
            if ('currentCARoot.crt' not in r[host][0].result) or ('AddTrustExternalCARoot.crt' not in r[host][0].result):
                BadCertList.append(host)
    return [BadCertList,CheckedHostCount]

username=input("username?")
password=getpass()
set_u_p(username , password)   #TODO fix if u/p wrong
BadCertList, CheckedHostCount = ComwareCheckCerts()
print(CheckedHostCount + " hosts checked")
print("No file found on the following hosts: " + BadCertList)
