import { renderHook, waitFor } from '@testing-library/react';
import { useMatches } from './useMatches';
import api from '@/lib/api';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the API module
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

describe('useMatches Polling Hook', () => {
  const candidateId = 'cand_123';
  const mockPagination = { total: 1, limit: 6, offset: 0, has_more: false };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.clearAllTimers();
  });

  it('should start polling when a job is in "processing" status and stop when "completed"', async () => {
    // 1. First call: returns a processing job
    const processingResp = {
      data: {
        data: [{ id: 'job_1', status: 'processing', retry_count: 0, created_at: 'now', updated_at: 'now' }],
        pagination: mockPagination
      }
    };

    // 2. Second call (polling): returns a completed job
    const completedResp = {
      data: {
        data: [{ id: 'job_1', status: 'completed', retry_count: 0, created_at: 'now', updated_at: 'now', overall_score: 90 }],
        pagination: mockPagination
      }
    };

    (api.get as any)
      .mockResolvedValueOnce(processingResp) // Initial fetch
      .mockResolvedValueOnce(completedResp); // First poll fetch

    const { result } = renderHook(() => useMatches(candidateId));

    // Wait for initial fetch to finish
    await waitFor(() => {
      expect(result.current.matches[0]?.status).toBe('processing');
    });

    expect(api.get).toHaveBeenCalledTimes(1);

    // Trigger polling by advancing time
    await vi.advanceTimersByTimeAsync(2500);

    // Should have called API again
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(2);
      expect(result.current.matches[0]?.status).toBe('completed');
    });

    // Advance time again - polling should have STOPPED because status is 'completed'
    await vi.advanceTimersByTimeAsync(2500);
    expect(api.get).toHaveBeenCalledTimes(2); // Still 2
  });

  it('should not start polling if all jobs are already "completed"', async () => {
    const completedResp = {
      data: {
        data: [{ id: 'job_1', status: 'completed' }],
        pagination: mockPagination
      }
    };

    (api.get as any).mockResolvedValueOnce(completedResp);

    const { result } = renderHook(() => useMatches(candidateId));

    await waitFor(() => {
      expect(result.current.matches[0]?.status).toBe('completed');
    });

    // Advance time - should NOT poll
    await vi.advanceTimersByTimeAsync(2500);
    expect(api.get).toHaveBeenCalledTimes(1);
  });
});
