import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

export const CallbackPage = () => {
    const navigate = useNavigate();
    const { isLoading, isAuthenticated, error } = useAuth0();

    useEffect(() => {
        if (isLoading) {
            return;
        }

        if (error) {
            console.error('Auth0 callback error:', error);
            navigate('/login');
            return;
        }

        if (isAuthenticated) {
            // Auth0 will handle the redirect via onRedirectCallback
            // But we can also manually navigate if needed
            navigate('/dashboard');
        } else {
            navigate('/login');
        }
    }, [isLoading, isAuthenticated, error, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-muted">
            <div className="text-center">
                <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="font-retro uppercase tracking-[0.3em]">Authenticating...</p>
            </div>
        </div>
    );
};
