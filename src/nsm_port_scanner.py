# THIS MODULE WILL BE FOR FULL BLOWN PORT SCANNING, IP BY IP FOR IP IN IPS


# UI IMPORTS
from rich.panel import Panel
from rich.live import Live



# ETC IMPORTS
import socket, time
from concurrent.futures import ThreadPoolExecutor



# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import File_Saver


# CONSTANTS
console = Variables.console





class Socket_Port_Scanner():
    """This class will be used to peform a full blown port scan off all 65,535 ports"""

    total       = 0
    total_ports = 0
    ip_port_map = {}





    @classmethod
    def _port_scanner(cls, ip, port, timeout, verbose=False):
        """This will peform port scan on said ip"""

        

        # COLORS
        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"


        try:
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                    s.settimeout(timeout)
                    result = s.connect_ex((ip,port))
                    both = (f"{ip}:{port}")

                    if result == 0:
                        

                        with Variables.LOCK:
                            console.print(f"[bold green][+] Active:[/bold green][yellow] {ip}:[/yellow]{port}")
                            
                            if ip not in cls.ip_port_map: cls.ip_port_map[ip] = {"ports": []}

                            cls.ip_port_map[ip]["port"].append(port); cls.total_ports += 1
                            Variables.panel_text = (f"[{c5}]IPs Scanning:[/{c5}] {cls.total}  -  [{c5}]Ports_Found:[/{c5}] {cls.total_ports}")
                            return True
                    

                    if verbose: console.print(f"[bold red][-] {both}")
                    return False

        except Exception as e: 
            if verbose: console.print(f"[bold red]Exception Error:[bold yellow] {e}")
            return False



    
    @classmethod
    def _threader_ports(cls, ip, max_threads):
        """This will spawn a thread for each port"""



        with ThreadPoolExecutor(max_workers=max_threads) as executor:

            for port in range(0,65536): executor.submit(cls._port_scanner, ip, port, 1)



    
    @classmethod
    def _threader_ip(cls, ips, max_threads):
        """This will spawn a thread for its own ip"""


        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"


        with ThreadPoolExecutor(max_workers=max_threads) as executor:

            for ip in ips:
                cls.total += 1
                with Variables.LOCK: Variables.panel_text = (f"[{c5}]IPs Scanning:[/{c5}] {cls.total}  -  [{c5}]Ports_Found:[/{c5}] {cls.total_ports}")
                console.print(f"[bold green][+] Threading:[yellow] {ip}")
                executor.submit(cls._threader_ports, ip, max_threads)


    

    @classmethod
    def main(cls):
        

        ips         = Variables.ips
        max_threads = Variables.max_threads


        ips = File_Saver.ips_sanitizer(ips=ips, verbose=True)
        time_total = time.time()

        
        p = "=" * 10
        console.print(f"[bold red]\n{p}  Mass Port Scanning  {p}\n")
        cls._threader_ip(ips=ips, max_threads=max_threads)
        File_Saver.push_scan_results(data=cls.ip_port_map, f_type="json")


        console.print(cls.ip_port_map); time_total = time.time() - cls.time_start

        c1 = "red"; c2 = "bold green"; c3 = "bold blue"; c4 = "bold yellow"

        stats = (
            f"[{c3}] [+] Total IPs Scanned:[{c4}] {len(ips)}"
            f"\n[{c3}] [+] Total Ports Found:[{c4}] {len(cls.total_ports)}"
            f"\n[{c3}] [+] Elapsed Time:[{c4}] {time_total}"
        )

        
        console.print(
            f"[{c1}]=========   Results   =========\n",
            stats,
            f"\n[{c1}]=================================",
        )



if __name__ == "__main__":


    Socket_Port_Scanner.main()