#!/usr/bin/env python3
"""
live_tls_probe.py  –  Dark-and-Darker handshake inspector (live sniff)

Confirms whether the Dark-and-Darker ports are encrypted.

• Listens on TCP ports 20204 & 20206.
• As soon as it sees a TLS handshake, it reports:
    – whether TLS is in use at all
    – whether the server issues CertificateRequest  (mTLS demanded)
    – whether the client sends Certificate + CertificateVerify
• Exits automatically after the first handshake is decided, or on Ctrl-C.
"""

from scapy.all import sniff, AsyncSniffer, IP, TCP, Raw
import sys, asyncio

PORTS         = {20204, 20206}
TLS_CT_HAND   = 22          # 0x16 – TLS record: Handshake
HS_CERT_REQ   = 13
HS_CERT       = 11
HS_CERT_VERIFY= 15

class LiveProbe:
    def __init__(self):
        self.seen_tls   = False
        self.seen_creq  = False
        self.seen_ccert = False
        self.done_event = asyncio.Event()

    def _process(self, pkt):
        if IP not in pkt or TCP not in pkt or Raw not in pkt:
            return
        tcp, raw = pkt[TCP], pkt[Raw]

        if tcp.dport not in PORTS and tcp.sport not in PORTS:
            return

        # TLS record?
        if raw.load[0] != TLS_CT_HAND:
            return
        self.seen_tls = True

        # TLS 1.2/1.3 handshake type is byte 5 of the record header
        hs_type = raw.load[5]

        # Server → client  (sport in PORTS)
        if tcp.sport in PORTS and hs_type == HS_CERT_REQ:
            self.seen_creq = True

        # Client → server  (dport in PORTS)
        if tcp.dport in PORTS and hs_type in (HS_CERT, HS_CERT_VERIFY):
            self.seen_ccert = True

        # We can decide once we’ve seen at least the server Finished or  client CertVerify
        if hs_type in (HS_CERT_VERIFY, 20):           # 20 = Finished
            self.done_event.set()

async def main():
    probe = LiveProbe()
    bpf = "tcp and (" + " or ".join(f"port {p}" for p in PORTS) + ")"
    sniffer = AsyncSniffer(filter=bpf, prn=probe._process, store=False)
    sniffer.start()
    print(f"sniffing on: {bpf}  (Ctrl-C to abort)\n")
    try:
        await asyncio.wait_for(probe.done_event.wait(), timeout=20)
    except asyncio.TimeoutError:
        print("✖ timeout—no TLS handshake observed on those ports.")
    finally:
        sniffer.stop()

    print("\nRESULTS")
    print("TLS in use?            ", probe.seen_tls)
    print("Server wants mTLS?     ", probe.seen_creq)
    print("Client sent certificate?", probe.seen_ccert)

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        print("⚠ needs admin & Npcap\n")
    asyncio.run(main())