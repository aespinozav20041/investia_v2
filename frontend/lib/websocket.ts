import { WS_URL } from "./api";

export function createWebSocket(path: string): WebSocket {
  const url = `${WS_URL}${path}`;
  return new WebSocket(url);
}
