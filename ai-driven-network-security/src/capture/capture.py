"""
Simple pcap reader and optional live capture.

Usage:
  # read pcap and export flows CSV
  python src/capture/capture.py --pcap data/sample_pcaps/sample.pcap --out data/processed/flows.csv

  # live capture for 10 seconds and save pcap
  python src/capture/capture.py --live 10 --save-pcap data/sample_pcaps/live_capture.pcap --out data/processed/flows.csv
"""
from scapy.all import rdpcap, sniff, IP, TCP, UDP, wrpcap
import argparse
import csv
import time
from collections import defaultdict
from tempfile import NamedTemporaryFile

def pcap_to_flows(pcap_path):
    packets = rdpcap(pcap_path)
    flows = defaultdict(list)  # key: (src, sport, dst, dport, proto)
    for pkt in packets:
        if IP not in pkt:
            continue
        ip = pkt[IP]
        proto = None
        sport = dport = None
        if TCP in pkt:
            proto = "TCP"
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
        elif UDP in pkt:
            proto = "UDP"
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
        else:
            proto = str(ip.proto)
            sport = 0
            dport = 0
        key = (ip.src, sport, ip.dst, dport, proto)
        ts = float(pkt.time)
        size = len(pkt)
        flows[key].append({"ts": ts, "size": size, "flags": getattr(getattr(pkt, 'payload', None), 'flags', None)})
    # convert to list of flow summaries
    flow_rows = []
    for (src, sport, dst, dport, proto), pkts in flows.items():
        start = min(p["ts"] for p in pkts)
        end = max(p["ts"] for p in pkts)
        duration = end - start
        total_bytes = sum(p["size"] for p in pkts)
        packet_count = len(pkts)
        avg_pkt_size = total_bytes / packet_count if packet_count else 0
        flow_rows.append({
            "src": src, "sport": sport, "dst": dst, "dport": dport,
            "proto": proto, "start": start, "end": end, "duration": duration,
            "total_bytes": total_bytes, "packet_count": packet_count, "avg_pkt_size": avg_pkt_size
        })
    return flow_rows

def write_csv(rows, out_path):
    if not rows:
        print("No flows extracted.")
        return
    keys = list(rows[0].keys())
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} flows to {out_path}")

def live_capture(seconds, save_pcap=None):
    print(f"Starting live capture for {seconds} seconds...")
    packets = sniff(timeout=seconds)
    print(f"Captured {len(packets)} packets.")
    if save_pcap:
        wrpcap(save_pcap, packets)
        print(f"Saved pcap to {save_pcap}")
    tmp = NamedTemporaryFile(delete=False, suffix=".pcap")
    wrpcap(tmp.name, packets)
    flows = pcap_to_flows(tmp.name)
    return flows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", help="Path to pcap file to read")
    parser.add_argument("--out", help="Output CSV for flows")
    parser.add_argument("--live", type=int, help="Live capture duration in seconds")
    parser.add_argument("--save-pcap", help="Save live capture to pcap")
    args = parser.parse_args()
    rows = []
    if args.pcap:
        rows = pcap_to_flows(args.pcap)
    elif args.live:
        rows = live_capture(args.live, save_pcap=args.save_pcap)
    else:
        parser.print_help()
        return
    if args.out:
        write_csv(rows, args.out)
    else:
        print("Sample flows:")
        for r in rows[:10]:
            print(r)

if __name__ == "__main__":
    main()
