import pandas as pd
from src.preprocessing.features import extract_features

def test_extract_features_basic():
    df = pd.DataFrame([{
        "src":"1.1.1.1","sport":1234,"dst":"2.2.2.2","dport":80,"proto":"TCP",
        "start":0,"end":1,"duration":1,"total_bytes":1000,"packet_count":4,"avg_pkt_size":250
    }])
    features, cols = extract_features(df)
    assert "duration" in features.columns
    assert features.shape[0] == 1
