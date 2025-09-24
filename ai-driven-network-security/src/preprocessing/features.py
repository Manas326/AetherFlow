"""
Convert flow CSV -> feature CSV for model training.

Features included (per flow):
- duration
- packet_count
- total_bytes
- avg_pkt_size
- bytes_per_sec
- packets_per_sec
- proto_num
"""
import argparse
import pandas as pd
import numpy as np

def load_flows(path):
    return pd.read_csv(path)

def extract_features(df):
    df = df.copy()
    # basic features
    df["bytes_per_sec"] = df["total_bytes"] / (df["duration"].replace(0, np.nan))
    df["bytes_per_sec"] = df["bytes_per_sec"].fillna(df["total_bytes"])  # for 0 duration
    df["pkts_per_sec"] = df["packet_count"] / (df["duration"].replace(0, np.nan))
    df["pkts_per_sec"] = df["pkts_per_sec"].fillna(df["packet_count"])
    # proto encoding (simple)
    df["proto_num"] = df["proto"].map({"TCP": 1, "UDP": 2}).fillna(0)
    feat_cols = ["duration", "packet_count", "total_bytes", "avg_pkt_size", "bytes_per_sec", "pkts_per_sec", "proto_num"]
    features = df[feat_cols].copy()
    return features, feat_cols

def save_features(features, out_path):
    features.to_csv(out_path, index=False)
    print(f"Saved features to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inpath", required=True)
    parser.add_argument("--out", dest="outpath", required=True)
    args = parser.parse_args()
    df = load_flows(args.inpath)
    features, cols = extract_features(df)
    save_features(features, args.outpath)

if __name__ == "__main__":
    main()
