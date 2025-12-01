import asyncio
from datetime import datetime

import torch

from app.core.database import AsyncSessionLocal
from ml import utils
from ml.model_registry import register_model_version

SYMBOL = "BTC-USD"
INTERVAL = "1d"


def train_enterprise_model(register: bool = True):
    """Enterprise model uses an LSTM classifier over sequential PRO features."""
    df = utils.load_ohlcv(SYMBOL, INTERVAL)
    features, target = utils.build_features_pro(df)
    features = features.fillna(0)
    feature_order = list(features.columns)

    seq_len = 20
    X_seq = utils.make_sequence_data(features, seq_len=seq_len)
    y_seq = target.iloc[seq_len:].to_numpy()

    model, preds = utils.train_lstm(X_seq, y_seq, feature_order, epochs=10, lr=1e-3)
    returns_series = features["log_return"].iloc[seq_len:]
    metrics = utils.compute_strategy_metrics(returns_series, preds)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    model_path = utils.MODEL_DIR / f"enterprise_model_{SYMBOL}_{INTERVAL}_{timestamp}.pt"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "input_dim": X_seq.shape[2],
            "hidden_dim": 32,
            "feature_order": feature_order,
            "seq_len": seq_len,
        },
        model_path,
    )

    if register:
        async def _register():
            async with AsyncSessionLocal() as session:
                await register_model_version("enterprise", str(model_path), metrics["sharpe"], metrics["win_rate"], session)

        asyncio.run(_register())

    return model_path, metrics


if __name__ == "__main__":
    path, metrics = train_enterprise_model(register=True)
    print("Saved ENTERPRISE model to", path)
    print("Validation metrics", metrics)
