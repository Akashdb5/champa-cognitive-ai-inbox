import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export const OAuthRedirectPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [status, setStatus] = useState<string>('Processing...');
    const [showCloseButton, setShowCloseButton] = useState(false);

    useEffect(() => {
        const handleOAuthCallback = async () => {
            console.log('=== OAuth Redirect Page Loaded ===');
            console.log('Current URL:', window.location.href);
            
            const code = searchParams.get('code');
            const state = searchParams.get('state');
            const platform = searchParams.get('platform') || 'gmail';
            const errorParam = searchParams.get('error');

            console.log('Platform:', platform);
            console.log('Code:', code ? `${code.substring(0, 20)}...` : 'MISSING');
            console.log('State:', state);
            console.log('Error:', errorParam);

            if (errorParam) {
                setError(`OAuth error: ${errorParam}`);
                setStatus('Failed');
                setTimeout(() => navigate('/profile'), 3000);
                return;
            }

            if (!code) {
                console.error('NO CODE RECEIVED!');
                setError('No authorization code received');
                setStatus('Failed');
                setTimeout(() => navigate('/profile'), 3000);
                return;
            }

            try {
                const platformName = platform.charAt(0).toUpperCase() + platform.slice(1);
                setStatus(`Connecting ${platformName}...`);
                
                // Backend already processed the OAuth callback and stored tokens
                // We just need to notify the parent window
                console.log('OAuth callback success - tokens already stored by backend');
                setStatus('Success!');
                
                // If opened in popup, notify parent and close
                if (window.opener && !window.opener.closed) {
                    console.log('Sending success message to parent window');
                    try {
                        window.opener.postMessage(
                            { type: 'OAUTH_SUCCESS', platform }, 
                            window.location.origin
                        );
                    } catch (e) {
                        console.error('Failed to send message to parent:', e);
                    }
                    setTimeout(() => {
                        console.log('Closing popup window');
                        window.close();
                    }, 1500);
                    
                    // Show close button after 3 seconds if window didn't close
                    setTimeout(() => {
                        setShowCloseButton(true);
                    }, 3000);
                } else {
                    console.log('Not in popup, redirecting to profile');
                    // If not in popup, redirect to profile
                    setTimeout(() => navigate('/profile'), 1500);
                }
            } catch (err: any) {
                console.error('OAuth callback error:', err);
                setError(err.response?.data?.detail || `Failed to connect ${platform}`);
                setStatus('Failed');
                
                // If opened in popup, notify parent and close
                if (window.opener && !window.opener.closed) {
                    console.log('Sending error message to parent window');
                    window.opener.postMessage(
                        { type: 'OAUTH_ERROR', error: err.response?.data?.detail }, 
                        window.location.origin
                    );
                    setTimeout(() => window.close(), 2000);
                } else {
                    setTimeout(() => navigate('/profile'), 3000);
                }
            }
        };

        handleOAuthCallback();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-muted">
            <div className="border-2 border-black bg-card p-8 shadow-retro max-w-md w-full">
                <div className="text-center space-y-4">
                    {!error ? (
                        <>
                            <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto"></div>
                            <h2 className="font-retro text-2xl uppercase tracking-[0.3em]">{status}</h2>
                            <p className="text-muted-foreground">Please wait while we connect your account...</p>
                            {showCloseButton && (
                                <button
                                    onClick={() => window.close()}
                                    className="mt-4 px-6 py-2 border-2 border-black bg-primary text-primary-foreground shadow-retro hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all font-retro uppercase tracking-wider"
                                >
                                    Close Window
                                </button>
                            )}
                        </>
                    ) : (
                        <>
                            <div className="w-16 h-16 border-4 border-red-500 rounded-full mx-auto flex items-center justify-center">
                                <span className="text-3xl text-red-500">✕</span>
                            </div>
                            <h2 className="font-retro text-2xl uppercase tracking-[0.3em] text-red-600">{status}</h2>
                            <p className="text-red-600">{error}</p>
                            <p className="text-sm text-muted-foreground">Redirecting back to profile...</p>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};
