import { useState, useEffect } from 'react';
import { statsService, SpamStats } from '../services/stats';

export const useSpamStats = () => {
    const [stats, setStats] = useState<SpamStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStats = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await statsService.getSpamStats();
            setStats(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch spam stats');
            console.error('Error fetching spam stats:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    return { stats, isLoading, error, refetch: fetchStats };
};
