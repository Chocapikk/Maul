# THIS WILL BE RESPONSIBLE FOR SUBDOMAIN SCAN // AND SUBDOMAIN SCAN ONLY


# UI IMPORTS


# ETC IMPORTS
import sys
import time
import dns.resolver
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import deque


# NSM IMPORTS
from nsm_vars import Variables


# CONSTANTS
console = Variables.console
resolver = dns.resolver.Resolver(configure=False)

resolver.timeout = 2
resolver.lifetime = 2

resolver.nameservers = ["1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4", "9.9.9.9"]


# wordlist presets because typing the same if/elif 4 times is a form of self harm
WORDLIST_PRESETS = {
    "1": "tiny.txt",
    "2": "small.txt",
    "3": "medium.txt",
    "4": "large.txt",
}


class Subdomain_Scanner:
    """subdomain scanner"""

    done = 0
    scan = True
    creations = deque()
    total = 0
    current_sub = False

    @classmethod
    def _iter_controller(
        cls, url=False, domains=False, subdomains=False, CONSOLE=console
    ):
        """This will be respomsible for passing domain and sub arguments"""

        if not cls.creations:
            if domains:
                targets = list(domains)
            else:
                targets = [url]
            cls.total = len(targets) * len(subdomains)
            for dom in targets:
                for sub in subdomains:
                    cls.creations.append((sub, dom))

            CONSOLE.print(f"Iterations made: {len(cls.creations)}")
            return False

        s, d = cls.creations.popleft()
        return s, d

    @staticmethod
    def _sub_sanitzer(wordlist, CONSOLE=console, verbose=True) -> list:
        """This method will be responsible for santizing the subdomain wordlist"""

        c1 = "bold green"
        c2 = "bold yellow"
        c6 = "bold red"

        valid_wordlist = set()

        path_main = Path(__file__).parent.parent / "database" / "subdomains"

        # dict lookup because we're not savages
        path = WORDLIST_PRESETS.get(wordlist)
        if path:
            path = path_main / path
        else:
            path = path_main / str(wordlist)

        try:
            if not path.exists():
                CONSOLE.print(
                    f"[{c6}][-] Invalid wordlist given, please check README.md for help!"
                )
                sys.exit()

            with open(str(path), "r") as file:
                for word in file:
                    text = word.strip().split("\t")
                    text = "".join(text)
                    valid_wordlist.add(text)

            if verbose:
                CONSOLE.print(f"[{c1}][+] Successfully validated sub wordlist: {path}")
            return valid_wordlist

        except FileNotFoundError as e:
            CONSOLE.print(f"[{c6}][-] File Not Found Error:[{c2}] {e}")
            Variables.errors += 1
            return

        except Exception as e:
            CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
            sys.exit()

    @staticmethod
    def _domain_sanitzer(domains, CONSOLE=console, verbose=True) -> list:
        """This will sanitize domain wordlist given by user --> coming from Vader --> Maul"""

        c1 = "bold green"
        c2 = "bold yellow"
        c6 = "bold red"

        valid_domains = []

        try:
            path = Path() / str(domains)
            if not path.exists():
                CONSOLE.print(
                    f"[{c6}][-] Invalid domain wordlist given, please check README.md for help!"
                )
                sys.exit()

            with open(str(path), "r") as file:
                for word in file:
                    # the original did .strip().split("\n") then '\n'.join() which does absolutely nothing
                    # it's like washing your hands then washing your hands again
                    valid_domains.append(word.strip())

            if verbose:
                CONSOLE.print(
                    f"[{c1}][+] Successfully validated domain wordlist: {path}"
                )
            return valid_domains

        except FileNotFoundError as e:
            CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
            sys.exit()

        except Exception as e:
            CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
            sys.exit()

    @classmethod
    def _subdomain_scanner(cls, mutations=False, CONSOLE=console, verbose=False):
        """Subdomain scan happens here"""

        c1 = "bold green"
        c2 = "bold yellow"
        c5 = "yellow"
        c7 = "bold red"

        # "return Exception" was returning the Exception CLASS OBJECT, not raising it
        # literally returning <class 'Exception'> as a truthy value, galaxy brain move
        if not cls.scan:
            return False
        with Variables.LOCK:
            sub, domain = Subdomain_Scanner._iter_controller()
            Variables.completed_sub += 1
            cls.scanned += 1

        try:
            subdomain = f"{sub}.{domain}"
            Variables.panel_text = f"Target:[{c5}] {sub}.*[/{c5}]  -  Enumeration:[{c5}] {cls.scanned}/{cls.total}[/{c5}]  -  Max_Workers:[{c5}] {Variables.max_threads}[/{c5}]  -  Wordlist:[{c5}] {Variables.s_name}[/{c5}]  -  Errors:[{c5}] {Variables.errors}[/{c5}]"
            rdata = resolver.resolve(subdomain, "A")

            if rdata:
                CONSOLE.print(f"[{c1}][*][{c2}] {subdomain}")
                with Variables.LOCK:
                    Variables.found_subs.add(subdomain)
                    return True

        except Exception as e:
            if verbose:
                CONSOLE.print(f"[{c7}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
            return False

    @classmethod
    def _worker(cls):
        """Worker thread that repeatedly runs the scanner"""

        while cls.scan:
            with Variables.LOCK:
                if not cls.creations:
                    return

            cls._subdomain_scanner()

    @classmethod
    def _threader(cls, max_threads, CONSOLE=console, verbose=True):
        """This will iter through and thread --> _subdomain_scanner"""

        c5 = "yellow"
        c6 = "bold red"

        futures = []
        cls.scanned = 0
        cls.time_start = time.time()

        try:
            max_threads = int(max_threads)
        except Exception:
            max_threads = 250

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            try:
                for _ in range(max_threads):
                    futures.append(executor.submit(cls._worker))

                for f in futures:
                    f.result()

            except KeyboardInterrupt as e:
                if verbose:
                    CONSOLE.print(f"[{c6}][-] Exception Error:[{c5}] {e}")
                Variables.errors += 1
                cls.scan = False
                exit()

            except Exception as e:
                if verbose:
                    CONSOLE.print(f"[{c6}][-] Exception Error:[{c5}] {e}")
                Variables.errors += 1
                cls.scan = False
                exit()

    @classmethod
    def main(cls):
        """This will run class wide logic"""

        max_threads = Variables.max_threads
        url = Variables.url
        domains = Variables.domains
        wordlist = Variables.wordlist_sub

        if Variables.domains:
            domains = Subdomain_Scanner._domain_sanitzer(domains=domains)
        elif Variables.found_doms:
            domains = Variables.found_doms
        else:
            domains = False
        if not domains and not url:
            console.print("\n[bold red][-] Input a valid domain goofy")

        wordlist = Subdomain_Scanner._sub_sanitzer(wordlist=wordlist)

        p = "=" * 10
        console.print(f"[bold red]\n{p}  Subdomain Enumeration  {p}\n")
        Subdomain_Scanner._iter_controller(
            url=url, domains=domains, subdomains=wordlist
        )
        Subdomain_Scanner._threader(max_threads=max_threads)

        from run import Run

        time_total = time.time() - cls.time_start
        Run.title(
            text="Subdomain Results",
            results=len(Variables.found_subs),
            total_scans=cls.total,
            total_time=time_total,
        )
