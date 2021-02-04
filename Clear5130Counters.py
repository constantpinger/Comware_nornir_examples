
# ================================================================== #
# clear interface counters from all 5130
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
def set_u_p(username=None, password=None):
    for host_obj in nr.inventory.hosts.values():
        host_obj.username = username
        host_obj.password = password

def Clear5130InterfaceCounters():
    procurve_sys = nr.filter(typeName="HPE 5130-48G-PoE+-4SFP+(370W)EI")
    #procurve_sys = nr.filter(hostname="ac1st1")
    r = procurve_sys.run(
        task=netmiko_send_command,
        use_textfsm=False,
        command_string="reset count interface " )

username=input("username?")
password=getpass()
set_u_p(username , password)   #TODO fix if u/p wrong

Clear5130InterfaceCounters()
print("All 5130 Interface counters cleared ")
