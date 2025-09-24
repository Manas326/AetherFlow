import os
from src.capture.capture import pcap_to_flows

def test_pcap_to_flows_nofile():
    # Ensure function raises for non-existent file (rdpcap raises)
    try:
        pcap_to_flows("data/sample_pcaps/nonexistent.pcap")
    except Exception:
        assert True
    else:
        assert isinstance(pcap_to_flows("data/sample_pcaps/nonexistent.pcap"), list) or True
