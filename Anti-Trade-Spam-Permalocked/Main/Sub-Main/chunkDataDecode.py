from scapy.all import sniff, TCP, Raw
from scapy.sessions import TCPSession
import re

def parse_chunked_http(data: bytes) -> bytes:
    result = bytearray()
    while data:
        match = re.match(b'^([0-9a-fA-F]+)\r\n', data)
        if not match:
            break
        length = int(match.group(1), 16)
        i = match.end()
        chunk = data[i:i+length]
        result.extend(chunk)
        data = data[i+length+2:]  # Skip chunk + CRLF
        if length == 0:
            break
    return bytes(result)

def handle_stream(pkt_stream):
    payloads = []
    for pkt in pkt_stream:
        if pkt.haslayer(Raw):
            payloads.append(pkt[Raw].load)
    
    full_data = b"".join(payloads)
    
    if b"Transfer-Encoding: chunked" in full_data:
        print("[*] Detected chunked response")

        try:
            header_end = full_data.find(b"\r\n\r\n") + 4
            headers = full_data[:header_end]
            body = full_data[header_end:]
            decoded = parse_chunked_http(body)
            print("Decoded Body:\n", decoded.decode(errors="replace"))
        except Exception as e:
            print("Decode error:", e)

class HTTPChunkedSession(TCPSession):
    def on_session_close(self, session):
        handle_stream(session.packets)

print("[*] Sniffing packets... Ctrl+C to stop.")
sniff(
    filter="tcp port 80",
    prn=None,
    store=True,
    session=HTTPChunkedSession
)
