#!/data/data/com.termux/files/usr/bin/bash
# =============================================================
#  data.sh — Launch local PHP server & print output.html link
#  Colour‑coded Termux version
#  Usage:  bash data.sh   (or  ./data.sh  if executable)
# =============================================================

# ─── Colour palette ───────────────────────────────────────────
RED="\e[31m"      # Error / stop
GRN="\e[32m"      # Success / go
YEL="\e[33m"      # Warnings / prompts
CYN="\e[36m"      # Info / highlight
RST="\e[0m"      # Reset colour

# ─── Config ───────────────────────────────────────────────────
PORT=8000  # Change to any free port e.g. 8080/9000

# ─── Ensure we are in script directory ────────────────────────
cd "$(dirname "$0")" || {
  echo -e "${RED}[!] Failed to cd into script directory.${RST}"; exit 1;
}

# ─── Verify output.html exists ────────────────────────────────
if [ ! -f output.html ]; then
  echo -e "${RED}[!] output.html not found in $(pwd)${RST}"
  exit 1
fi

# ─── Start PHP built‑in server ───────────────────────────────-
echo -e "${CYN}Starting PHP server on port ${YEL}$PORT${CYN} …${RST}"
php -S 0.0.0.0:"$PORT" >/dev/null 2>&1 &
SERVER_PID=$!

# ─── Determine local IP ───────────────────────────────────────
MY_IP=$(ip -o -4 addr show wlan0 2>/dev/null | awk '{print $4}' | cut -d/ -f1)
[ -z "$MY_IP" ] && MY_IP="127.0.0.1"

LINK="http://$MY_IP:$PORT/output.html"

# ─── Display link ─────────────────────────────────────────────
echo -e "\n${GRN}🔗 Open this link in your browser:${RST}"
echo -e "${YEL}   $LINK${RST}\n"

# ─── Wait for user to stop ────────────────────────────────────
echo -ne "${CYN}⌨️  Press ENTER to stop the server …${RST}"
read -r   # Wait for Enter

# ─── Stop PHP server ──────────────────────────────────────────
kill "$SERVER_PID" >/dev/null 2>&1

echo -e "\n${GRN}✔ Server stopped. Bye!${RST}\n"

