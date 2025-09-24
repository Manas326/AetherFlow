"""
Load model and scaler, compute reconstruction error as anomaly score.
"""
import torch
import numpy as np
import pandas as pd

def load_scaler(mean_path, scale_path):
    mean = np.load(mean_path)
    scale = np.load(scale_path)
    return mean, scale

def compute_scores(model_obj, model_path, features_csv, mean_path, scale_path, device="cpu"):
    from src.models.autoencoder import Autoencoder
    df = pd.read_csv(features_csv)
    mean, scale = load_scaler(mean_path, scale_path)
    X = (df.values - mean) / scale
    X_tensor = torch.tensor(X.astype(np.float32)).to(device)
    model_instance = Autoencoder(input_dim=X.shape[1], latent_dim=min(3, X.shape[1]//2))
    model_instance.load_state_dict(torch.load(model_path, map_location=device))
    model_instance.to(device)
    model_instance.eval()
    with torch.no_grad():
        out = model_instance(X_tensor)
        mse = torch.mean((out - X_tensor) ** 2, dim=1).cpu().numpy()
    df_out = df.copy()
    df_out["anomaly_score"] = mse
    return df_out

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--features", required=True)
    parser.add_argument("--mean", required=True)
    parser.add_argument("--scale", required=True)
    parser.add_argument("--out", required=False)
    args = parser.parse_args()
    df = compute_scores(None, args.model, args.features, args.mean, args.scale)
    if args.out:
        df.to_csv(args.out, index=False)
    else:
        print(df.head())
