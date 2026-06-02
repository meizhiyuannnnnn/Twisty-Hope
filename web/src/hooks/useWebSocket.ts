import { useEffect, useRef, useCallback, useState } from 'react';
import type { TaskProgress } from '@/types';
import { getWsUrl } from '@/services/api';

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  lastMessage: TaskProgress | null;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(taskId: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<TaskProgress | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'client disconnect');
      wsRef.current = null;
    }
    setConnectionState('disconnected');
  }, []);

  const connect = useCallback(() => {
    if (!taskId) return;
    disconnect();

    const url = getWsUrl(taskId);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    setConnectionState('connecting');

    ws.onopen = () => {
      setConnectionState('connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg: TaskProgress = JSON.parse(event.data as string);
        setLastMessage(msg);
      } catch {
        // 忽略无法解析的消息
      }
    };

    ws.onerror = () => {
      setConnectionState('error');
    };

    ws.onclose = (e) => {
      if (e.code !== 1000) {
        // 非正常关闭，尝试重连
        setConnectionState('disconnected');
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, 3000);
      } else {
        setConnectionState('disconnected');
      }
    };
  }, [taskId, disconnect]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { connectionState, lastMessage, connect, disconnect };
}
