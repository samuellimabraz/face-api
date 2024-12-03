import React, { useState } from 'react';
import { UserPlus, Trash2 } from 'lucide-react';
import { WebcamCapture } from './WebcamCapture';
import { api } from '../services/api';
import { APIKeyResponse } from '../types/api';

interface PersonRegistrationProps {
  organization: string;
  apiKey: APIKeyResponse;
}

export const PersonRegistration: React.FC<PersonRegistrationProps> = ({ organization, apiKey }) => {
  const [name, setName] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);

  const handleCapture = (imageSrc: string) => {
    if (isCapturing) {
      setImages((prev) => [...prev, imageSrc]);
    }
  };

  const handleToggleCapture = () => {
    setIsCapturing(!isCapturing);
  };

  const handleRemoveImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (images.length === 0) {
      alert('Please capture at least one image');
      return;
    }

    setLoading(true);
    try {
      await api.registerPerson(organization, apiKey.key, {
        images,
        name,
        api_auth: {
          user: apiKey.user,
          api_key_name: apiKey.api_key_name,
        },
      });
      setName('');
      setImages([]);
      setIsCapturing(false);
      alert('Person registered successfully!');
    } catch (error) {
      console.error('Error registering person:', error);
      alert('Failed to register person');
    }
    setLoading(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <UserPlus size={24} />
        Register Person
      </h2>
      <form onSubmit={handleRegister} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Capture Images ({images.length} captured)
          </label>
          <WebcamCapture
            onCapture={handleCapture}
            isCapturing={isCapturing}
            onToggleCapture={handleToggleCapture}
          />
          <div className="mt-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {images.map((img, index) => (
                <div key={index} className="relative group">
                  <img
                    src={img}
                    alt={`Capture ${index + 1}`}
                    className="w-full h-24 object-cover rounded-md"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveImage(index)}
                    className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading || images.length === 0}
          className="w-full bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors disabled:opacity-50"
        >
          {loading ? 'Registering...' : 'Register Person'}
        </button>
      </form>
    </div>
  );
};