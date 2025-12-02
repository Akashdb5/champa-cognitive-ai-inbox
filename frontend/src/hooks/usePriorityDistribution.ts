import { useState, useEffect } from 'react';
import { statsService, PriorityDistribution } from '../services/stats';

export const usePriorityDistribution = () => {
    const [distribution, setDistribution] = useState<PriorityDistribution | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchDistribution = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await statsService.getPriorityDistribution();
            setDistribution(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch priority distribution');
            console.error('Error fetching priority distribution:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDistribution();
    }, []);

    return { distribution, isLoading, error, refetch: fetchDistribution };
};
