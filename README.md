<div align="center">
  <img src="assets/banner.svg" alt="MAUL - Brother Program of Vader" width="100%"/>

  <br/>

  <img src="assets/darth_maul.png" alt="Darth Maul" width="300"/>
</div>

---

### *By a Star Wars Nerd*

> **"Fear is my ally."** - Darth Maul

Infrastructure mapping and enumeration tool. Takes IPs/domains from **Vader** and maps infrastructure via PTR records, SSL certs, subdomain/directory bruteforcing.

**Core Features:** IP-to-Domain mapping • SSL cert extraction • Subdomain enumeration • Directory scanning • Multi-threaded

---

## Installation

```bash
git clone https://github.com/nsm-barii/maul.git
cd maul/src
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

**Reverse DNS lookup:**
```bash
venv/bin/python main.py -i ips.txt --rdns --save
```

**Port scanning:**
```bash
venv/bin/python main.py -i ips.txt --ports -t 100 --timeout 1 --save
```

**Subdomain enumeration:**
```bash
venv/bin/python main.py -d domains.txt --subs --sub-wordlist 2 -t 100 --save
```

**Directory bruteforce:**
```bash
venv/bin/python main.py -d domains.txt --dirs --dir-wordlist 2 -t 50 --timeout 5 --save
```

**Full workflow:**
```bash
venv/bin/python main.py -i ips.txt --all -t 100 --sub-wordlist 2 --dir-wordlist 2 --save
```

---

## Key Arguments

### Input Options
| Flag | Description |
|------|-------------|
| `-i` | IP list file |
| `-u` | Single URL/domain |
| `-d` | Domain list file |
| `-t` | Max threads (default: 250) |

### Scan Types
| Flag | Description |
|------|-------------|
| `--rdns` | Reverse DNS lookup on IPs |
| `--ports` | Port scan on IPs (all 65535 ports) |
| `--subs` | Subdomain enumeration |
| `--dirs` | Directory/file bruteforce |
| `--all` | Run all scan types |

### Scan Configuration
| Flag | Description |
|------|-------------|
| `--status-codes` | HTTP status codes to filter (default: 200,204,301,302,303,304) |
| `--sub-wordlist` | `1`/`tiny.txt`, `2`/`small.txt`, `3`/`medium.txt`, `4`/`large.txt` (default: 2) |
| `--dir-wordlist` | `1`/`tiny.txt`, `2`/`small.txt`, `3`/`medium.txt`, `4`/`large.txt` (default: 2) |
| `--mutations` | Custom mutations wordlist for subdomain permutations |

### Output
| Flag | Description |
|------|-------------|
| `--timeout` | Request timeout in seconds (default: 5) |
| `--save` | Save scan results to file |
| `--x` | Custom output filename |

---

## About

Created by **NSM-Barii** - Star Wars nerd | Cybersecurity enthusiast

**NSM Toolset:**
- **Vader** - Recon & discovery
- **Maul** - Infrastructure mapping

---

**Disclaimer:** Authorized testing only. Unauthorized scanning is illegal.

MIT License
