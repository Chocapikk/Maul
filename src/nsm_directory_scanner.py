# THIS WILL BE FOR DIRECTORY BRUTEFORCING AND THAT ALONE


# UI IMPORTS


# ETC IMPORTS
import requests
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import deque


# NSM IMPORTS
from nsm_vars import Variables


# CONSTANTS
console = Variables.console

# wordlist presets (yes this dict exists in 3 files, deal with it)
WORDLIST_PRESETS = {
    "1": "tiny.txt",
    "2": "small.txt",
    "3": "medium.txt",
    "4": "large.txt",
}


class Directory_Scanner:
    """directory scanner (the docstring used to say "subdomain scanner" lmao, copy paste strikes again)"""

    done = 0
    total = 0
    scanned = 0
    scan = True
    current_dir = False
    creations = deque()

    @classmethod
    def _iter_controller(
        cls, url=False, domains=False, directores=False, CONSOLE=console
    ):
        """This will be respomsible for passing domain and dir arguments"""

        if not cls.creations:
            if domains:
                targets = list(domains)
            else:
                targets = [url]
            cls.total = len(targets) * len(directores)
            for dom in targets:
                for sub in directores:
                    cls.creations.append((dom, sub))

            CONSOLE.print(f"Iterations made: {len(cls.creations)}")
            return False

        s, d = cls.creations.popleft()
        return s, d

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
                    # .strip() is all you need, the old split("\n")/join("\n") was a round trip to nowhere
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

    @staticmethod
    def _dir_sanitzer(wordlist, CONSOLE=console, verbose=True) -> list:
        """This method will be responsible for santizing the directory wordlist"""

        c1 = "bold green"
        c2 = "bold yellow"
        c6 = "bold red"

        valid_wordlist = set()

        path_main = Path(__file__).parent.parent / "database" / "directories"

        # dict lookup, say goodbye to the if/elif tower of babel
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
                CONSOLE.print(f"[{c1}][+] Successfully validated dir wordlist: {path}")
            return valid_wordlist

        except FileNotFoundError as e:
            CONSOLE.print(f"[{c6}][-] File Not Found Error:[{c2}] {e}")
            Variables.errors += 1
            return

        except Exception as e:
            CONSOLE.print(f"[{c6}][-] Exception Error:[{c2}] {e}")
            Variables.errors += 1
            sys.exit()

    @classmethod
    def _directory_scanner(cls, mutations=False, CONSOLE=console, verbose=False):
        """Directory scan happens here (not subdomain scan, despite what the old docstring claimed)"""

        c1 = "bold green"
        c2 = "bold yellow"
        c5 = "yellow"
        c6 = "green"
        c7 = "bold red"

        if not cls.scan:
            return False
        with Variables.LOCK:
            # same TOCTOU fix as subdomain scanner, check inside the lock
            if not cls.creations:
                return False
            subdomain, directory = Directory_Scanner._iter_controller()
            Variables.completed_dir += 1
            cls.scanned += 1

        try:
            domain = f"{subdomain}/{directory}"
            url = f"http://{domain}"
            Variables.panel_text = f"Target:[{c5}] {subdomain}/*[/{c5}]  -  Enumeration:[{c5}] {cls.scanned}/{cls.total}[/{c5}]  -  Max_Workers:[{c5}] {Variables.max_threads}[/{c5}]  -  Wordlist:[{c5}] {Variables.s_name}[/{c5}]  -  Errors:[{c5}] {Variables.errors}[/{c5}]"

            response = requests.get(
                url=url,
                timeout=int(Variables.timeout),
                allow_redirects=False,
                verify=False,
            )
            code = response.status_code

            if code in Variables.status_codes:
                with Variables.LOCK:
                    if code in [200, 204]:
                        cc = c6
                    elif code in [300, 301, 302, 303, 304]:
                        cc = c2
                    else:
                        cc = c7  # everything else gets the angry red treatment

                    CONSOLE.print(f"[{c1}][[{cc}]{code}[/{cc}]][/{c1}][white] {domain}")
                    Variables.found_dirs.add(domain)
                    return True

        except requests.exceptions.SSLError as e:
            if verbose:
                CONSOLE.print(f"[{c7}][-] SSL Error:[{c2}] {e}")
            Variables.errors += 1
        except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
            if verbose:
                CONSOLE.print(f"[{c7}][-] Timeout Error:[{c2}] {e}")
            Variables.errors += 1
        except requests.ConnectionError as e:
            if verbose:
                CONSOLE.print(f"[{c7}][-] Connection Error:[{c2}] {e}")
            Variables.errors += 1
        except Exception as e:
            if verbose:
                CONSOLE.print(f"[{c7}][-] Exception Error:[{c2}] {e}")
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
    def _threader(cls, max_threads, CONSOLE=console, verbose=True):
        """This will iter through and thread --> _directory_scanner"""

        c5 = "yellow"
        c6 = "bold red"

        futures = []
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
                CONSOLE.print(f"[[{c6}]][-] Exception Error:[{c5}] {e}")
                Variables.errors += 1
                cls.scan = False
            except Exception:
                Variables.errors += 1
                cls.scan = False

    @classmethod
    def main(cls):
        """This will run class wide logic"""

        subdomains = Variables.domains
        max_threads = Variables.max_threads
        url = Variables.url
        wordlist = Variables.wordlist_dir

        if Variables.domains:
            subdomains = Directory_Scanner._domain_sanitzer(domains=subdomains)
        elif Variables.found_subs:
            subdomains = Variables.found_subs
        elif Variables.found_doms:
            subdomains = Variables.found_doms
        else:
            subdomains = False
        if not subdomains and not url:
            console.print("\n[bold red][-] Input a valid domain goofy")
            return

        wordlist = Directory_Scanner._dir_sanitzer(wordlist=wordlist)
        p = "=" * 10
        console.print(f"[bold red]\n{p}  Directory Enumeration  {p}\n")
        Directory_Scanner._iter_controller(
            url=url, domains=subdomains, directores=wordlist
        )
        Directory_Scanner._threader(max_threads=max_threads)

        from run import Run

        time_total = time.time() - cls.time_start
        Run.title(
            text="Directory Results",
            results=len(Variables.found_dirs),
            total_scans=cls.total,
            total_time=time_total,
        )
