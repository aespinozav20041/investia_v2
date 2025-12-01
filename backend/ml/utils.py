from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Tuple

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit
from torch import nn

DATA_DIR = Path(__file__).resolve().parent / "data"
MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class SimpleLSTMClassifier(nn.Module):
    """Small LSTM classifier for sequence-based enterprise model."""

    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Linear(32, 2))

    def forward(self, x):
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last)


def load_ohlcv(symbol: str = "BTC-USD", interval: str = "1d") -> pd.DataFrame:
    """Load OHLCV from csv in data folder; fallback to synthetic data."""
    path = DATA_DIR / f"{symbol.replace('/', '-')}_{interval}.csv"
    if not path.exists():
        path = DATA_DIR / "sample_prices.csv"
    if not path.exists():
        # synthetic fallback
        dates = pd.date_range(end=pd.Timestamp.today(), periods=300, freq="D")
        prices = [100]
        volumes = []
        for _ in range(1, len(dates)):
            prices.append(max(30, prices[-1] * (1 + np.random.normal(0, 0.01))))
            volumes.append(np.random.randint(800, 2000))
        df = pd.DataFrame({"date": dates, "close": prices, "volume": volumes + [volumes[-1]]})
        return df
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    df = df.rename(columns={c: c.lower() for c in df.columns})
    if "close" not in df.columns:
        raise ValueError("Dataframe must include close column")
    if "volume" not in df.columns:
        df["volume"] = 1_000
    return df.reset_index(drop=True)


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(com=window - 1, adjust=False).mean()
    ma_down = down.ewm(com=window - 1, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def build_features_free(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df["log_return"] = np.log(df["close"]).diff().fillna(0)
    df["volatility_10"] = df["log_return"].rolling(10).std().fillna(0)
    df["ma_fast"] = df["close"].rolling(10).mean().fillna(method="bfill")
    df["ma_slow"] = df["close"].rolling(30).mean().fillna(method="bfill")
    df["ma_ratio"] = (df["ma_fast"] / df["ma_slow"]).replace([np.inf, -np.inf], 1).fillna(1)
    df["rsi_14"] = compute_rsi(df["close"], 14)
    target = (df["close"].shift(-1) > df["close"]).astype(int)
    features = df[["log_return", "volatility_10", "ma_ratio", "rsi_14"]].copy()
    target = target.fillna(0)
    return features, target


def build_features_pro(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df["log_return"] = np.log(df["close"]).diff().fillna(0)
    df["volatility_10"] = df["log_return"].rolling(10).std().fillna(0)
    df["volatility_20"] = df["log_return"].rolling(20).std().fillna(0)
    df["volatility_50"] = df["log_return"].rolling(50).std().fillna(0)
    df["ma_fast"] = df["close"].rolling(10).mean().fillna(method="bfill")
    df["ma_mid"] = df["close"].rolling(20).mean().fillna(method="bfill")
    df["ma_slow"] = df["close"].rolling(50).mean().fillna(method="bfill")
    df["ma_ratio"] = (df["ma_fast"] / df["ma_slow"]).replace([np.inf, -np.inf], 1).fillna(1)
    df["rsi_14"] = compute_rsi(df["close"], 14)
    df["volume_zscore"] = ((df["volume"] - df["volume"].rolling(20).mean()) / (df["volume"].rolling(20).std() + 1e-9)).fillna(0)
    df["sentiment_score"] = df.get("sentiment", pd.Series(0, index=df.index)).fillna(0)
    df["price_spread"] = (df["close"] - df["close"].rolling(5).min()) / (df["close"].rolling(5).max() - df["close"].rolling(5).min() + 1e-9)
    target = (df["close"].shift(-1) > df["close"]).astype(int)
    features = df[
        [
            "log_return",
            "volatility_10",
            "volatility_20",
            "volatility_50",
            "ma_ratio",
            "rsi_14",
            "volume_zscore",
            "price_spread",
            "sentiment_score",
        ]
    ].copy()
    target = target.fillna(0)
    return features, target


def compute_strategy_metrics(returns: Iterable[float], y_pred: Iterable[int]) -> dict:
    returns = np.array(list(returns))
    y_pred = np.array(list(y_pred))
    pnl_series = returns * y_pred
    pnl = float(np.prod(1 + pnl_series) - 1.0)
    mean_ret = pnl_series.mean()
    std_ret = pnl_series.std() + 1e-9
    sharpe = float((mean_ret / std_ret) * math.sqrt(252)) if std_ret > 0 else 0.0
    win_rate = float(np.mean(pnl_series > 0)) if len(pnl_series) else 0.0
    n_trades = int(np.sum(y_pred != 0))
    return {"pnl": pnl, "sharpe": sharpe, "win_rate": win_rate, "n_trades": n_trades}


def evaluate_predictions(y_true: Iterable[int], y_pred: Iterable[int], returns: Iterable[float]) -> dict:
    y_true = np.array(list(y_true))
    y_pred = np.array(list(y_pred))
    returns = np.array(list(returns))
    pnl = float(np.sum(y_pred * returns))
    win_rate = float(np.mean((y_pred == 1) & (returns > 0))) if len(y_pred) else 0
    sharpe = float(np.mean(returns * y_pred) / (np.std(returns * y_pred) + 1e-9)) if len(y_pred) else 0
    acc = float(accuracy_score(y_true, y_pred)) if len(y_pred) else 0
    metrics = compute_strategy_metrics(returns, y_pred)
    metrics.update({"accuracy": acc, "pnl_sum": pnl})
    return metrics


def save_model(obj, path: Path, feature_order: list[str], extra: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model": obj, "feature_order": feature_order}
    if extra:
        payload.update(extra)
    joblib.dump(payload, path)
    return path


def train_lstm(X: np.ndarray, y: np.ndarray, feature_order: list[str], epochs: int = 5, lr: float = 1e-3):
    device = torch.device("cpu")
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
    y_tensor = torch.tensor(y, dtype=torch.long).to(device)
    model = SimpleLSTMClassifier(input_dim=X.shape[2], hidden_dim=32)
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for _ in range(epochs):
        model.train()
        optimizer.zero_grad()
        logits = model(X_tensor)
        loss = criterion(logits, y_tensor)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        preds = torch.argmax(model(X_tensor), dim=1).cpu().numpy()
    return model, preds


def time_series_cv(model_builder, X: pd.DataFrame, y: pd.Series, n_splits: int = 4):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    best_model = None
    best_metrics = None
    feature_order = list(X.columns)
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        model = model_builder()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = evaluate_predictions(
            y_test, preds, returns=X["log_return"].iloc[test_idx] if "log_return" in X else np.zeros_like(preds)
        )
        if not best_metrics or metrics["sharpe"] > best_metrics["sharpe"]:
            best_model = model
            best_metrics = metrics
    return best_model, best_metrics or {"pnl": 0, "win_rate": 0, "sharpe": 0, "accuracy": 0}, feature_order


def make_sequence_data(X: pd.DataFrame, seq_len: int = 20) -> np.ndarray:
    arr = X.to_numpy(dtype=np.float32)
    sequences = []
    for i in range(len(arr) - seq_len):
        sequences.append(arr[i : i + seq_len])
    return np.stack(sequences)


def recent_window(df: pd.DataFrame, days: int = 60) -> pd.DataFrame:
    if "date" not in df.columns:
        return df.tail(days)
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff]
