"""
Flask dashboard:
- index: shows model health and recent alerts
- /run_inference: endpoint to run inference on features and save alerts over threshold
- /alerts: API to fetch recent alerts
"""
from flask import Flask, render_template, jsonify, request
import os
from src.db.db import init_db, get_recent, insert_alert
from src.models.inference import compute_scores
import threading
import json

app = Flask(__name__, template_folder="templates")

MODEL_PATH = os.environ.get("MODEL_PATH", "out/model.pth")
MEAN_PATH = os.environ.get("MEAN_PATH", "out/scaler_mean.npy")
SCALE_PATH = os.environ.get("SCALE_PATH", "out/scaler_scale.npy")
FEATURES_CSV = os.environ.get("FEATURES_CSV", "data/processed/features.csv")
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "0.01"))

@app.route("/")
def index():
    init_db()
    alerts = get_recent(50)
    return render_template("index.html", alerts=alerts, model_path=MODEL_PATH, threshold=ANOMALY_THRESHOLD)

@app.route("/run_inference", methods=["POST"])
def run_inference():
    def job():
        # compute scores and write alerts for those above threshold
        try:
            df = compute_scores(None, MODEL_PATH, FEATURES_CSV, MEAN_PATH, SCALE_PATH)
        except Exception as e:
            print("Inference error:", e)
            return
        flagged = df[df["anomaly_score"] > ANOMALY_THRESHOLD]
        for _, r in flagged.iterrows():
            src = r.get("src", "n/a") if "src" in r else "n/a"
            dst = r.get("dst", "n/a") if "dst" in r else "n/a"
            proto = r.get("proto", "n/a") if "proto" in r else "n/a"
            insert_alert(src=src, dst=dst, proto=proto, score=float(r["anomaly_score"]), metadata=json.dumps(r.dropna().to_dict()))
    t = threading.Thread(target=job)
    t.start()
    return jsonify({"status": "running"}), 202

@app.route("/alerts")
def alerts_api():
    alerts = get_recent(200)
    return jsonify([{
        "id": r[0], "ts": r[1], "src": r[2], "dst": r[3], "proto": r[4], "score": r[5], "metadata": r[6]
    } for r in alerts])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
