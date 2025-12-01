import asyncio
from datetime import datetime
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit

from app.core.database import AsyncSessionLocal
from ml import utils
from ml.model_registry import register_model_version

SYMBOL = "BTC-USD"
INTERVAL = "1d"


def train_free_model(register: bool = True):
    df = utils.load_ohlcv(SYMBOL, INTERVAL)
    features, target = utils.build_features_free(df)
    tscv = TimeSeriesSplit(n_splits=4)
    best_model = None
    best_metrics = {"sharpe": -1e9}
    feature_order = list(features.columns)

    for train_idx, test_idx in tscv.split(features):
        X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
        y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]
        model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = utils.compute_strategy_metrics(X_test["log_return"], preds)
        if metrics["sharpe"] > best_metrics.get("sharpe", -1e9):
            best_model = model
            best_metrics = metrics

    # Refit on all data
    best_model.fit(features, target)
    split_idx = int(len(features) * 0.8)
    X_val = features.iloc[split_idx:]
    y_val = target.iloc[split_idx:]
    val_preds = best_model.predict(X_val)
    val_metrics = utils.compute_strategy_metrics(X_val["log_return"], val_preds)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    model_path = utils.MODEL_DIR / f"free_signal_model_{SYMBOL}_{INTERVAL}_{timestamp}.pkl"
    utils.save_model(best_model, model_path, feature_order, extra={"metrics": val_metrics})

    if register:
        async def _register():
            async with AsyncSessionLocal() as session:
                await register_model_version("free", str(model_path), val_metrics["sharpe"], val_metrics["win_rate"], session)

        asyncio.run(_register())

    return model_path, val_metrics


if __name__ == "__main__":
    path, metrics = train_free_model(register=True)
    print("Saved FREE model to", path)
    print("Validation metrics", metrics)
