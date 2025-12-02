import { useState, useEffect } from 'react';
import { statsService, ActionableStats } from '../services/stats';

export const useActionableStats = () => {
    const [stats, setStats] = useState<ActionableStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStats = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await statsService.getActionableStats();
            setStats(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch actionable stats');
            console.error('Error fetching actionable stats:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    return { stats, isLoading, error, refetch: fetchStats };
};
