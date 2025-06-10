#!/usr/bin/env python3
"""
dad_login_tracker.py  –  passive Dark-and-Darker login catcher
--------------------------------------------------------------
• Works on Windows (Npcap) and Unix.  No asyncio, no signal headaches.
• Shows “waiting for login… NN s” on ONE console line.
• Writes the first login payload to login.bin.
• Keeps a flow table so later tools can reuse seq/ack/flags.

Usage
-----
# list interfaces once to find the right NIC number
python dad_login_tracker.py --list

# start tracking on that interface (example uses 7)
python dad_login_tracker.py --iface 7
"""

import argparse, time, sys
from pathlib import Path
from threading import Event
from scapy.all import AsyncSniffer, IP, TCP, Raw, conf

PORTS        = {20204, 20206}
LOGIN_MAGIC  = b"\xBA\x06\x00\x00"   # little-endian 0x06BA = LoginRequest

def is_login(payload: bytes) -> bool:
    return payload.startswith(LOGIN_MAGIC)

class Tracker:
    def __init__(self, out_path: Path):
        self.out_path   = out_path
        self.login_seen = Event()
        self.flows      = {}   # (cli,cp,srv,sp) -> (seq,ack,flags)

    def packet_cb(self, pkt):
        if IP not in pkt or TCP not in pkt or Raw not in pkt:
            return
        ip, tcp, raw = pkt[IP], pkt[TCP], pkt[Raw]
        if tcp.dport not in PORTS and tcp.sport not in PORTS:
            return

        self.flows[(ip.src, tcp.sport, ip.dst, tcp.dport)] = (tcp.seq, tcp.ack, tcp.flags)
        self.flows[(ip.dst, tcp.dport, ip.src, tcp.sport)] = (tcp.ack, tcp.seq, tcp.flags)

        if (not self.login_seen.is_set()
            and tcp.dport in PORTS
            and is_login(raw.load)):
            print("\n=== LOGIN PAYLOAD (hex) ===")
            print(raw.load.hex())
            print("===========================\n")
            self.out_path.write_bytes(raw.load)
            print(f"[+] saved to {self.out_path}\n")
            self.login_seen.set()

def list_ifaces_and_exit():
    print("\nAvailable interfaces:")
    for iface in conf.ifaces.values():
        print(f"  {iface.index}: {iface.name}  ({iface.description})")
    sys.exit(0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iface", help="interface index or name")
    ap.add_argument("--list", action="store_true", help="show NIC list and exit")
    ap.add_argument("--out", default="login.bin", help="file to dump login payload")
    args = ap.parse_args()

    if args.list:
        list_ifaces_and_exit()

    iface = args.iface or conf.iface
    out_path = Path(args.out)
    tracker = Tracker(out_path)

    bpf = "tcp and (" + " or ".join(f"port {p}" for p in PORTS) + ")"
    print(f"[•] sniffing on «{iface}»: {bpf}")
    print("    Ctrl-C to stop.\n")

    sniffer = AsyncSniffer(iface=iface, filter=bpf, prn=tracker.packet_cb, store=False)
    sniffer.start()
    # one-line timer loop
    start = time.time()
    try:
        while not tracker.login_seen.wait(timeout=1):
            elapsed = int(time.time() - start)
            print(f"\rwaiting for login… {elapsed:>4}s", end='', flush=True)
    except KeyboardInterrupt:
        pass

    # clear timer line
    print("\r" + " " * 40 + "\r", end='', flush=True)
    sniffer.stop()

    print("\n[✓] stopped.  tracked flows:")
    for (cli, cport, srv, sport), (seq, ack, flg) in tracker.flows.items():
        if (cli, cport) < (srv, sport):  # show each direction once
            print(f"  {cli}:{cport} ⇄ {srv}:{sport}  seq={seq} ack={ack} flags={flg}")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        print("⚠  Run PowerShell as Administrator (Npcap required).")
    main()