# THIS MODULE WILL BE FOR FULL BLOWN PORT SCANNING, IP BY IP FOR IP IN IPS


# UI IMPORTS
from rich.panel import Panel
from rich.live import Live



# ETC IMPORTS
import socket, time, asyncio
from concurrent.futures import ThreadPoolExecutor



# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import File_Saver


# CONSTANTS
console = Variables.console






class Async_Port_Scanner():
    """Async port scanner - much faster than threaded version"""

    total          = 0
    total_ports    = 0
    ports_scanned  = 0
    ip_port_map    = {}
    semaphore      = None


    @classmethod
    async def _scan_port(cls, ip, port, timeout):
        """Async port scan for single port"""

        cls.ports_scanned += 1

        # Update panel every 100 ports scanned
        if cls.ports_scanned % 100 == 0:
            with Variables.LOCK:
                Variables.panel_text = (f"[yellow]IPs:[/yellow] {cls.total}  -  [yellow]Ports Scanned:[/yellow] {cls.ports_scanned}  -  [yellow]Open:[/yellow] {cls.total_ports}")

        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
            writer.close()
            await writer.wait_closed()

            with Variables.LOCK:
                console.print(f"[bold green][+] Active:[/bold green][yellow] {ip}:[/yellow]{port}")

                if ip not in cls.ip_port_map: cls.ip_port_map[ip] = {"ports": []}

                cls.ip_port_map[ip]["ports"].append(port)
                cls.total_ports += 1

            return True

        except:
            return False


    @classmethod
    async def _scan_ip(cls, ip, ports, timeout, max_concurrent):
        """Scan all ports for one IP in batches"""

        # Process in chunks to avoid memory issues but keep speed
        chunk_size = 10000

        for i in range(0, len(ports), chunk_size):
            chunk = ports[i:i + chunk_size]
            cls.semaphore = asyncio.Semaphore(max_concurrent)

            async def scan_with_sem(port):
                async with cls.semaphore:
                    return await cls._scan_port(ip, port, timeout)

            tasks = [scan_with_sem(port) for port in chunk]
            await asyncio.gather(*tasks, return_exceptions=True)


    @classmethod
    async def _scan_all(cls, ips, ports, timeout, max_concurrent):
        """Scan all IPs concurrently"""

        c5 = "yellow"

        # Scan all IPs concurrently instead of one at a time
        async def scan_single_ip(ip):
            cls.total += 1
            console.print(f"[bold green][+] Scanning:[yellow] {ip}")
            await cls._scan_ip(ip, ports, timeout, max_concurrent)

        tasks = [scan_single_ip(ip) for ip in ips]
        await asyncio.gather(*tasks, return_exceptions=True)


    @classmethod
    def main(cls):
        """Main entry point"""

        ips         = Variables.ips
        timeout     = Variables.timeout
        max_threads = Variables.max_threads

        ips = File_Saver.ips_sanitizer(ips=ips, verbose=True)
        ports = range(0, 65536)
        time_total = time.time()

        p = "=" * 10
        console.print(f"[bold red]\n{p}  Async Port Scanning  {p}\n")

        asyncio.run(cls._scan_all(ips, ports, timeout, max_threads))

        File_Saver.push_scan_results(data=cls.ip_port_map, f_type="json")

        time_total = time.time() - time_total

        c1 = "red"; c2 = "bold green"; c3 = "bold blue"; c4 = "bold yellow"

        stats = (
            f"[{c3}] [+] Total IPs Scanned:[{c4}] {len(ips)}"
            f"\n[{c3}] [+] Total Ports Found:[{c4}] {cls.total_ports}"
            f"\n[{c3}] [+] Elapsed Time:[{c4}] {time_total}"
        )

        console.print(
            f"[{c1}]=========   Results   =========\n",
            stats,
            f"\n[{c1}]=================================",
        )




class Socket_Port_Scanner():
    """This class will be used to peform a full blown port scan off all 65,535 ports"""

    total          = 0
    total_ports    = 0
    ports_scanned  = 0
    ip_port_map    = {}


    @classmethod
    def _port_scanner(cls, ip, port, timeout, verbose=False):
        """This will peform port scan on said ip"""

        cls.ports_scanned += 1


        if cls.ports_scanned % 100 == 0:
            with Variables.LOCK:
                Variables.panel_text = (f"[yellow]IPs:[/yellow] {cls.total}  -  [yellow]Ports Scanned:[/yellow] {cls.ports_scanned}  -  [yellow]Open:[/yellow] {cls.total_ports}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))

                if result == 0:
                    with Variables.LOCK:
                        console.print(f"[bold green][+] Active:[/bold green][yellow] {ip}:[/yellow]{port}")

                        if ip not in cls.ip_port_map: cls.ip_port_map[ip] = {"ports": []}

                        cls.ip_port_map[ip]["ports"].append(port)
                        cls.total_ports += 1

                    return True

                return False

        except Exception as e:
            if verbose: console.print(f"[bold red]Exception Error:[bold yellow] {e}")
            return False




    @classmethod
    def _threader_all(cls, ips, max_threads, timeout=1):
        """Single thread pool for all IP:port combinations"""

        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for ip in ips:
                cls.total += 1
                console.print(f"[bold green][+] Scanning:[yellow] {ip}")

                # Submit all ports for this IP and wait for completion before next IP
                futures = [executor.submit(cls._port_scanner, ip, port, timeout) for port in range(0, 65536)]

                with Variables.LOCK: Variables.panel_text = (f"[yellow]IPs:[/yellow] {cls.total}  -  [yellow]Ports Scanned:[/yellow] {cls.ports_scanned}  -  [yellow]Open:[/yellow] {cls.total_ports}")


    

    @classmethod
    def main(cls):
        

        ips         = Variables.ips
        timeout     =  Variables.timeout
        max_threads = Variables.max_threads


        ips = File_Saver.ips_sanitizer(ips=ips, verbose=True)
        time_total = time.time()


        p = "=" * 10
        console.print(f"[bold red]\n{p}  Mass Port Scanning  {p}\n")
        cls._threader_all(ips=ips, max_threads=max_threads, timeout=timeout)
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