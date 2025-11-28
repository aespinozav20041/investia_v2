export type UserState =
  | "UNREGISTERED"
  | "REGISTERED_PAPER"
  | "BROKER_CONNECTED"
  | "ML_MODEL_ACTIVE";

export interface UserProfile {
  id: string;
  email: string;
  state: UserState;
  createdAt: string;
  tradesCount?: number;
  positivePnL?: boolean;
}

export interface EquityPoint {
  timestamp: string;
  value: number;
}

export interface PaperPerformance {
  equityCurve: EquityPoint[];
  totalPnL: number;
  dailyPnL: number;
  initialBalance: number;
  currentBalance: number;
  status: "running" | "paused";
}

export interface TradeRow {
  id: string;
  timestamp: string;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
  pnl: number;
}

export interface BrokerConnectionPayload {
  broker: string;
  apiKey: string;
  apiSecret: string;
  passphrase?: string;
  accountId?: string;
}

export interface ModelSummary {
  id: string;
  name: string;
  description: string;
  assetClass: string;
  sharpe: number;
  drawdown: number;
  historicalPnl: number;
  price: string;
  active?: boolean;
}

export interface Plan {
  id: string;
  name: string;
  price: string;
  description: string;
  features: string[];
  recommended?: boolean;
}
