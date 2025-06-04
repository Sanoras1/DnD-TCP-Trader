from scapy.all import sniff, Raw

# Define your keyword to detect in decoded payloads
TARGET_KEYWORD = b"WlochatyMisPLr"

# Callback to process each packet
def packet_callback(pkt):
    if pkt.haslayer(Raw):
        raw_data = pkt[Raw].load
        if TARGET_KEYWORD in raw_data:
            print("[MATCH FOUND]")
            print(f"Raw Packet (hex): {raw_data.hex()}")
            try:
                decoded = raw_data.decode('utf-8', errors='ignore') 
                print(f"Decoded UTF-8: {decoded}")
            except:
                print("[!] Could not decode payload.")
            print("-" * 50)

# Start sniffing on your network interface (e.g., "Ethernet" or "Wi-Fi")
# You may need admin/root privileges to run this
sniff(iface="Ethernet 2", filter="tcp", prn=packet_callback, store=False)