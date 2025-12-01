"""Online/continuous trainer for ENTERPRISE plan using LSTM fine-tuning."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.core.database import AsyncSessionLocal  # noqa: E402
from ml import utils  # noqa: E402
from ml.model_registry import get_latest_model_uri, register_model_version  # noqa: E402
from ml.train_enterprise_model import SYMBOL, INTERVAL, train_enterprise_model  # noqa: E402


def load_lstm_checkpoint(uri: str):
    payload = torch.load(uri, map_location="cpu")
    model = utils.SimpleLSTMClassifier(payload["input_dim"], payload.get("hidden_dim", 32))
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model, payload


def fine_tune(model: nn.Module, X: np.ndarray, y: np.ndarray, epochs: int = 2, lr: float = 5e-4) -> nn.Module:
    device = torch.device("cpu")
    dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long))
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            logits = model(xb.to(device))
            loss = criterion(logits, yb.to(device))
            loss.backward()
            optimizer.step()
    model.eval()
    return model


async def online_loop(max_cycles: int = 3, eval_interval: int = 1, register: bool = True) -> Tuple[Path, dict]:
    async with AsyncSessionLocal() as session:
        uri = await get_latest_model_uri("enterprise", db_session=session)
        if not uri:
            base_path, base_metrics = train_enterprise_model(register=register)
            uri = str(base_path)
        model, payload = load_lstm_checkpoint(uri)

        df = utils.load_ohlcv(SYMBOL, INTERVAL)
        features, target = utils.build_features_pro(df)
        features = features.fillna(0)
        seq_len = payload.get("seq_len", 20)
        feature_order = payload.get("feature_order", list(features.columns))

        best_metrics = payload.get("metrics") or {"sharpe": -1e9, "win_rate": 0}
        best_uri = uri

        for cycle in range(1, max_cycles + 1):
            # Simulate streaming by taking the most recent window
            stream_df = utils.recent_window(features.join(target.rename("target")), days=60 + 10 * cycle)
            X_seq = utils.make_sequence_data(stream_df[feature_order], seq_len=seq_len)
            y_seq = stream_df["target"].iloc[seq_len:].to_numpy()
            if len(y_seq) == 0:
                break

            model = fine_tune(model, X_seq, y_seq, epochs=2, lr=5e-4)

            if cycle % eval_interval == 0:
                preds = []
                with torch.no_grad():
                    logits = model(torch.tensor(X_seq, dtype=torch.float32))
                    preds = torch.argmax(logits, dim=1).cpu().numpy()
                returns = stream_df["log_return"].iloc[seq_len:]
                metrics = utils.compute_strategy_metrics(returns, preds)
                if metrics["sharpe"] > best_metrics.get("sharpe", -1e9):
                    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    model_path = utils.MODEL_DIR / f"enterprise_model_online_{SYMBOL}_{INTERVAL}_{timestamp}.pt"
                    torch.save(
                        {
                            "state_dict": model.state_dict(),
                            "input_dim": X_seq.shape[2],
                            "hidden_dim": 32,
                            "feature_order": feature_order,
                            "seq_len": seq_len,
                            "metrics": metrics,
                        },
                        model_path,
                    )
                    best_metrics = metrics
                    best_uri = str(model_path)
                    if register:
                        await register_model_version("enterprise", best_uri, metrics["sharpe"], metrics["win_rate"], session)

        return Path(best_uri), best_metrics


if __name__ == "__main__":
    path, metrics = asyncio.run(online_loop(max_cycles=3, eval_interval=1, register=True))
    print("Online enterprise model at", path)
    print("Metrics", metrics)
