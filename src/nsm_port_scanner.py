# THIS MODULE WILL BE FOR FULL BLOWN PORT SCANNING, IP BY IP FOR IP IN IPS
# if this breaks its not my fault, the original spawned 65k threads per IP like a psychopath


# UI IMPORTS
from rich.panel import Panel
from rich.live import Live



# ETC IMPORTS
import socket, time, threading
from concurrent.futures import ThreadPoolExecutor



# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import File_Saver


# CONSTANTS
console = Variables.console




class Socket_Port_Scanner():
    """This class will be used to peform a full blown port scan off all 65,535 ports"""


    total_ips_scanned = 0
    total_ips_all     = 0
    total_ports_all   = 0
    total_ports_open  = 0
    ports_scanned     = 0
    ip_port_map       = {}
    time_start        = 0


    @classmethod
    def _port_scanner(cls, ip, port, timeout, verbose=False):
        """This will peform port scan on said ip"""

        cls.ports_scanned += 1


        if cls.ports_scanned % 100 == 0:
            with Variables.LOCK:
                Variables.panel_text = (f"[yellow]IPs:[/yellow] {cls.total_ips_scanned}/{cls.total_ips_all}  -  [yellow]Ports Scanned:[/yellow] {cls.ports_scanned}  -  [yellow]Open:[/yellow] {cls.total_ports_open}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))

                if result == 0:
                    with Variables.LOCK:
                        console.print(f"[bold green][+] Active:[/bold green][yellow] {ip}:[/yellow]{port}")

                        if ip not in cls.ip_port_map: cls.ip_port_map[ip] = {"ports": []}

                        cls.ip_port_map[ip]["ports"].append(port)
                        cls.total_ports_open += 1

                    return True

                return False

        except Exception as e:
            if verbose: console.print(f"[bold red]Exception Error:[bold yellow] {e}")
            return False




    @classmethod
    def _scan_ip(cls, ip, timeout):
        """Scan all ports on a single IP using a thread pool instead of 65k raw threads (we're not animals)"""

        with Variables.LOCK:
            cls.total_ips_scanned += 1

        with ThreadPoolExecutor(max_workers=Variables.max_threads) as executor:
            futures = []
            for port in range(1, 65536):
                futures.append(executor.submit(cls._port_scanner, ip, port, timeout))
            for future in futures:
                future.result()

        console.print(f"[bold red][+] Nutted:[yellow] {ip}")


    @classmethod
    def _threader_ips(cls, ips, timeout=1):
        """This will iterate through IPs and scan each one"""

        for ip in ips:
            if not ip: continue

            console.print(f"\n[bold green][+] Scanning:[yellow] {ip}")
            cls._scan_ip(ip=ip, timeout=timeout)




    @classmethod
    def main(cls):


        ips         = Variables.ips
        timeout     = Variables.timeout
        max_threads = Variables.max_threads


        ips = File_Saver.ips_sanitizer(ips=ips, verbose=True)
        cls.total_ips_all = len(ips)
        cls.time_start = time.time()


        p = "=" * 10
        console.print(f"[bold red]\n{p}  Mass Port Scanning  {p}\n")
        cls._threader_ips(ips=ips, timeout=timeout)
        File_Saver.push_scan_results(data=cls.ip_port_map, f_type="json")


        time_total = time.time() - cls.time_start

        c1 = "red"; c2 = "bold green"; c3 = "bold blue"; c4 = "bold yellow"

        stats = (
            f"[{c3}] [+] Total IPs Scanned:[{c4}] {len(ips)}"
            f"\n[{c3}] [+] Total Ports Found:[{c4}] {cls.total_ports_open}"
            f"\n[{c3}] [+] Elapsed Time:[{c4}] {time_total}"
        )


        console.print(
            f"[{c1}]=========   Results   =========\n",
            stats,
            f"\n[{c1}]=================================",
        )



if __name__ == "__main__":


    Socket_Port_Scanner.main()
