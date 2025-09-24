# AI-Driven Network Security

An end-to-end demo of capturing network traffic, extracting features, training an autoencoder-based anomaly detector, and visualizing results in a Flask dashboard.

## QuickStart (local)

1. Create virtualenv \& install:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
2. Capture (pcap read):
   python src/capture/capture.py --pcap data/sample\_pcaps/sample.pcap --out data/processed/flows.csv
3. Extract features:
   python src/preprocessing/features.py --in data/processed/flows.csv --out data/processed/features.csv
4. Train:
   mkdir -p out
   python src/models/train.py --data data/processed/features.csv --out out/model.pth --epochs 30
5. Run dashboard:
   export MODEL\_PATH=out/model.pth
   export MEAN\_PATH=out/scaler\_mean.npy
   export SCALE\_PATH=out/scaler\_scale.npy
   export FEATURES\_CSV=data/processed/features.csv
   python src/web/app.py
   Open http://localhost:5000

## Notes

* This repo is for learning and demo purposes. Do not run automated blocking actions on production or public networks.
* Add real PCAPs to data/sample\_pcaps/ before running the capture->features steps.
