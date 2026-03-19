# THIS WILL LAUCNH THE MAIN CODE RUNNING FROM ALL OTHER MODULES
# THIS PROGRAM IS THE BROTHER PROGRAM OF "Vader" AND IS MEANT TO BE USED ALONGSIDE IT (Optional)


# UI IMPORTS
from rich.console import Console


# NSM IMPORTS
from run import Run
from nsm_vars import Variables


# ETC IMPORTS
import argparse


# CONSTANTS
console = Console()


# LETS GET SOMETHING STRAIGHT
"""

AMERICA FIRST
AMERICA ONLY
AMERICA ALWAYS

"""
# PRO USA
# PRO WESTERN


# wordlist presets because if/elif chains are a war crime
WORDLIST_PRESETS = {
    "1": "tiny.txt",
    "2": "small.txt",
    "3": "medium.txt",
    "4": "large.txt",
}


def main():
    """This will launch program wide logic, now as a function because classes with no instances are just namespaces with extra steps"""

    # COLORS
    c1 = "bold green"
    c4 = "bold blue"

    parser = argparse.ArgumentParser(
        description="Deep infrastructure scanning and enumeration framework"
    )

    # INPUT OPTIONS
    parser.add_argument("-i", help="Input file containing list of IPs")
    parser.add_argument("-u", help="Single URL target for scanning")
    parser.add_argument("-d", help="Input file containing list of domains")
    parser.add_argument("-t", help="Maximum threads (default: 250)")

    # SCAN TYPES
    parser.add_argument(
        "--rdns", action="store_true", help="Perform reverse DNS lookup on IPs"
    )
    parser.add_argument(
        "--ports", action="store_true", help="Perform port scanning on IPs"
    )
    parser.add_argument(
        "--subs", action="store_true", help="Perform subdomain enumeration"
    )
    parser.add_argument(
        "--dirs", action="store_true", help="Perform directory/file bruteforce"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all available scan types"
    )

    # SCAN CONFIG
    parser.add_argument(
        "--status-codes",
        help="Comma-separated HTTP status codes to filter (default: 200,204,301,302,303,304)",
    )
    parser.add_argument(
        "--sub-wordlist",
        choices=[
            "1",
            "2",
            "3",
            "4",
            "tiny.txt",
            "small.txt",
            "medium.txt",
            "large.txt",
        ],
        help="Subdomain wordlist: 1=tiny, 2=small, 3=medium, 4=large (default: 2)",
    )
    parser.add_argument(
        "--dir-wordlist",
        choices=[
            "1",
            "2",
            "3",
            "4",
            "tiny.txt",
            "small.txt",
            "medium.txt",
            "large.txt",
        ],
        help="Directory wordlist: 1=tiny, 2=small, 3=medium, 4=large (default: 2)",
    )
    parser.add_argument(
        "--mutations", help="Custom mutations wordlist for subdomain permutations"
    )

    # OUTPUT
    parser.add_argument("--timeout", help="Request timeout in seconds (default: 5)")
    parser.add_argument("--save", action="store_true", help="Save scan results to file")
    parser.add_argument("--x", help="Custom output filename")

    args = parser.parse_args()

    Variables.ips = args.i
    Variables.url = args.u
    Variables.domains = args.d
    Variables.max_threads = args.t or 250

    Variables.scan_rdns = args.rdns
    Variables.scan_ports = args.ports
    Variables.scan_sub = args.subs
    Variables.scan_dir = args.dirs

    if args.all:
        Variables.scan_rdns = Variables.scan_ports = Variables.scan_sub = (
            Variables.scan_dir
        ) = True

    Variables.status_codes = args.status_codes
    Variables.wordlist_sub = args.sub_wordlist or "2"
    Variables.wordlist_dir = args.dir_wordlist or "2"

    Variables.timeout = int(args.timeout) if args.timeout else 5
    Variables.save = args.save
    Variables.save_name = args.x

    # dict lookup instead of 8 lines of if/elif (you're welcome)
    Variables.s_name = WORDLIST_PRESETS.get(Variables.wordlist_sub)
    Variables.d_name = WORDLIST_PRESETS.get(Variables.wordlist_dir)

    try:
        Variables.max_threads = int(Variables.max_threads)
    except Exception:
        Variables.max_threads = 250

    if args.status_codes:
        Variables.status_codes = [int(c) for c in args.status_codes.split(",")]
    else:
        Variables.status_codes = [200, 204, 301, 302, 303, 304]

    stats = (
        f"[{c1}][+] Url:[{c4}] {Variables.url}"
        f"\n[{c1}] [+] Domains:[{c4}] {Variables.domains}"
        f"\n[{c1}] [+] Max_Threads:[{c4}] {Variables.max_threads}"
        f"\n[{c1}] [+] Sub-Wordlist:[{c4}] {Variables.s_name}"
        f"\n[{c1}] [+] Dir-Wordlist:[{c4}] {Variables.d_name}"
        f"\n[{c1}] [+] Mutations:[{c4}] {Variables.mutations}"
        f"\n[{c1}] [+] Status_Codes:[{c4}] {Variables.status_codes}"
        f"\n[{c1}] [+] Timeout:[{c4}] {Variables.timeout}"
        f"\n[{c1}] [+] File_Saving:[{c4}] {Variables.save}"
    )

    console.print(
        f"\n[{c1}]=========   CONSTANTS   =========\n",
        stats,
        f"\n[{c1}]=================================",
    )

    # time.sleep(5); print("")

    Run.runner()


if __name__ == "__main__":
    main()
