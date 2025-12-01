class DataIngestionService:
    """Collects market and sentiment features (stubbed)."""

    def get_order_book_snapshot(self, symbol: str) -> float:
        return 0.6  # pretend imbalance score

    def get_sentiment_features(self, symbol: str) -> float:
        return 0.55  # pretend sentiment score

    def get_quant_features(self, symbol: str) -> float:
        return 0.5  # pretend momentum score


data_ingestion_service = DataIngestionService()
