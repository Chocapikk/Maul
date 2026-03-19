# TRYING SOMETHING NEW // WILL HOST ALL MULTI-MODULE VARS HERE


# ONE IMPORT // LOL
import threading
from rich.console import Console
from rich.panel import Panel


class Variables():
    """Host multi-module vars in here"""



    # TYPE OF SCAN
    scan_rdns  = False
    scan_ports = False
    scan_sub   = False
    scan_dir   = False
    scan_sd    = False


    ips          = False
    url          = False
    domains      = False

    wordlist_sub = False
    wordlist_dir = False
    mutations    = False

    s_name       = False
    d_name       = False

    status_codes = False

    max_threads = 250
    timeout     = 1
    save        = False
    save_name   = False
    # RLock so the same thread can re-acquire without deadlocking itself like a dumbass
    LOCK        = threading.RLock()

    # sets not lists, because duplicates are for people who don't respect RAM
    found_doms = set()
    found_subs = set()
    found_dirs = set()


    console = Console()
    panel_text = "Starting"
    panel   = Panel(renderable="Starting", style="bold red", border_style="bold purple", expand=False)
    refresh_per_second = 1





    completed_sub = 0
    completed_dir = 0
    # COLLECT ALL ERRORS
    errors = 0

