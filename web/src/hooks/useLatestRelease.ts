import { useState, useEffect } from 'react';

interface LatestRelease {
  version: string;
  download_url: string;
  file_name: string;
  file_size: string;
  download_count: number;
  published_at: string;
  name?: string;
  description?: string;
  html_url?: string;
}

interface UseLatestReleaseReturn {
  data: LatestRelease | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useLatestRelease(): UseLatestReleaseReturn {
  const [data, setData] = useState<LatestRelease | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLatestRelease = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/latest-release');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch latest release: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.error || 'Failed to fetch release data');
        // Usar datos de respaldo si están disponibles
        if (result.fallback) {
          setData(result.fallback);
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error fetching latest release:', err);
      
      // Set fallback data
      setData({
        version: 'v1.0.0',
        download_url: 'https://github.com/SiegAxel/EncryptU/releases/download/pre-release/EncryptU-Setup-v1.0.0.exe',
        file_name: 'EncryptU-Setup-v1.0.0.exe',
        file_size: '39 MB',
        download_count: 0,
        published_at: '2024-01-01',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestRelease();
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchLatestRelease,
  };
}