#!/usr/bin/env python3
"""
Scan a Dark-and-Darker pcap for:
  • the first login request (just printed so you can confirm it)
  • every trade-accept packet whose payload starts with '^'
    – write the partner names to names.txt
"""

from pathlib import Path
from scapy.all import PcapReader, TCP, Raw
import argparse, re, itertools

TRADE_PORTS = {20204, 20206}          # server → client
CARET       = 0x5E                    # '^'

def guess_name(payload: bytes) -> str | None:
    """
    Very light-weight decoder:
    • caret
    • 1-byte length
    • UTF-8 display name
    (You can tighten this if you know the exact protobuf schema.)
    """
    if len(payload) < 2 or payload[0] != CARET:
        return None
    name_len = payload[1]
    if 2 + name_len > len(payload):
        return None
    try:
        return payload[2:2 + name_len].decode("utf-8")
    except UnicodeDecodeError:
        return None

def main(pcap_path: Path, names_out: Path):
    names = set()
    login_shown = False

    with PcapReader(str(pcap_path)) as cap:
        for pkt in cap:
            if TCP not in pkt or Raw not in pkt:
                continue
            tcp, raw = pkt[TCP], pkt[Raw]
            sport, dport = tcp.sport, tcp.dport

            # 1  First-seen login (client → server, your creds inside)
            if not login_shown and dport in TRADE_PORTS:
                print("=== First login payload (hex) ===")
                print(raw.load.hex())
                print("=== /login ===")
                login_shown = True
                continue

            # 2  Trade-accept from server → you
            if sport in TRADE_PORTS and raw.load and raw.load[0] == CARET:
                name = guess_name(raw.load)
                if name:
                    names.add(name)

    if names:
        names_out.write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")
        print(f"[+] Wrote {len(names)} unique partner names → {names_out}")
    else:
        print("[-] No trade-accept packets with caret found.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pcap",      type=Path, help="darkndarkeripinfo.pcapng")
    ap.add_argument("--out",     type=Path, default=Path("names.txt"))
    args = ap.parse_args()

    main(args.pcap, args.out)