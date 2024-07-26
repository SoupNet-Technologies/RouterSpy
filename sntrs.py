import tkinter as tk
from tkinter import ttk
import subprocess
import socket
import platform
import re

class RouterSpyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SNTRS / RouterSpy")
        self.root.geometry("1000x600")

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Network Configuration Data")
        self.label.pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Property", "Value"), show="headings")
        self.tree.heading("Property", text="Property")
        self.tree.heading("Value", text="Value")
        self.tree.column("Property", width=300, stretch=False)
        self.tree.column("Value", width=680)
        self.tree.pack(fill="both", expand=True, pady=5)

        self.scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(pady=5)

    def refresh_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        network_data = self.get_network_data()
        for key, value in network_data.items():
            self.tree.insert("", "end", values=(key, value))

    def get_network_data(self):
        data = {}
        data['Hostname'] = socket.gethostname()
        data['IP Address'] = self.get_ip_address()
        data['Subnet Mask'] = self.get_subnet_mask()
        data['Default Gateway'] = self.get_default_gateway()
        data['DNS Servers'] = self.get_dns_servers()
        data['ISP'] = self.get_isp_info()
        data['MAC Address'] = self.get_mac_address()
        data['DHCP Enabled'] = self.get_dhcp_status()
        data['OS Type'] = platform.system()
        data['OS Version'] = platform.version()
        data['Network Interfaces'] = self.get_network_interfaces()

        return data

    def get_ip_address(self):
        try:
            if platform.system() == "Windows":
                return socket.gethostbyname(socket.gethostname())
            elif platform.system() == "Darwin":
                output = subprocess.check_output("ipconfig getifaddr en0", shell=True).decode().strip()
                return output
            elif platform.system() == "Linux":
                output = subprocess.check_output("hostname -I", shell=True).decode().strip()
                return output.split()[0]
        except Exception as e:
            return str(e)

    def get_subnet_mask(self):
        try:
            if platform.system() == "Windows":
                return self.run_ipconfig_command('Subnet Mask')
            elif platform.system() == "Darwin":
                output = subprocess.check_output("ifconfig en0", shell=True).decode()
                mask = re.search(r'netmask (\w+)', output).group(1)
                return self.convert_netmask(mask)
            elif platform.system() == "Linux":
                output = subprocess.check_output("ifconfig", shell=True).decode()
                mask = re.search(r'Mask:([\d\.]+)', output).group(1)
                return mask
        except Exception as e:
            return str(e)

    def convert_netmask(self, hex_mask):
        hex_mask = hex_mask[2:]
        if len(hex_mask) != 8:
            return "Invalid netmask"
        mask = []
        for i in range(0, 8, 2):
            mask.append(str(int(hex_mask[i:i+2], 16)))
        return '.'.join(mask)

    def get_default_gateway(self):
        try:
            if platform.system() == "Windows":
                return self.run_ipconfig_command('Default Gateway')
            elif platform.system() == "Darwin":
                output = subprocess.check_output("netstat -nr | grep default", shell=True).decode()
                gateway = output.split()[1]
                return gateway
            elif platform.system() == "Linux":
                output = subprocess.check_output("ip r | grep default", shell=True).decode()
                gateway = output.split()[2]
                return gateway
        except Exception as e:
            return str(e)

    def get_dns_servers(self):
        try:
            if platform.system() == "Windows":
                return self.run_ipconfig_command('DNS Servers')
            elif platform.system() == "Darwin" or platform.system() == "Linux":
                output = subprocess.check_output("cat /etc/resolv.conf", shell=True).decode()
                dns_servers = re.findall(r'nameserver\s+([\d\.]+)', output)
                return ", ".join(dns_servers)
        except Exception as e:
            return str(e)

    def get_mac_address(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("getmac", shell=True).decode()
                mac = re.search(r'([A-F0-9-]{17})', output).group(1)
                return mac
            elif platform.system() == "Darwin" or platform.system() == "Linux":
                output = subprocess.check_output("ifconfig", shell=True).decode()
                mac = re.search(r'ether ([\w:]+)', output).group(1)
                return mac
        except Exception as e:
            return str(e)

    def get_dhcp_status(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True).decode()
                return "Yes" if "DHCP Enabled. . . . . . . . . . . : Yes" in output else "No"
            elif platform.system() == "Darwin":
                output = subprocess.check_output("ipconfig getpacket en0", shell=True).decode()
                return "Yes" if "yiaddr" in output else "No"
            elif platform.system() == "Linux":
                output = subprocess.check_output("nmcli dev show", shell=True).decode()
                return "Yes" if "DHCP4" in output else "No"
        except Exception as e:
            return str(e)

    def get_isp_info(self):
        try:
            output = subprocess.check_output("nslookup myip.opendns.com resolver1.opendns.com", shell=True).decode()
            ip_match = re.search(r'Address: (\d+\.\d+\.\d+\.\d+)', output)
            if ip_match:
                ip = ip_match.group(1)
                return f"Public IP: {ip}"
        except Exception as e:
            return str(e)

    def get_network_interfaces(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True).decode()
                interfaces = re.findall(r'Adapter (.*):', output)
            elif platform.system() == "Darwin" or platform.system() == "Linux":
                output = subprocess.check_output("ifconfig", shell=True).decode()
                interfaces = re.findall(r'^(\w+): flags', output, re.MULTILINE)
            return ", ".join(interfaces)
        except Exception as e:
            return str(e)

    def run_ipconfig_command(self, keyword):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True).decode()
                matches = re.findall(rf'{keyword}.*?:\s*([\d\.]+)', output)
                return ", ".join(matches)
            else:
                return "Command not supported on this OS"
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    root = tk.Tk()
    app = RouterSpyApp(root)
    root.mainloop()
