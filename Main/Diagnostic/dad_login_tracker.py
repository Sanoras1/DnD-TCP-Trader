#!/usr/bin/env python3
"""
tcp_login_monitor.py  —  auto-discovers the first login frame and shows a
single-line timer:  awaiting login…..NN seconds
"""

import argparse, sys, time, threading
from pathlib import Path
from scapy.all import sniff, IP, TCP, Raw

DEFAULT_PORTS = {20204, 20206}

# ──────────────────────────────────────────────────────────────────────────── #
class Tracker:
    def __init__(self, server_ips, ports, login_out):
        self.server_ips  = set(server_ips)      # may start empty
        self.ports       = set(ports)
        self.login_out   = login_out
        self.login_seen  = False
        self.state       = {}                   # flow-key → (seq, ack, flags)

    def __call__(self, pkt):
        if IP not in pkt or TCP not in pkt or Raw not in pkt:
            return
        ip, tcp, raw = pkt[IP], pkt[TCP], pkt[Raw]

        cli2srv = (ip.src, tcp.sport, ip.dst, tcp.dport)
        srv2cli = (ip.dst, tcp.dport, ip.src, tcp.sport)
        self.state[cli2srv] = (tcp.seq, tcp.ack, tcp.flags)
        self.state[srv2cli] = (tcp.ack, tcp.seq, tcp.flags)

        if self.login_seen:            # timer already stopped
            return

        is_login_port = tcp.dport in self.ports
        is_ok_ip      = not self.server_ips or ip.dst in self.server_ips
        if is_login_port and is_ok_ip and raw.load:
            self.login_seen = True
            if not self.server_ips:        # auto-discover destination IP
                self.server_ips.add(ip.dst)

            # clear timer line
            print("\r" + " " * 40 + "\r", end="", flush=True)

            print("=== FIRST LOGIN PAYLOAD (hex) ===")
            print(raw.load.hex())
            print("=================================")
            if self.login_out:
                Path(self.login_out).write_bytes(raw.load)
                print(f"[+] saved login payload → {self.login_out}")

# ──────────────────────────────────────────────────────────────────────────── #
def start_timer(tracker: Tracker):
    """Prints 'awaiting login…NN seconds' on one line until login is found."""
    start = time.monotonic()
    while not tracker.login_seen:
        elapsed = int(time.monotonic() - start)
        print(f"\rawaiting login…{elapsed:>4} seconds", end="", flush=True)
        time.sleep(1)
    # ensure the line is cleared once login appears
    print("\r" + " " * 40 + "\r", end="", flush=True)

# ──────────────────────────────────────────────────────────────────────────── #
def main():
    ap = argparse.ArgumentParser(description="Live-sniff Dark-and-Darker login")
    ap.add_argument("--server-ips",
                    help="comma-separated server IP list (optional)")
    ap.add_argument("--ports",
                    default="20204,20206",
                    help="comma-separated TCP ports; default 20204,20206")
    ap.add_argument("--login-out",
                    help="file to save captured login payload")
    args = ap.parse_args()

    ports     = {int(p) for p in args.ports.split(",") if p.strip()}
    server_ips = {ip.strip() for ip in args.server_ips.split(",")} if args.server_ips else set()

    tracker = Tracker(server_ips, ports, args.login_out)

    port_filter = " or ".join(f"port {p}" for p in ports)
    bpf = f"tcp and ({port_filter})"

    print(f"[•] sniffing on: {bpf}")
    if server_ips:
        print(f"[•] limiting to server IPs: {', '.join(server_ips)}")
    else:
        print("[•] auto-discovering server IP from first login packet")

    # launch the timer thread
    t = threading.Thread(target=start_timer, args=(tracker,), daemon=True)
    t.start()

    try:
        sniff(filter=bpf, prn=tracker, store=False)
    except KeyboardInterrupt:
        pass
    finally:
        tracker.login_seen = True        # ensure timer thread stops
        t.join()

        print("\n[✓] stopped.  tracked flows:")
        for (cli, cport, srv, sport), (seq, ack, flg) in tracker.state.items():
            if (cli, cport) < (srv, sport):   # show each dir once
                print(f"  {cli}:{cport} ⇄ {srv}:{sport}   seq={seq} ack={ack} flags={flg}")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        print("⚠  Live sniffing on Windows needs Npcap + admin rights.")
    main()