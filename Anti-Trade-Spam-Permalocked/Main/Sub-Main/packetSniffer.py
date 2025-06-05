from scapy.all import sniff, Raw, IP


myCondition = {"ip": "52.223.44.23"}
# TODO: determine min/max and conditions to be considered a spammer
"todo: determine min/max, and condition to be considered spammer| work on the actual coding bit for determining when you are traded after entering trade"
def detect_spam_trade(interface="Ethernet 2", min_len=100, max_len=200, hex_pattern=b'\x68\x65\x6c\x6c\x6f'):
    """
    Sniffs packets on the network and looks for certain conditions in the raw packet data.
    
    Parameters:
    - min_len: Minimum packet length to check
    - max_len: Maximum packet length to check
    - hex_pattern: Specific byte sequence (in hexadecimal) to look for in the raw packet data
    """
    
    def packet_callback(pkt):
        # Check if the packet contains raw data (payload)
        if pkt.haslayer(Raw):
            raw_data = pkt[Raw].load  # Get the raw payload data
            ip = pkt[IP]
            packet_length = len(raw_data)  # Length of raw payload
            
            # Check if the packet length is within the specified range
            if min_len <= packet_length <= max_len:
                print(f"Packet length {packet_length} within range ({min_len}-{max_len})")

            # Check if the raw packet data contains the specified hex pattern
            if hex_pattern in raw_data:
                print(f"Hex pattern {hex_pattern} found in packet!")
                return True  # Return True if we find the pattern
            
    # Start sniffing the network for packets
    sniff(iface=interface, prn=packet_callback, filter="tcp", count=50)

# Call the function with your custom conditions
if myCondition:
if "ip" in myCondition:
    detect_spam_trade()
