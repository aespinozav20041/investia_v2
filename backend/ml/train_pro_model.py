import asyncio
from datetime import datetime

import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

from app.core.database import AsyncSessionLocal
from ml import utils
from ml.model_registry import register_model_version

SYMBOL = "BTC-USD"
INTERVAL = "1d"


def train_pro_model(register: bool = True):
    df = utils.load_ohlcv(SYMBOL, INTERVAL)
    features, target = utils.build_features_pro(df)
    tscv = TimeSeriesSplit(n_splits=4)
    best_model = None
    best_metrics = {"sharpe": -1e9}
    feature_order = list(features.columns)

    for train_idx, test_idx in tscv.split(features):
        X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
        y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]
        model = xgb.XGBClassifier(
            n_estimators=220,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = utils.compute_strategy_metrics(X_test["log_return"], preds)
        if metrics["sharpe"] > best_metrics.get("sharpe", -1e9):
            best_model = model
            best_metrics = metrics

    best_model.fit(features, target)
    split_idx = int(len(features) * 0.8)
    X_val, y_val = features.iloc[split_idx:], target.iloc[split_idx:]
    val_preds = best_model.predict(X_val)
    val_metrics = utils.compute_strategy_metrics(X_val["log_return"], val_preds)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    model_path = utils.MODEL_DIR / f"pro_signal_model_{SYMBOL}_{INTERVAL}_{timestamp}.pkl"
    utils.save_model(best_model, model_path, feature_order, extra={"metrics": val_metrics})

    if register:
        async def _register():
            async with AsyncSessionLocal() as session:
                await register_model_version("pro", str(model_path), val_metrics["sharpe"], val_metrics["win_rate"], session)

        asyncio.run(_register())

    return model_path, val_metrics


if __name__ == "__main__":
    path, metrics = train_pro_model(register=True)
    print("Saved PRO model to", path)
    print("Validation metrics", metrics)
