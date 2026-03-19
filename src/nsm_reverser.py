# THIS WILL BE FOR RESOLVING



# UI IMPORTS
from rich.table import Table
from rich.panel import Panel



# ETC IMPORTS
import dns.resolver, socket, ssl, sys, time, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor



# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import File_Saver



# CONSTANTS
console = Variables.console

# reuse the same resolver instead of creating one per call like a goldfish with no memory
_resolver = dns.resolver.Resolver()
_resolver.timeout = 3
_resolver.lifetime = 3


# shared colors because copy-pasting them in every method was getting old
C1 = "bold green"
C2 = "bold yellow"
C4 = "bold blue"
C5 = "yellow"
C6 = "bold red"




class Reverse_IP_Domain():
    """This class will be responsible for pulling domains from ips"""


    scan_socket = 0
    scan_ssl    = 0
    scan_ptr    = 0

    scan = 0
    total = 0




    @classmethod
    def _ips_sanitzer(cls, ips, verbose=True) -> set:
        """This will sanitize and validate ips list"""

        valid_ips = set()


        try:

            path = Path() / str(ips)
            if not path.exists(): console.print(f"[{C6}][-] Invalid wordlist given, please check README.md for help!"); sys.exit()
            console.print(path)
            with open(path, "r") as file:

                for word in file:
                    ip = word.strip().split('\t'); ip = ''.join(ip)
                    console.print(ip)
                    Variables.panel_text = (f"Target:[{C5}] {ip}[/{C5}]  -  Max_Workers:[{C5}] {Variables.max_threads}[/{C5}]  -  Errors:[{C5}] {Variables.errors}[/{C5}]")
                    valid_ips.add(ip)

            cls.total = len(valid_ips)
            if verbose: console.print(f"\n\n[{C1}][+] Successfully sanitized list <-- ips.txt ")
            return valid_ips

        except Exception as e: console.print(f"[{C6}][-] Exception Error:[/{C6}] {e}"); sys.exit()



    @classmethod
    def _pull_domains_socket(cls, ip, verbose=False):
        """This will pull domains using the socket library"""


        try:

            domain = socket.gethostbyaddr(ip)[0]
            if not domain: return False


            with Variables.LOCK:
                console.print(f"[{C1}][*] Socket:[{C2}] {domain}")
                Variables.found_doms.add(domain)
                cls.scan_socket += 1


        except Exception as e:
            if verbose: console.print(f"[{C6}][-] Socket Exception Error:[{C2}] {e}")
            Variables.errors +=1


    @classmethod
    def _pull_domains_ssl(cls, ip, verbose=False):
        """This will pull domains using the ssl library"""


        try:

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, 443))

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            ssl_sock = context.wrap_socket(sock, server_hostname=ip)

            cert_bin = ssl_sock.getpeercert(binary_form=True)
            ssl_sock.close()

            import OpenSSL.crypto
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_bin)

            domains = set()

            subject = x509.get_subject()
            cn = subject.CN
            if cn:
                domains.add(cn)

            for i in range(x509.get_extension_count()):
                ext = x509.get_extension(i)
                if 'subjectAltName' in str(ext.get_short_name()):
                    san_str = str(ext)
                    for san in san_str.split(','):
                        san = san.strip()
                        if san.startswith('DNS:'):
                            domain = san.replace('DNS:', '')
                            domains.add(domain)


            if domains:
                with Variables.LOCK:
                    cls.scan_ssl += 1
                    for domain in domains:
                        console.print(f"[{C1}][*] SSL:[{C2}] {domain}")
                        Variables.found_doms.add(domain)

                    Variables.panel_text = (f"IP:[{C5}] {cls.scan}/{cls.total}[/{C5}]  -  Socket:[{C5}] {cls.scan_socket}[/{C5}]  -  SSL:[{C5}] {cls.scan_ssl}[/{C5}]  -  PTR:[{C5}] {cls.scan_ptr}[/{C5}]  -  Max_Workers:[{C5}] {Variables.max_threads}[/{C5}]  -  Errors:[{C5}] {Variables.errors}[/{C5}]")



        except socket.timeout:
            if verbose: console.print(f"[{C6}][-] SSL: Timeout connecting to {ip}:443")
            Variables.errors +=1
        except ConnectionRefusedError:
            if verbose: console.print(f"[{C6}][-] SSL: Connection refused for {ip}:443")
            Variables.errors +=1
        except Exception as e:
            if verbose: console.print(f"[{C6}][-] SSL Exception Error:[{C2}] {e}")
            Variables.errors +=1


    @classmethod
    def _pull_domains_ptr(cls, ip, verbose=False):
        """This will pull domains using PTR DNS records"""


        try:

            cls.scan += 1

            rev_ip = dns.reversename.from_address(ip)
            answers = _resolver.resolve(rev_ip, 'PTR')

            with Variables.LOCK:
                cls.scan_ptr += 1
                for rdata in answers:
                    domain = str(rdata).rstrip('.')
                    console.print(f"[{C1}][*] PTR:[{C2}] {domain}")
                    Variables.found_doms.add(domain)

                Variables.panel_text = (f"IP:[{C5}] {cls.scan}/{cls.total}[/{C5}]  -  Socket:[{C5}] {cls.scan_socket}[/{C5}]  -  SSL:[{C5}] {cls.scan_ssl}[/{C5}]  -  PTR:[{C5}] {cls.scan_ptr}[/{C5}]  -  Max_Workers:[{C5}] {Variables.max_threads}[/{C5}]  -  Errors:[{C5}] {Variables.errors}[/{C5}]")

        except dns.resolver.NXDOMAIN:
            if verbose: console.print(f"[{C6}][-] PTR: No PTR record for {ip}")
            Variables.errors +=1
        except dns.resolver.NoAnswer:
            if verbose: console.print(f"[{C6}][-] PTR: No answer for {ip}")
            Variables.errors +=1
        except Exception as e:
            if verbose: console.print(f"[{C6}][-] PTR Exception Error:[/{C6}] {e}")
            Variables.errors +=1


    @classmethod
    def _threader(cls, max_threads, ips):
        """Thread that task"""

        max_threads = int(max_threads)
        futures = []
        cls.total = len(ips)
        cls.time_start = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:

            try:

                for ip in ips:

                    futures.append(executor.submit(Reverse_IP_Domain._pull_domains_socket, ip))
                    futures.append(executor.submit(Reverse_IP_Domain._pull_domains_ssl, ip))
                    futures.append(executor.submit(Reverse_IP_Domain._pull_domains_ptr, ip))

                    Variables.panel_text = (f"IP:[{C5}] {cls.scan}/{cls.total}[/{C5}]  -  Socket:[{C5}] {cls.scan_socket}[/{C5}]  -  SSL:[{C5}] {cls.scan_ssl}[/{C5}]  -  PTR:[{C5}] {cls.scan_ptr}[/{C5}]  -  Max_Workers:[{C5}] {Variables.max_threads}[/{C5}]  -  Errors:[{C5}] {Variables.errors}[/{C5}]")



            except Exception as e: console.print(f"[{C6}][-] Exception Error:[/{C6}] {e}");  Variables.errors +=1



    @classmethod
    def _clean_domains(cls, domains):
        """
        Clean domain list for external tool usage

        Filters out:
        - Wildcard domains (but saves root domain: *.example.com -> example.com)
        - Certificate junk (CloudFlare Origin, WAF, Traefik default certs)
        - PTR noise (ptr.network, centraldnserver.com)
        - Hash domains (32+ char hex strings from default certificates)
        - Invalid domains (no TLD, single words, malformed)
        - IP addresses formatted as domains
        - Empty lines

        Returns: Sorted list of clean, usable domains
        """

        cleaned = set()
        Variables.panel_text = (f"[{C5}] Cleaning and Saving Results!")

        for domain in domains:
            domain = domain.strip()

            if not domain:
                continue

            if domain.startswith('*'):
                root = domain.replace('*.', '')
                if root and '.' in root:
                    cleaned.add(root.lower())
                continue

            if any(x in domain.lower() for x in ['certificate', 'waf', 'traefik.default', 'origin', 'reported', 'attack behavior']):
                continue

            if any(x in domain for x in ['ptr.network', 'centraldnserver.com', 'ip-ptr.tech', 'static.hostiran.name', 'localhost']):
                continue

            if len(domain.split('.')[0]) > 30 and domain.split('.')[0].replace('-', '').isalnum():
                continue

            if re.match(r'^[\d\-\.]+\.(static|ip-ptr|ptr)', domain):
                continue

            if '.' not in domain:
                continue

            tld = domain.split('.')[-1]
            if not tld.isalpha() or len(tld) < 2 or len(tld) > 10:
                continue

            if domain.count('.') == 3 and all(part.isdigit() for part in domain.split('.')):
                continue

            cleaned.add(domain.lower())



        return sorted(cleaned)

    @classmethod
    def main(cls):
        """This will control domain <-- ip  // mapping"""


        ips         = Variables.ips
        max_threads = Variables.max_threads


        ips = File_Saver.ips_sanitizer(ips=ips)

        p = "=" * 10
        console.print(f"[bold red]\n{p}  IP Enumeration  {p}\n")
        Reverse_IP_Domain._threader(max_threads=max_threads, ips=ips)


        File_Saver.push_scan_results(data=Variables.found_doms, reverse=True)

        cleaned_domains = Reverse_IP_Domain._clean_domains(Variables.found_doms)
        File_Saver.push_scan_results(data=cleaned_domains, reverse=True)


        from run import Run
        time_total = time.time() - cls.time_start
        Run.title(text="ReverseDNS Results", results=len(Variables.found_doms), total_scans=cls.total, total_time=time_total)
