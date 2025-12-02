import { useState, useEffect } from 'react';
import { platformService, PlatformStatus } from '../services/platforms';

export const usePlatforms = () => {
    const [platformStatus, setPlatformStatus] = useState<PlatformStatus>({
        gmail: false,
        slack: false,
        calendar: false,
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPlatformStatus = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const status = await platformService.getPlatformStatus();
            setPlatformStatus(status);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch platform status');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPlatformStatus();
    }, []);

    const connectPlatform = async (platform: string) => {
        try {
            // Get authorization URL
            const response = await platformService.getAuthUrl(platform);
            
            // Open OAuth popup
            if (response.redirect_url) {
                window.open(response.redirect_url, 'oauth_popup', 'width=600,height=700');
                
                // Listen for messages from popup
                const handleMessage = async (event: MessageEvent) => {
                    // Ignore messages from browser extensions (MetaMask, etc.)
                    if (!event.data || !event.data.type || event.data.target === 'metamask-inpage') {
                        return;
                    }
                    
                    console.log('Received message from popup:', event.data, 'origin:', event.origin);
                    
                    // Verify origin for security
                    if (event.origin !== window.location.origin) {
                        console.log('Origin mismatch, ignoring message');
                        return;
                    }
                    
                    if (event.data.type === 'OAUTH_SUCCESS') {
                        console.log('OAuth success, refreshing platform status');
                        // Refresh platform status
                        await fetchPlatformStatus();
                        console.log('Platform status refreshed');
                        window.removeEventListener('message', handleMessage);
                    } else if (event.data.type === 'OAUTH_ERROR') {
                        console.log('OAuth error:', event.data.error);
                        setError(event.data.error || 'OAuth failed');
                        window.removeEventListener('message', handleMessage);
                    }
                };
                
                console.log('Adding message listener for OAuth popup');
                window.addEventListener('message', handleMessage);
                
                // Fallback: Refresh status after 5 seconds
                setTimeout(() => {
                    console.log('Fallback: Refreshing platform status');
                    fetchPlatformStatus();
                    window.removeEventListener('message', handleMessage);
                }, 5000);
            }
            
            return response;
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to connect platform');
        }
    };

    const disconnectPlatform = async (platform: string) => {
        try {
            await platformService.disconnectPlatform(platform);
            await fetchPlatformStatus();
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to disconnect platform');
        }
    };

    return {
        platformStatus,
        isLoading,
        error,
        connectPlatform,
        disconnectPlatform,
        refetch: fetchPlatformStatus,
    };
};
