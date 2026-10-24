import re
from netmiko import ConnectHandler

Private_Key = r"C:/Users/LAB308_XX/Desktop/67070066_IPA/PrivateKey_IPA"

devices = [
    {
        "name": "R1-P",
        "device_type": "cisco_ios",
        "host": "172.31.15.4",
        "username": "admin",
        "use_keys": True,
        "key_file": Private_Key,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
    {
        "name": "R2-P",
        "device_type": "cisco_ios",
        "host": "172.31.15.5",
        "username": "admin",
        "use_keys": True,
        "key_file": Private_Key,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
]

ACTIVE_INTF_RE = re.compile(
    r"^(?P<interface>\S+)\s+"
    r"(?P<ip_address>\S+)\s+"
    r"\S+\s+\S+\s+"
    r"up\s+" 
    r"up\s*$",
    re.MULTILINE,
)

UPTIME_RE = re.compile(
    r"^(?P<hostname>\S+)\s+uptime is\s+(?P<uptime>.+)$",
    re.MULTILINE,
)

def get_active_interfaces(output: str):
    """Return a list of (interface, ip_address) tuples that are up/up."""
    return ACTIVE_INTF_RE.findall(output)

def get_uptime(output: str):
    """Return the uptime string parsed from `show version` output."""
    match = UPTIME_RE.search(output)
    return match.group("uptime") if match else "Unknown"

def main():
    for dev in devices:
        dev = dict(dev)
        dev_name = dev.pop("name")

        print(f"--- Connecting to {dev_name} ({dev['host']}) ---")
        try:
            net_connect = ConnectHandler(**dev)
            net_connect.enable()

            intf_output = net_connect.send_command("show ip interface brief")
            version_output = net_connect.send_command("show version")

            net_connect.disconnect()

            active_interfaces = get_active_interfaces(intf_output)
            uptime = get_uptime(version_output)

            print(f"\n{dev_name} - Uptime: {uptime}")
            if active_interfaces:
                print(f"{dev_name} - Active interfaces (status=up, protocol=up):")
                for intf, ip in active_interfaces:
                    print(f"    {intf:<25} {ip}")
            else:
                print(f"{dev_name} - No active interfaces found.")
            print(f"--- Completed {dev_name} ---\n")

        except Exception as e:
            print(f"Failed to check {dev_name}: {e}\n")

if __name__ == "__main__":
    main()