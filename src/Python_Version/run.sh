#!/bin/bash

PATH_LENGTH=5
THRESHOLD=5
STTPS=20
MIXNODES=50
CLIENTS=1

VERBOSE=1

# Override defaults if provided
while getopts "p:t:m:s:c:v:" opt; do
  case $opt in
    p) PATH_LENGTH="$OPTARG" ;;
    t) THRESHOLD="$OPTARG" ;;
    m) MIXNODES="$OPTARG" ;;
    s) STTPS="$OPTARG" ;;
    c) CLIENTS="$OPTARG" ;;
    v) VERBOSE="$OPTARG" ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

export VERBOSE

# ==========================================
# KILL OLD PROCESSES
# ==========================================

pkill -f STTP/node.py
pkill -f Mixnode/main.py
pkill -f Client/main.py

# ==========================================
# CLEAN LOGS and config
# ==========================================

rm -rf .tmp
rm -rf .logs

mkdir -p .logs/sttp
mkdir -p .logs/mix
mkdir -p .logs/client

rm -f .config.json

# ==========================================
# GENERATE CONFIG
# ==========================================

python3 config.py --path_length $PATH_LENGTH --mixnodes $MIXNODES --sttps $STTPS --t $THRESHOLD || exit 1

# ==========================================
# START STTPS
# ==========================================

for ((i=1; i<=STTPS; i++))
do
    python3 STTP/node.py --id $i &
done

# ==========================================
# WAIT FOR STTP TO START
# ==========================================

while [ "$(ls .tmp/*.flag 2>/dev/null | wc -l)" -lt "$STTPS" ]; do
    sleep 0.1
done
rm -rf .tmp/*

# ==========================================
# START MIXNODES
# ==========================================

# echo "MIXNODES SETUP ..."
for ((i=1; i<=MIXNODES; i++))
do
    python3 Mixnode/main.py --id $i &
done

# ==========================================
# WAIT FOR END OF SETUP
# ==========================================

while [ "$(ls .tmp/*.flag 2>/dev/null | wc -l)" -lt "$MIXNODES" ]; do
    sleep 0.1
done
rm -rf .tmp

# ==========================================
# START Client
# ==========================================


# echo "RUNNING CLIENTS ..."
for ((i=1; i<=CLIENTS; i++))
do
    python3 Client/main.py --id $i #&
done

# ==========================================
# Automatically stop the script if no UDP activity is detected
# ==========================================

# touch /tmp/udp_activity
# tshark -l -i lo -f "udp port 5000" 2>/dev/null |
# sleep 0.1
# while read -r line; do
#     touch /tmp/udp_activity
# done &

# while true; do
#     last=$(stat -c %Y /tmp/udp_activity)
#     now=$(date +%s)

#     if (( now - last >= 3 )); then
#         # echo "No activity for 3 seconds - exiting..."

#         pkill -f STTP/node.py
#         pkill -f Mixnode/main.py
#         pkill -f Client/main.py
#         rm -f /tmp/udp_activity
        
#         sleep 0.1
#         exit 0
#     fi
#     sleep 1
# done
