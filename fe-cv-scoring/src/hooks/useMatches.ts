import { useState, useEffect, useCallback, useRef } from 'react';
import api from '@/lib/api';
import { MatchJob, MatchListResponse } from '@/types';

export function useMatches(candidateId: string | null, page: number = 1, limit: number = 6) {
  const [matches, setMatches] = useState<MatchJob[]>([]);
  const [pagination, setPagination] = useState({ total: 0, limit: 6, offset: 0, has_more: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const matchesRef = useRef<MatchJob[]>([]);
  matchesRef.current = matches;
  
  const offset = (page - 1) * limit;

  const fetchMatches = useCallback(async (isPolling = false) => {
    if (!candidateId) {
      setMatches([]);
      setPagination({ total: 0, limit, offset: 0, has_more: false });
      return;
    }
    
    try {
      if (!isPolling) setLoading(true);
      const res = await api.get<MatchListResponse>(`/matches?candidate_id=${candidateId}&limit=${limit}&offset=${offset}`);
      setMatches(res.data.data);
      setPagination(res.data.pagination);
      setError(null);
    } catch (err) {
      console.error(err);
      if (!isPolling) setError('Failed to fetch matches.');
    } finally {
      if (!isPolling) setLoading(false);
    }
  }, [candidateId, limit, offset]);

  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  useEffect(() => {
    if (!candidateId) return;

    const needsPolling = matchesRef.current.some(
      (m) => m.status === 'pending' || m.status === 'processing'
    );

    if (!needsPolling) return;

    const intervalId = setInterval(() => {
      fetchMatches(true);
    }, 2500);

    return () => clearInterval(intervalId);
  }, [candidateId, matches, fetchMatches]);

  return { matches, pagination, loading, error, refetch: () => fetchMatches(false) };
}
