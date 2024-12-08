import { RecognitionResult } from '../types/api';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private messageCallback: ((result: RecognitionResult) => void) | null = null;

  connect(organization: string, apiKey: string, user: string, apiKeyName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const uri = `ws://localhost:8000/ws/recognize?token=${apiKey}&organization=${organization}&user=${user}&api_key_name=${apiKeyName}`;
      this.ws = new WebSocket(uri);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onmessage = (event) => {
        try {
          const result = JSON.parse(event.data) as RecognitionResult;
          this.messageCallback?.(result);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  setMessageCallback(callback: (result: RecognitionResult) => void) {
    this.messageCallback = callback;
  }

  sendImage(data: { image: string; threshold: number; organization: string }) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }
}

export const websocketService = new WebSocketService();