#!/usr/bin/env python3
# 🔥 MailXtract v4.2 — Email Info Scanner
# Author  : Alok Thakur
# YouTube : Firewall Breaker

import os, re, socket, requests, dns.resolver, whois
from hashlib import md5
from datetime import datetime, timezone
from pathlib import Path
from colorama import Fore, Style, init
init(autoreset=True)

# ── Colour codes ────────────────────────────────────────────────────
RED="\033[31m"; GRN="\033[32m"; YEL="\033[33m"
BLU="\033[34m"; MAG="\033[35m"; CYN="\033[36m"; RST="\033[0m"
WHT="\033[37m"

# ── Disposable domains (sample) ─────────────────────────────────────
DISPOSABLE_DOMAINS = {
    "mailinator.com","tempmail.com","10minutemail.com","yopmail.com",
    "trashmail.com","guerrillamail.com","sharklasers.com","getnada.com"
}

# ── Offline breach demo DB (optional) ───────────────────────────────
DEMO_BREACH_DUMP = {
    "john@example.com": ["DemoLeak2022"],
    "alice@sample.net": ["OldBreach2019","AnotherLeak2021"]
}

BLACKLIST_ZONES = ["multi.surbl.org","zen.spamhaus.org"]
HEADERS = {"User-Agent":"MailXtract/4.2"}

# ── HTML report template ────────────────────────────────────────────
HTML_HEAD = (
    "<html><head><meta charset='utf-8'><title>MailXtract Report</title>"
    "<style>body{font-family:Arial;background:#f7f7f7;padding:20px}"
    "table{width:100%;border-collapse:collapse;background:#fff}"
    "th,td{border:1px solid #ccc;padding:8px;text-align:left}"
    "th{background:#eaeaea}</style></head><body>"
    "<h1>MailXtract Report</h1><table>"
)
HTML_TAIL="</table></body></html>"

# ── Banner (4‑line) ────────────────────────────────────────────────
BANNER=f"""
{RED}╔════════════════════════════════════════════╗
{GRN}║ {YEL}🔍 MailXtract v4.2 — Email Info Scanner{' '*5}{GRN}║
{BLU}║ {MAG}Created by: {WHT}Alok Thakur{' '*15}{BLU}║
{CYN}║ {YEL}YouTube: {CYN}Firewall Breaker{' '*18}{CYN}║
{RED}╚════════════════════════════════════════════╝{RST}
"""

# ── Helper functions ────────────────────────────────────────────────
def rfc_validate(email:str)->bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",email))

def split_email(email:str):
    return email.split("@")[0],email.split("@")[1].lower()

def qdns(domain:str,rtype:str):
    try:
        res=dns.resolver.Resolver()
        res.nameservers=['8.8.8.8','1.1.1.1']      # Google + Cloudflare DNS
        return [r.to_text().strip('"') for r in res.resolve(domain,rtype,lifetime=6)]
    except: return None

def get_ip(domain:str):
    try:return socket.gethostbyname(domain)
    except:return None

def dnssec(domain:str)->bool:
    return bool(qdns(domain,"DNSKEY"))

def bl_check(domain:str):
    for zone in BLACKLIST_ZONES:
        try:
            query=".".join(reversed(domain.split(".")))+"."+zone
            dns.resolver.resolve(query,"A",lifetime=4)
            return True,zone
        except: continue
    return False,None

def geo(ip:str):
    if not ip: return None
    # primary: ipapi
    try:
        r=requests.get(f"https://ipapi.co/{ip}/json/",timeout=6,headers=HEADERS)
        if r.status_code==200:
            d=r.json()
            loc=", ".join(filter(None,[d.get("city"),d.get("region"),d.get("country_name")])) or "N/A"
            return loc,d.get("org")
    except: pass
    # fallback: ipinfo
    try:
        r=requests.get(f"https://ipinfo.io/{ip}/json",timeout=6,headers=HEADERS)
        if r.status_code==200:
            d=r.json()
            loc=", ".join(filter(None,[d.get("city"),d.get("region"),d.get("country")])) or "N/A"
            return loc,d.get("org")
    except: pass
    return None

def spf_dmarc(domain:str):
    spf=dmarc="Not found"
    for rec in (qdns(domain,"TXT") or []):
        if "v=spf" in rec.lower(): spf=rec; break
    dmarc_txt=qdns(f"_dmarc.{domain}","TXT") or []
    if dmarc_txt: dmarc=dmarc_txt[0]
    return spf,dmarc

def mx(domain:str): return qdns(domain,"MX") or []

def grav(email:str):
    url=f"https://www.gravatar.com/avatar/{md5(email.lower().encode()).hexdigest()}?d=404"
    try:found=requests.get(url,timeout=6).status_code==200
    except:found=False
    return found,url

def who(domain:str):
    try:return whois.whois(domain)
    except:return None

def clean_date(dt):
    if isinstance(dt,list):dt=dt[0]
    return dt.date() if hasattr(dt,"date") else dt

def age(dt):
    try:
        if isinstance(dt,list): dt=dt[0]
        return datetime.now(timezone.utc).year-dt.year if dt else "Unknown"
    except:return "Unknown"

def save_txt(lines,file="output.txt"):
    Path(file).write_text("\n".join(lines),encoding="utf-8")
    print(f"{BLU}📁 Text report saved to {file}{RST}")

def save_html(rows,file="output.html"):
    body="\n".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in rows)
    Path(file).write_text(HTML_HEAD+body+HTML_TAIL,encoding="utf-8")
    print(f"{BLU}📁 HTML report saved to {file}{RST}")

# ── Main ────────────────────────────────────────────────────────────
def main():
    os.system("clear")
    print(BANNER)
    email=input(f"{YEL}📧 Enter Email: {RST}").strip()
    if not rfc_validate(email):
        print(f"{RED}[!] Invalid email format{RST}"); return

    user,domain=split_email(email)
    lines,rows=[],[]
    add=lambda k,v:(lines.append(f"{k}: {v}"),rows.append((k,v)))

    add("Email",email)
    add("Username",user)
    add("Domain",domain)
    add("Disposable","Yes" if domain in DISPOSABLE_DOMAINS else "No")
    add("Provider Logo",f"https://logo.clearbit.com/{domain}")
    add("Offline Breach",", ".join(DEMO_BREACH_DUMP.get(email.lower(),[])) or "No match")

    w=who(domain); registrar=w.registrar if w and w.registrar else "N/A"
    created=clean_date(w.creation_date) if w else "N/A"
    add("Registrar",registrar)
    add("Created",f"{created} ({age(w.creation_date) if w else 'Unknown'} years)")

    ip=get_ip(domain); add("IP Address",ip or "Not Found")
    g=geo(ip); add("Location",g[0] if g else "N/A"); add("ISP",g[1] if g else "N/A")
    add("DNSSEC","Yes" if dnssec(domain) else "No")
    bl,zone=bl_check(domain); add("Blacklisted",f"Yes ({zone})" if bl else "No")
    spf,dmarc=spf_dmarc(domain); add("SPF",spf); add("DMARC",dmarc)
    add("MX",", ".join(mx(domain)) or "None")
    gfound,gurl=grav(email); add("Gravatar",gurl if gfound else "Not Found")

    save_txt(lines); save_html(rows)
    print(f"\n{GRN}✅ Scan Complete. Reports generated.{RST}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Exiting…{RST}")

