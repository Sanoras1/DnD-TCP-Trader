#!/usr/bin/env python3
"""
TCP_fake_handshake_connection.py
────────────────────────────────
• Sniffs TCP packets from one of several SOURCE_IPs arriving on SOURCE_PORT.
• For every packet, forges a reply containing a personalised payload built
  from a rotating list of names read from disk.
• Sends the forged reply once per second.

HOW TO RUN
----------
python3 TCP_fake_handshake_connection.py \
        --name-file names.txt \
        --source-ips 52.223.44.23,35.71.175.214 \
        --port 20204
"""

import argparse, itertools, threading, time
from pathlib import Path
from scapy.all import sniff, send, IP, TCP, Raw

###############################################################################
# 1. Helpers
###############################################################################

def iter_names(path: Path):
    """Yield names forever in round-robin order."""
    names = [n.strip() for n in path.read_text().splitlines() if n.strip()]
    if not names:
        raise ValueError(f"{path} is empty")
    return itertools.cycle(names)

BASE_TEMPLATE = bytes.fromhex(
    #   ... untouched prefix …
    "d7000000f20728000a07"            #    <- header
    "{name_hex}"                      #    <- we’ll splice the encoded name here
    "12b9010a074c656f6e4a7567"        #    <- rest of the message
    #   ^^^^^^^ dummy bytes – leave as-is unless you know the protocol
)

def build_payload(name: str) -> bytes:
    """Return a protobuf-ish payload with the name encoded as length-prefixed."""
    name_bytes = name.encode("utf-8")
    length_byte = len(name_bytes).to_bytes(1, "big")
    name_hex = (length_byte + name_bytes).hex()
    return bytes.fromhex(BASE_TEMPLATE.replace("{name_hex}", name_hex))

###############################################################################
# 2. Packet logic
###############################################################################

class FakeTCPResponder:
    def __init__(self, ips, port, name_iter):
        self.allowed_ips = set(ips)
        self.port = port
        self.name_iter = name_iter
        self.state = {}          # flow-key -> (seq, ack, flags)

    def packet_callback(self, pkt):
        if IP in pkt and TCP in pkt:
            ip, tcp = pkt[IP], pkt[TCP]
            if ip.src in self.allowed_ips and tcp.sport == self.port:
                key = (ip.src, tcp.sport, ip.dst, tcp.dport)
                self.state[key] = (tcp.seq, tcp.ack, tcp.flags)

    def replay_once(self):
        for (src, sport, dst, dport), (seq, ack, flags) in list(self.state.items()):
            name = next(self.name_iter)
            payload = build_payload(name)
            forged = IP(src=dst, dst=src) / \
                     TCP(sport=dport, dport=sport, seq=ack, ack=seq, flags=flags) / \
                     Raw(load=payload)
            forged = forged.__class__(bytes(forged))  # recompute checksums
            send(forged, verbose=False)
            print(f"[SEND] to {src}:{sport}  name={name}")

###############################################################################
# 3. Main
###############################################################################

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name-file",  required=True, type=Path)
    ap.add_argument("--source-ips", required=True,
                    help="comma-separated list, e.g. 52.223.44.23,35.71.175.214")
    ap.add_argument("--port",       default=20204, type=int)
    args = ap.parse_args()

    names = iter_names(args.name_file)
    ips   = [ip.strip() for ip in args.source_ips.split(",") if ip.strip()]
    responder = FakeTCPResponder(ips, args.port, names)

    stop = threading.Event()
    thread = threading.Thread(
        target=lambda: sniff(
            filter=f"tcp and src port {args.port} and (" +
                   " or ".join(f"src host {ip}" for ip in ips) + ")",
            prn=responder.packet_callback,
            store=False,
            stop_filter=lambda _: stop.is_set()),
        daemon=True)
    thread.start()

    try:
        while True:
            responder.replay_once()
            time.sleep(1)
    except KeyboardInterrupt:
        stop.set()
        thread.join()
        print("\n[!] Exiting cleanly.")

if __name__ == "__main__":
    main()