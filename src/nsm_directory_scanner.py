# THIS WILL BE FOR DIRECTORY BRUTEFORCING AND THAT ALONE



# UI IMPORTS 
from rich.panel import Panel


# ETC IMPORTS
import requests, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import deque



# NSM IMPORTS
from nsm_vars import Variables



# CONSTANTS
console = Variables.console




class Directory_Scanner():
    """subdomain scanner"""

    
    done  = 0
    total = 0
    scan = True
    current_dir = False
    creations = deque()
   

    @classmethod
    def _iter_controller(cls, url=False, domains=False, subdomains=False, CONSOLE=console):
        """This will be respomsible for passing domain and sub arguments"""
    

        if not cls.creations:
            if domains: targets = [domain for domain in domains] 
            else:       targets = []; targets.append(url)
            cls.total = len(targets) * len(subdomains)
            for dom in targets:
                for sub in subdomains:
                    #console.print(sub, dom)
                    cls.creations.append((sub, dom))
            
            CONSOLE.print(f"Iterations made: {len(cls.creations)}"); return False
        
        s, d = cls.creations.popleft()
        #if cls.current_dir != s: cls.current_dir = s
        #console.print(s,d)
        return s,d
    

    @staticmethod
    def _domain_sanitzer(domains, CONSOLE=console, verbose=True) -> list:
        """This will sanitize domain wordlist given by user --> coming from Vader --> Maul"""


        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"


        valid_domains = []


        try:

            path = Path() / str(domains)
            if not path.exists(): CONSOLE.print(f"[{c6}][-] Invalid domain wordlist given, please check README.md for help!"); sys.exit()

            with open(str(path), "r") as file:

                for word in file:
                    text = word.strip().split("\n"); text = '\n'.join(text)
                    valid_domains.append(text)


            if verbose: CONSOLE.print(f"[{c1}][+] Successfully validated domain wordlist: {path}")
            return valid_domains
            
        

        except FileNotFoundError as e: CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}"); Variables.errors += 1; sys.exit()

        except Exception as e: CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}"); Variables.errors += 1; sys.exit()
    

        

    @staticmethod
    def _dir_sanitzer(wordlist, CONSOLE=console, verbose=True) -> list:
        """This method will be responsible for santizing the subdomain wordlist"""
        
        
        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"


        valid_wordlist = set()

        path_main = Path(__file__).parent.parent / "database" / "directories" 
        path  = False


        try:

            if   wordlist=="1" or wordlist=="tiny.txt":     path = path_main / "tiny.txt"
            elif wordlist=="2" or wordlist=="small.txt":    path = path_main / "small.txt"
            elif wordlist=="3" or wordlist=="medium.txt":   path = path_main / "medium.txt"   
            elif wordlist=="4" or wordlist=="large.txt":    path = path_main / "large.txt"


            if not path: path = Path(__file__).parent.parent / "database" / f"directories" / str(wordlist)
            if not path.exists(): CONSOLE.print(f"[{c6}][-] Invalid wordlist given, please check README.md for help!"); sys.exit()


            with open(str(path), "r") as file:

                for word in file:
                    text = word.strip().split("\t"); text = ''.join(text)
                    valid_wordlist.add(text)


                
            if verbose: CONSOLE.print(f"[{c1}][+] Successfully validated dir wordlist: {path}")
            return valid_wordlist
                

        except FileNotFoundError as e: CONSOLE.print(f"[{c6}][-] File Not Found Error:[{c2}] {e}"); Variables.errors += 1; return

        except Exception as e: CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}"); Variables.errors += 1; sys.exit()
    

    @classmethod
    def _directory_scanner(cls, mutations=False, CONSOLE=console, verbose=False):
        """Subdomain scan happens here"""


        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "green"
        c7 = "bold red"

        if not cls.scan: return Exception
        with Variables.LOCK: subdomain, dir = Directory_Scanner._iter_controller(); Variables.completed_dir += 1; cls.scanned += 1
       

        try: 
            
            subdomain = f"{subdomain}/{dir}"
            url = f"http://{subdomain}/{dir}"
            Variables.panel_text = f"Target:[{c5}] {subdomain}/*[/{c5}]  -  Enumeration:[{c5}] {cls.scanned}/{cls.total}[/{c5}]  -  Max_Workers:[{c5}] {Variables.max_threads}[/{c5}]  -  Wordlist:[{c5}] {Variables.s_name}[/{c5}]  -  Errors:[{c5}] {Variables.errors}[/{c5}]"


            response = requests.get(url=url, timeout=int(Variables.timeout), allow_redirects=False, verify=False)
            code     = response.status_code
            headers  = response.headers
           

            if code in Variables.status_codes:
                
                with Variables.LOCK:

                    if code in [200,204]:cc = c6
                    elif code in [300,301,302,303,304]: cc = c2


                    CONSOLE.print(f"[{c1}][[{cc}]{code}[/{cc}]][/{c1}][white] {url}")
                    Variables.found_dirs.append(url)
                    return True


        except requests.exceptions.SSLError as e:
            if verbose: CONSOLE.print(f"[{c7}][-] SSL Error:[{c2}] {e}")
            Variables.errors += 1
        except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e: 
            if verbose: CONSOLE.print(f"[{c7}][-] Timeout Error:[{c2}] {e}")
            Variables.errors += 1
        except requests.ConnectionError as e: 
            if verbose: CONSOLE.print(f"[{c7}][-] Connection Error:[{c2}] {e}")
            Variables.errors += 1
        except Exception as e: 
            if verbose: CONSOLE.print(f"[{c7}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
    


    @classmethod
    def _worker(cls):
        """Worker thread that repeatedly runs the scanner"""

        while cls.scan:

            with Variables.LOCK:
                if not cls.creations:
                    return

            cls._directory_scanner()


    @classmethod
    def _threader(cls, max_threads, subdomains, wordlist, CONSOLE=console, verbose=True):
        """This will iter through and thread --> _subdomain_scanner"""


        c1 = "bold green"
        c2 = "bold yellow"
        c4 = "bold blue"
        c5 = "yellow"
        c6 = "bold red"


        futures = []
        total   = len(wordlist) * len(subdomains)  #
        cls.time_start = time.time()


        try: max_threads = int(max_threads)
        except Exception: max_threads = 250



        with ThreadPoolExecutor(max_workers=max_threads) as executor:

            try:

                for _ in range(max_threads): futures.append(executor.submit(cls._worker))

                for f in futures: f.result()


            except KeyboardInterrupt as e:
                CONSOLE.print(f"[[{c6}]][-] Exception Error:[{c5}] {e}")
                Variables.errors += 1
                cls.scan = False
            except Exception as e:
                Variables.errors += 1
                cls.scan = False
    
    

    @classmethod
    def main(cls):
        """This will run class wide logic"""

        
        subdomains  = Variables.domains 
        max_threads = Variables.max_threads
        timeout     = Variables.timeout
        url         = Variables.url
        wordlist    = Variables.wordlist_dir

        

        if subdomains: subdomains = Directory_Scanner._domain_sanitzer(domains=subdomains)
        else:          subdomains = Variables.found_doms
        wordlist  = Directory_Scanner._dir_sanitzer(wordlist=wordlist)
        p = "=" * 10
        console.print(f"[bold red]\n{p}  Directory Enumeration  {p}\n")
        Directory_Scanner._iter_controller(url=url, domains=subdomains, wordlist=wordlist)
        Directory_Scanner._threader(max_threads=max_threads, subdomains=subdomains, wordlist=wordlist)


        from run import Run
        time_total = time.time() - cls.time_start
        Run.title(text="Directory Results", results=len(Variables.found_dirs), total_scans=cls.total, total_time=time_total)
    
    
        
