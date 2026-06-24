import { useEffect, useRef, useCallback, useState } from 'react';
import type { TaskProgress } from '@/types';
import { getWsUrl, getTaskStatus } from '@/services/api';

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  lastMessage: TaskProgress | null;
  connect: () => void;
  disconnect: () => void;
}

// ── 模块级 WebSocket 管理（避开 React 闭包问题）──────────────────
let _staticWs: WebSocket | null = null;
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null;
const _listeners = new Set<(msg: TaskProgress) => void>();

function createConnection(taskId: string, token: string): WebSocket {
  // 清理旧连接和重连计时器
  if (_reconnectTimer) {
    clearTimeout(_reconnectTimer);
    _reconnectTimer = null;
  }
  if (_staticWs) {
    _staticWs.close(1000, 'reconnect');
    _staticWs = null;
  }

  const url = getWsUrl(taskId, token);
  const ws = new WebSocket(url);
  _staticWs = ws;

  ws.onopen = () => {
    // 连接成功，通知状态变更（通过特殊的 status 事件？不，改用 connectionState）
  };

  ws.onmessage = (event) => {
    try {
      const msg: TaskProgress = JSON.parse(event.data as string);
      // 通知所有已注册的监听器
      _listeners.forEach((fn) => fn(msg));
    } catch { /* ignore */ }
  };

  ws.onerror = () => {
    // 错误发生后 onclose 会紧随触发，在 onclose 中统一处理重连
  };

  ws.onclose = (e) => {
    if (_staticWs !== ws) return; // 已被新连接替代，忽略
    _staticWs = null;

    // 非正常关闭 → 3 秒后自动重连
    if (e.code !== 1000) {
      _reconnectTimer = setTimeout(() => {
        _reconnectTimer = null;
        // 重连前检查是否仍有监听器需要服务
        if (_listeners.size > 0) {
          createConnection(taskId, token);
        }
      }, 3000);
    }
  };

  return ws;
}

function closeStaticConnection(code = 1000, reason = 'disconnect'): void {
  if (_reconnectTimer) {
    clearTimeout(_reconnectTimer);
    _reconnectTimer = null;
  }
  if (_staticWs) {
    _staticWs.close(code, reason);
    _staticWs = null;
  }
}

export function useWebSocket(taskId: string | null, token: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<TaskProgress | null>(null);
  const listenerRef = useRef<((msg: TaskProgress) => void) | null>(null);
  // 轮询回退计时器
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // 记录最近消息时间，用于检测连接僵死
  const lastMsgTimeRef = useRef<number>(0);

  // ── 启动 HTTP 轮询作为 WebSocket 失败时的回退 ──────────────────
  const startPolling = useCallback((tid: string, tok: string) => {
    if (pollTimerRef.current) return; // 已在轮询
    pollTimerRef.current = setInterval(async () => {
      try {
        const status = await getTaskStatus(tid, tok);
        // 仅当 WebSocket 断开超过 10 秒才用轮询数据更新
        // 避免与 WebSocket 消息冲突
        const timeSinceLastWs = Date.now() - lastMsgTimeRef.current;
        if (timeSinceLastWs > 10000) {
          _listeners.forEach((fn) => fn(status));
        }
      } catch {
        // 轮询失败静默忽略
      }
    }, 8000); // 每 8 秒轮询一次
  }, []);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }, []);

  // ── 断开连接 ──────────────────────────────────────────────────
  const disconnect = useCallback(() => {
    stopPolling();
    if (listenerRef.current) {
      _listeners.delete(listenerRef.current);
      listenerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'client disconnect');
      wsRef.current = null;
    }
    closeStaticConnection(1000, 'client disconnect');
    setConnectionState('disconnected');
  }, [stopPolling]);

  // ── 建立连接 ──────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (!taskId || !token) return;

    // 清理旧状态
    disconnect();

    // 注册本 hook 的监听器
    const listener = (msg: TaskProgress) => {
      lastMsgTimeRef.current = Date.now();
      setLastMessage(msg);
    };
    _listeners.add(listener);
    listenerRef.current = listener;

    setConnectionState('connecting');

    const ws = createConnection(taskId, token);
    wsRef.current = ws;

    // 覆盖 createConnection 中的 onopen/onerror/onclose 以同步 React 状态
    const origOnOpen = ws.onopen;
    ws.onopen = (ev) => {
      setConnectionState('connected');
      if (origOnOpen) origOnOpen.call(ws, ev);
    };

    const origOnError = ws.onerror;
    ws.onerror = (ev) => {
      setConnectionState('error');
      if (origOnError) origOnError.call(ws, ev);
    };

    const origOnClose = ws.onclose;
    ws.onclose = (ev) => {
      if (_staticWs !== ws) return;
      setConnectionState('disconnected');
      if (origOnClose) origOnClose.call(ws, ev);
    };

    // 启动轮询回退
    startPolling(taskId, token);
  }, [taskId, token, disconnect, startPolling]);

  // ── 自动连接：taskId/token 变化时自动建连 ──────────────────────
  useEffect(() => {
    if (taskId && token) {
      connect();
    }
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, token]);

  // ── 组件卸载时清理 ────────────────────────────────────────────
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { connectionState, lastMessage, connect, disconnect };
}

// ── 静态连接方法 ── 供 handleHistorySelect 等场景使用 ────────────
// 返回 cleanup 函数，调用后移除监听器并断开连接
export function connectWebSocket(
  taskId: string,
  token: string,
  onMsg: (msg: TaskProgress) => void,
): () => void {
  _listeners.add(onMsg);
  createConnection(taskId, token);
  return () => {
    _listeners.delete(onMsg);
    closeStaticConnection(1000, 'disconnect');
  };
}

// ── 清理所有模块级状态（供 resetAll 等场景使用）─────────────────
export function clearWebSocketState(): void {
  _listeners.clear();
  closeStaticConnection(1000, 'reset');
}
