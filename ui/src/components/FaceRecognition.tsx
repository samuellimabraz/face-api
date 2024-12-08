import React, { useState, useEffect } from 'react';
import { Scan } from 'lucide-react';
import { WebcamCapture } from './WebcamCapture';
import { api } from '../services/api';
import { websocketService } from '../services/websocketService';
import { APIKeyResponse, RecognitionResult } from '../types/api';
import { ConnectionToggle, ConnectionType } from './ConnectionToggle';

interface FaceRecognitionProps {
  organization: string;
  apiKey: APIKeyResponse;
}

export const FaceRecognition: React.FC<FaceRecognitionProps> = ({ organization, apiKey }) => {
  const [threshold, setThreshold] = useState(0.5);
  const [result, setResult] = useState<RecognitionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [connectionType, setConnectionType] = useState<ConnectionType>('http');

  useEffect(() => {
    if (connectionType === 'websocket' && isCapturing) {
      websocketService.connect(organization, apiKey.key, apiKey.user, apiKey.api_key_name)
        .then(() => {
          websocketService.setMessageCallback(setResult);
        })
        .catch((error) => {
          console.error('Failed to connect to WebSocket:', error);
          setIsCapturing(false);
        });
    }

    return () => {
      if (connectionType === 'websocket') {
        websocketService.disconnect();
      }
    };
  }, [connectionType, isCapturing, organization, apiKey]);

  const handleRecognize = async (imageSrc: string) => {
    if (!isCapturing) return;
    
    setLoading(true);
    try {
      if (connectionType === 'websocket') {
        websocketService.sendImage({
          image: imageSrc,
          threshold,
          organization,
        });
      } else {
        const response = await api.recognizePerson(organization, apiKey.key, {
          image: imageSrc,
          threshold,
          api_auth: {
            user: apiKey.user,
            api_key_name: apiKey.api_key_name,
          },
        });
        setResult(response);
      }
    } catch (error) {
      console.error('Error recognizing face:', error);
      setIsCapturing(false);
    }
    setLoading(false);
  };

  const handleToggleCapture = () => {
    setIsCapturing(!isCapturing);
    if (!isCapturing) {
      setResult(null);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Scan size={24} />
          Face Recognition
        </h2>
        <ConnectionToggle
          connectionType={connectionType}
          onChange={setConnectionType}
          disabled={isCapturing}
        />
      </div>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Threshold: {threshold}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
        <WebcamCapture
          onCapture={handleRecognize}
          isCapturing={isCapturing}
          onToggleCapture={handleToggleCapture}
          detections={result?.detections}
        />
        {loading && (
          <div className="text-center text-gray-600">Processing...</div>
        )}
        {result && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Results:</h3>
            <div className="max-h-40 overflow-y-auto">
              {result.searchs.map((search, index) => (
                <div
                  key={index}
                  className="bg-gray-50 p-3 rounded-md mb-2 flex justify-between items-center"
                >
                  <span className="font-medium">{search.name}</span>
                  <span className="text-sm text-gray-500">
                    Distance: {search.distance?.toFixed(3) ?? 'N/A'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};