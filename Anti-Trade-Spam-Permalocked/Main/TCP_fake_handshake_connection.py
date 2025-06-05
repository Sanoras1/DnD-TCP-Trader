from scapy.all import sniff, IP, TCP, Raw, send
import time

SOURCE_IP = "52.223.44.23"  # target to watch
MY_IP = "192.168.1.133"      # your IP

stop_sniffing = False
tcp_state = {}  # (src, sport, dst, dport) => (seq, ack, flags)

# Use this to track TCP flow state
def packet_callback(pkt):
    if IP in pkt and TCP in pkt:
        ip = pkt[IP]
        tcp = pkt[TCP]
        key = (ip.src, tcp.sport, ip.dst, tcp.dport)
        seq = tcp.seq
        ack = tcp.ack
        flags = tcp.flags
        tcp_state[key] = (seq, ack, flags)
        print(f"[Captured] {key} | SEQ={seq} ACK={ack} FLAGS={flags}")

# Use this to safely replay packets using stored TCP state
def replay_packet():
    for (src, sport, dst, dport), (seq, ack, flags) in tcp_state.items():
        if src == SOURCE_IP and dst == MY_IP:
            payload = bytes.fromhex("d7000000f20728000a073537353039323912b9010a074c656f6e4a7567121242617262617269616e23313139393431363122334c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f4e656f70687974655f4949492801380142334c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f4e656f70687974655f4949494a2c4c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f43616465741a083233363036333736")
            ip = IP(src=MY_IP, dst=src)
            tcp = TCP(sport=dport, dport=sport, seq=ack, ack=seq, flags=flags)

            packet = ip / tcp / Raw(load=payload)

            print(f"[Replay] SEQ={tcp.seq} ACK={tcp.ack} Flags={tcp.flags}")
            decoded = payload.decode(errors="ignore")
            if not decoded.startswith("^"):
                send(packet)
    print("No matching flow to replay")

def sniff_packets():
    sniff(filter=f"tcp and src host {SOURCE_IP}", prn=packet_callback, store=0, stop_filter=lambda _: stop_sniffing)

import threading
sniffer_thread = threading.Thread(target=sniff_packets)
sniffer_thread.start()

try:
    while True:
        replay_packet()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[!] KeyboardInterrupt: stopping...")
    stop_sniffing = True
    sniffer_thread.join()
    print("[+] Exited cleanly.")
