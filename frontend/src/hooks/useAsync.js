import { useState, useCallback, useRef } from 'react';
import { ApiError } from '../api/client';

export function useAsync() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const lastErrorRef = useRef(null);

  const run = useCallback(async (fn) => {
    lastErrorRef.current = null;
    setLoading(true);
    setError(null);
    try {
      return await fn();
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : (e.message ?? 'Unknown error');
      lastErrorRef.current = msg;
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    lastErrorRef.current = null;
  }, []);

  // getLastError reads from ref - always reflects the result of the most recent run()
  const getLastError = useCallback(() => lastErrorRef.current, []);

  return { loading, error, clearError, run, getLastError };
}
