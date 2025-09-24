Design notes:
- Flow extraction groups by 5-tuple.
- Features are flow-level; model learns normal flows via autoencoder.
- Anomaly detection via reconstruction error; threshold set by percentile or manual tuning.
- Explainability: use SHAP KernelExplainer on a small subset to show which features contributed to high reconstruction error.
- Response hooks: add scripts that call iptables or trigger external workflows (not included by default for safety).
