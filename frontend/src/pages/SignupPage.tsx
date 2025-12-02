import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';

const mosaicTiles = [
    '#f9e2ae',
    '#ff9fb2',
    '#88c0d0',
    '#f4b942',
    '#8bd450',
    '#ffb347',
    '#c084fc',
    '#f38ba0',
    '#77dd77',
    '#ffda79',
    '#6ddccf',
    '#fab5a0',
    '#83b4ff',
    '#f7aef8',
    '#fcd29f',
    '#84fab0',
];

export const SignupPage = () => {
    const navigate = useNavigate();
    const { loginWithRedirect, isAuthenticated, isLoading } = useAuth0();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    const handleSignup = async () => {
        await loginWithRedirect({
            authorizationParams: {
                screen_hint: 'signup',
            },
            appState: { returnTo: '/' }
        });
    };

    const handleSocialSignup = async (connection: string) => {
        await loginWithRedirect({
            authorizationParams: {
                connection: connection,
                screen_hint: 'signup',
            },
            appState: { returnTo: '/' }
        });
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-muted">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="font-retro uppercase tracking-[0.3em]">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen w-full flex flex-col lg:flex-row bg-muted">
            <section className="flex-1 border-r-2 border-black bg-card px-8 py-12 flex flex-col">
                <div className="flex items-center justify-between border-b-2 border-black pb-6">
                    <div>
                        <p className="font-retro text-2xl uppercase tracking-[0.4em]">Champa</p>
                        <h1 className="text-4xl font-retro uppercase tracking-tight mt-2">Create Account</h1>
                    </div>
                </div>
                <div className="flex-1 w-full flex items-center justify-center">
                    <div className="w-full max-w-lg space-y-8">
                        <div className="space-y-3">
                            <Button
                                type="button"
                                variant="outline"
                                className="w-full border-2 border-black bg-[#4f7cff] text-white h-12 font-retro uppercase tracking-[0.2em] shadow-retro-xs hover:-translate-y-0.5 transition"
                                onClick={() => handleSocialSignup('google-oauth2')}
                            >
                                Google
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                className="w-full border-2 border-black bg-[#3b5998] text-white h-12 font-retro uppercase tracking-[0.2em] shadow-retro-xs hover:-translate-y-0.5 transition"
                                onClick={() => handleSocialSignup('facebook')}
                            >
                                Facebook
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                className="w-full border-2 border-black bg-black text-white h-12 font-retro uppercase tracking-[0.2em] shadow-retro-xs hover:-translate-y-0.5 transition"
                                onClick={() => handleSocialSignup('twitter')}
                            >
                                X
                            </Button>
                        </div>
                        <div className="flex items-center text-xs uppercase font-retro tracking-[0.3em] text-muted-foreground">
                            <span className="flex-1 border-t border-black"></span>
                            <span className="px-4">or</span>
                            <span className="flex-1 border-t border-black"></span>
                        </div>
                        <Button
                            type="button"
                            className="w-full border-2 border-black bg-primary text-white h-12 font-retro uppercase tracking-[0.2em]"
                            onClick={handleSignup}
                        >
                            Sign Up with Email
                        </Button>
                        <p className="text-center text-sm text-muted-foreground">
                            Auth0 Universal Login handles secure authentication
                        </p>
                    </div>
                </div>
            </section>
            <aside className="flex-1 min-h-[320px] border-l-2 border-black">
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 h-full">
                    {mosaicTiles.map((color, index) => (
                        <div
                            key={color + index}
                            className="border-b-2 border-r-2 border-black flex items-center justify-center font-retro text-xl"
                            style={{ backgroundColor: color }}
                        >
                            :)
                        </div>
                    ))}
                </div>
            </aside>
        </div>
    );
};
