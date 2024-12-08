import React, { useState } from 'react';
import { Key } from 'lucide-react';
import { api } from '../services/api';
import { APIKeyResponse } from '../types/api';

interface ApiKeyManagerProps {
  organization: string;
  onApiKeyCreated: (apiKey: APIKeyResponse) => void;
}

export const ApiKeyManager: React.FC<ApiKeyManagerProps> = ({ organization, onApiKeyCreated }) => {
  const [user, setUser] = useState('');
  const [keyName, setKeyName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.createApiKey(organization, {
        user,
        api_key_name: keyName,
      });
      onApiKeyCreated(response);
      setUser('');
      setKeyName('');
    } catch (error) {
      console.error('Error creating API key:', error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Key size={24} />
        API Key Management
      </h2>
      <form onSubmit={handleCreateKey} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">User</label>
          <input
            type="text"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Key Name</label>
          <input
            type="text"
            value={keyName}
            onChange={(e) => setKeyName(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create API Key'}
        </button>
      </form>
    </div>
  );
};