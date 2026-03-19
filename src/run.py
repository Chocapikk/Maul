# THIS WILL RUN ALL SCANS AS A MAIN INSTANCE // ITS REALLY FOR THE LIVE FEATURE // LOL


# UI IMPORT
from rich.live import Live


# ETC IMPORTS
import time
import threading


# NSM IMPORTS
from nsm_vars import Variables
from nsm_reverser import Reverse_IP_Domain
from nsm_port_scanner import Socket_Port_Scanner
from nsm_subdomain_scanner import Subdomain_Scanner
from nsm_directory_scanner import Directory_Scanner
from nsm_database import File_Saver


# CONSTANTS
console = Variables.console


class Run:
    """Run scans"""

    @staticmethod
    def title(text, results, total_scans, total_time=False):
        """This will be used to print text"""

        if total_time:
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            total_time = f"{hours}:{minutes}:{seconds}"

        c1 = "red"
        c2 = "bold green"
        c4 = "bold yellow"

        stats = (
            f"[{c2}] [+] Results:[{c4}] {results}"
            f"\n[{c2}]  [+] Total Scans:[{c4}] {total_scans}"
            f"\n[{c2}]  [+] Elapsed Time:[{c4}] {total_time}"
        )

        console.print(
            f"\n\n[{c1}]=========   {text}   =========\n",
            stats,
            f"\n[{c1}]=================================\n\n",
        )

    @staticmethod
    def _update():
        """This will auto update the panel.renderable // since doing it within a thread fucks it up and doesnt work"""

        Variables.console.print("\n[yellow][*] Background Thread started")

        while True:
            text = Variables.panel_text
            Variables.panel.renderable = text

            # was 0.0005 (2000 updates/sec) which is completely unhinged, 50ms is fine
            time.sleep(0.05)

    @staticmethod
    def runner():
        """I need no comment // LOL"""

        with Live(
            Variables.panel,
            console=Variables.console,
            refresh_per_second=Variables.refresh_per_second,
        ):
            threading.Thread(target=Run._update, args=(), daemon=True).start()

            if Variables.save:
                File_Saver.make_path()

            if Variables.ips and Variables.scan_rdns:
                Reverse_IP_Domain.main()
            if Variables.ips and Variables.scan_ports:
                Socket_Port_Scanner.main()

            if Variables.scan_sub:
                Subdomain_Scanner.main()
            if Variables.scan_dir:
                Directory_Scanner.main()

            # save results - each type gets its own file so they don't overwrite each other
            # (the old code wrote both subs and dirs to the same path, RIP subdomain results)
            if Variables.save:
                if Variables.found_subs:
                    File_Saver.push_scan_results(data=Variables.found_subs)
                if Variables.found_dirs:
                    File_Saver.push_scan_results(
                        data=Variables.found_dirs, reverse=True
                    )
