import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

export type ConnectionType = 'http' | 'websocket';

interface ConnectionToggleProps {
  connectionType: ConnectionType;
  onChange: (type: ConnectionType) => void;
  disabled?: boolean;
}

export const ConnectionToggle: React.FC<ConnectionToggleProps> = ({
  connectionType,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700">Connection Type:</span>
      <button
        onClick={() => onChange(connectionType === 'http' ? 'websocket' : 'http')}
        disabled={disabled}
        className={`
          flex items-center gap-2 px-3 py-1 rounded-md text-sm
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${connectionType === 'websocket' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}
        `}
      >
        {connectionType === 'websocket' ? (
          <>
            <Wifi size={16} />
            WebSocket
          </>
        ) : (
          <>
            <WifiOff size={16} />
            HTTP
          </>
        )}
      </button>
    </div>
  );
};