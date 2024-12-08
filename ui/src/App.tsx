import React, { useState } from 'react';
import { Building } from 'lucide-react';
import { api } from './services/api';
import { APIKeyResponse } from './types/api';
import { ApiKeyManager } from './components/ApiKeyManager';
import { PersonRegistration } from './components/PersonRegistration';
import { FaceRecognition } from './components/FaceRecognition';

function App() {
  const [organization, setOrganization] = useState('');
  const [orgCreated, setOrgCreated] = useState(false);
  const [apiKey, setApiKey] = useState<APIKeyResponse | null>(null);

  const handleCreateOrganization = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createOrganization({ organization });
      setOrgCreated(true);
    } catch (error) {
      console.error('Error creating organization:', error);
      alert('Failed to create organization');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Face Recognition System</h1>
        
        {!orgCreated ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Building size={24} />
              Create Organization
            </h2>
            <form onSubmit={handleCreateOrganization} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
              >
                Create Organization
              </button>
            </form>
          </div>
        ) : !apiKey ? (
          <ApiKeyManager
            organization={organization}
            onApiKeyCreated={setApiKey}
          />
        ) : (
          <div className="space-y-8">
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-green-800">
                <span className="font-semibold">Active API Key:</span> {apiKey.key}
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <PersonRegistration
                organization={organization}
                apiKey={apiKey}
              />
              <FaceRecognition
                organization={organization}
                apiKey={apiKey}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;