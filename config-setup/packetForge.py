from scapy.all import sniff, IP, TCP, Raw, send
import time
sport = 0
dport = 0 
flags = ""
ackLit = 0
seqLit = 0
SOURCE_IP = "35.71.175.214"  # Change this to your target source IP

def packet_callback(pkt):
    global sport, dport, flags, ackLit, seqLit
    if IP in pkt and TCP in pkt:
        ip = pkt[IP]
        tcp = pkt[TCP]
        payload = pkt[Raw].load.hex() if Raw in pkt else None
        #replayPacket(tcp.flags, tcp.seq, tcp.ack, tcp.sport, tcp.dport)
        ackLit = tcp.seq
        seqLit = tcp.ack
        dport = tcp.sport
        sport = tcp.dport
        flags = tcp.flags

def replayPacket():
    global sport, dport, flags, ackLit, seqLit
    if 0 != ackLit or 0 != seqLit or sport != 0 or dport != 0 or flags != "":
        payload = bytes.fromhex("d3000000f20730000a073531353734363812b5010a06536961776e61120f436c6572696323313133373839323622334c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f4e656f70687974655f4949492801380142334c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f4e656f70687974655f4949494a2c4c6561646572626f61726452616e6b446174613a49645f4c6561646572626f61726452616e6b5f43616465741a083233343635323434")
        ip = IP(src="192.168.1.133", dst=SOURCE_IP)
        tcp = TCP(sport=sport, dport=dport, seq=seqLit, ack=ackLit, flags=flags)
        print(f"Sport:{tcp.sport}Dport:{tcp.dport}")
        print(f"    Flags  : {flags}")
        print(f"    SEQ    : {seqLit}")
        print(f"    ACK    : {ackLit}")
        packet = ip / tcp / Raw(load=payload)
        send(packet)
        print("packet sent")
        sport = 0
        dport = 0
        flags = ""
        ackLit = 0
        seqLit = 0
    else:
        print("awaiting new tcp..")

# Capture only TCP packets from a specific source IP
sniff(filter=f"tcp and src host {SOURCE_IP}", prn=packet_callback, store=0)

while True:
    replayPacket()
    time.sleep(1)

