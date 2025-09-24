"""
Train autoencoder on features CSV.
Saves a model file and scaler mean/scale as numpy files (scaler_mean.npy, scaler_scale.npy).
"""
import argparse
import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
import os

def train_loop(model, dataloader, epochs=30, lr=1e-3, device="cpu"):
    model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()
    model.train()
    for epoch in range(epochs):
        total = 0.0
        for xb in dataloader:
            xb = xb[0].to(device)
            out = model(xb)
            loss = loss_fn(out, xb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * xb.size(0)
        avg = total / len(dataloader.dataset)
        if epoch % 5 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch+1}/{epochs} loss={avg:.6f}")
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch", type=int, default=32)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    scaler = StandardScaler()
    X = scaler.fit_transform(df.values.astype(np.float32))
    out_dir = os.path.dirname(args.out) or '.'
    os.makedirs(out_dir, exist_ok=True)
    # save scaler mean and scale
    np.save(os.path.join(out_dir, "scaler_mean.npy"), scaler.mean_)
    np.save(os.path.join(out_dir, "scaler_scale.npy"), scaler.scale_)
    X_tensor = torch.tensor(X)
    ds = TensorDataset(X_tensor)
    loader = DataLoader(ds, batch_size=args.batch, shuffle=True)
    # import here to avoid package issues
    from src.models.autoencoder import Autoencoder
    model = Autoencoder(input_dim=X.shape[1], latent_dim=min(3, X.shape[1]//2))
    model = train_loop(model, loader, epochs=args.epochs)
    torch.save(model.state_dict(), args.out)
    print("Model saved to", args.out)

if __name__ == "__main__":
    main()
