import os
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

Private_Key = r"C:/Users/LAB308_XX/Desktop/67070066_IPA/PrivateKey_IPA"

devices = [
    {
        "name": "S1-P",
        "template": "switch.j2",
        "device_type": "cisco_ios",
        "host": "172.31.15.3",
        "username": "admin",
        "use_keys": True,
        "key_file": Private_Key,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
    {
        "name": "R1-P",
        "template": "router.j2",
        "device_type": "cisco_ios",
        "host": "172.31.15.4",
        "username": "admin",
        "use_keys": True,
        "key_file": Private_Key,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
    {
        "name": "R2-P",
        "template": "router.j2",
        "device_type": "cisco_ios",
        "host": "172.31.15.5",
        "username": "admin",
        "use_keys": True,
        "key_file": Private_Key,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
]

common_vty_acl = {
    "acl_number": 10,
    "acl_permit_networks": [
        {"network": "172.31.15.0", "wildcard": "0.0.0.15"},
        {"network": "10.30.6.0", "wildcard": "0.0.0.255"},
    ],
}

config_vars = {
    "S1-P": {
        "vlan_id": 101,
        "vlan_name": "Control-Data",
        "access_interfaces": ["GigabitEthernet0/1", "GigabitEthernet1/1"],
        **common_vty_acl,
    },
    "R1-P": {
        "mgmt_ospf_process": 10,
        "mgmt_network": "172.31.15.0",
        "mgmt_wildcard": "0.0.0.15",
        "mgmt_area": 15,
        "cd_ospf_process": 20,
        "cd_networks": [
            {"network": "10.15.1.0", "wildcard": "0.0.0.3"},
            {"network": "10.15.1.8", "wildcard": "0.0.0.3"},
        ],
        "cd_area": 15,
        "default_information_originate": False,
        "nat": None,
        "dns": None,
        **common_vty_acl,
    },
    "R2-P": {
        "mgmt_ospf_process": 10,
        "mgmt_network": "172.31.15.0",
        "mgmt_wildcard": "0.0.0.15",
        "mgmt_area": 15,
        "cd_ospf_process": 20,
        "cd_networks": [
            {"network": "10.15.1.4", "wildcard": "0.0.0.3"},
            {"network": "10.15.1.8", "wildcard": "0.0.0.3"},
        ],
        "cd_area": 15,
        "default_information_originate": True,
        "nat": {
            "inside_interfaces": ["GigabitEthernet0/1", "GigabitEthernet0/2"],
            "outside_interface": "GigabitEthernet0/3",
            "acl_number": 1,
            "network": "10.15.1.0",
            "wildcard": "0.0.0.255",
        },
        "dns": {
            "vrf": "control-data",
            "servers": ["192.168.42.1", "8.8.8.8", "1.1.1.1"],
        },
        **common_vty_acl,
    },
}

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True,
)

def render_commands(device_name: str, template_name: str) -> list:
    """Render a device's Jinja2 template"""
    template = jinja_env.get_template(template_name)
    rendered = template.render(**config_vars[device_name])
    return [line for line in rendered.splitlines() if line.strip()]


def main():
    for dev in devices:
        dev = dict(dev)
        dev_name = dev.pop("name")
        template_name = dev.pop("template")

        commands = render_commands(dev_name, template_name)

        print(f"--- Connecting to {dev_name} ({dev['host']}) ---")
        try:
            net_connect = ConnectHandler(**dev)
            net_connect.enable()

            print(f"Applying configuration to {dev_name}...")
            output = net_connect.send_config_set(commands)
            print(output)

            net_connect.save_config()
            net_connect.disconnect()
            print(f"--- Completed {dev_name} successfully ---\n")

        except Exception as e:
            print(f"Failed to configure {dev_name}: {e}\n")

if __name__ == "__main__":
    main()
