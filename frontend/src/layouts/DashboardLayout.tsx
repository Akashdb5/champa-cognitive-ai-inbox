import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import { Home, LogOut, Menu, MessageCircle, Moon, Sun, User, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const navItems = [
    { label: 'Dashboard', icon: Home, to: '/dashboard' },
    { label: 'Chat', icon: MessageCircle, to: '/chat' },
    { label: 'Profile', icon: User, to: '/profile' },
];

export const DashboardLayout = () => {
    const { logout } = useAuth0();
    const [theme, setTheme] = useState<'light' | 'dark'>(() => {
        if (typeof window !== 'undefined') {
            return (window.localStorage.getItem('retro-theme') as 'light' | 'dark') || 'light';
        }
        return 'light';
    });
    const [menuOpen, setMenuOpen] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [syncMessage, setSyncMessage] = useState<string | null>(null);
    const location = useLocation();

    useEffect(() => {
        if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('dark', theme === 'dark');
        }
        if (typeof window !== 'undefined') {
            window.localStorage.setItem('retro-theme', theme);
        }
    }, [theme]);

    const toggleTheme = () => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));

    const handleLogout = () => {
        logout({
            logoutParams: {
                returnTo: window.location.origin + '/login'
            }
        });
    };

    const handleSync = async () => {
        setSyncing(true);
        setSyncMessage('Syncing messages...');
        try {
            const response = await api.post('/api/messages/sync');
            const data = response.data;
            
            // Show detailed sync results
            const messages = [];
            if (data.new_messages > 0) {
                messages.push(`${data.new_messages} new`);
            }
            if (data.analyzed > 0) {
                messages.push(`${data.analyzed} analyzed`);
            }
            if (data.duplicates > 0) {
                messages.push(`${data.duplicates} duplicates`);
            }
            
            const summary = messages.length > 0 ? messages.join(', ') : 'No new messages';
            setSyncMessage(`✓ ${summary}`);
            
            // Refresh the page data after successful sync
            setTimeout(() => {
                setSyncMessage(null);
                window.location.reload(); // Reload to show updated stats
            }, 2000);
        } catch (error: any) {
            setSyncMessage(`✗ Sync failed: ${error.response?.data?.detail || 'Unknown error'}`);
            setTimeout(() => setSyncMessage(null), 5000);
        } finally {
            setSyncing(false);
        }
    };

    return (
        <div className="min-h-screen bg-background flex flex-col transition-colors">
            <header className="border-b-2 border-black bg-card p-4 flex justify-between items-center sticky top-0 z-20">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-primary border-2 border-black shadow-retro-sm"></div>
                        <span className="font-bold text-xl font-retro uppercase tracking-tight">Champa</span>
                    </div>
                    {syncMessage && (
                        <span className={`text-sm font-retro ${syncMessage.startsWith('✓') ? 'text-green-600' : 'text-red-600'}`}>
                            {syncMessage}
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex gap-2 items-center border-2 border-black shadow-retro-xs"
                        onClick={handleSync}
                        disabled={syncing}
                    >
                        <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
                        {syncing ? 'Syncing...' : 'Sync'}
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex gap-2 items-center border-2 border-black shadow-retro-xs"
                        onClick={toggleTheme}
                    >
                        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                        {theme === 'dark' ? 'Light' : 'Dark'}
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex gap-2 items-center border-2 border-black shadow-retro-xs lg:hidden"
                        onClick={() => setMenuOpen((prev) => !prev)}
                        aria-expanded={menuOpen}
                        aria-label="Toggle menu"
                    >
                        <Menu size={16} />
                        Menu
                    </Button>
                    <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex gap-2 items-center border-2 border-black shadow-retro-xs"
                        onClick={handleLogout}
                    >
                        <LogOut size={16} /> Logout
                    </Button>
                </div>
            </header>
            <nav
                className={`lg:hidden border-b-2 border-black bg-card px-4 py-3 shadow-retro-sm transition-all ${
                    menuOpen ? 'max-h-96' : 'max-h-0 overflow-hidden border-transparent'
                }`}
            >
                <div className="flex flex-col gap-3">
                    {navItems.map((item) => (
                        <Link
                            key={item.to}
                            to={item.to}
                            className={`flex items-center gap-3 border-2 border-black px-3 py-2 shadow-retro-xs font-retro uppercase text-sm tracking-tight ${
                                location.pathname === item.to ? 'bg-primary/20' : 'bg-background'
                            }`}
                            onClick={() => setMenuOpen(false)}
                        >
                            <item.icon size={16} />
                            {item.label}
                        </Link>
                    ))}
                </div>
            </nav>
            <div className="flex flex-1 flex-col lg:flex-row">
                <aside className="hidden lg:flex w-60 border-r-2 border-black bg-card p-4 shadow-retro-sm flex-col gap-4">
                    <p className="text-xs font-retro uppercase tracking-[0.2em] text-muted-foreground">Menu</p>
                    <div className="flex flex-col gap-3">
                        {navItems.map((item) => (
                            <Link
                                key={item.to}
                                to={item.to}
                                className={`flex items-center gap-3 border-2 border-black px-3 py-2 shadow-retro-xs font-retro uppercase text-sm tracking-tight transition ${
                                    location.pathname === item.to ? 'bg-primary/20' : 'bg-background hover:bg-primary/10'
                                }`}
                            >
                                <item.icon size={16} />
                                {item.label}
                            </Link>
                        ))}
                    </div>
                </aside>
                <main className="flex-1 w-full px-4 py-6 lg:p-8">
                    <div className="w-full max-w-5xl mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};
