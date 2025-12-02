import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { usePlatforms } from '../hooks/usePlatforms';
import { useAuth } from '../contexts/AuthContext';
import { useState, useEffect } from 'react';
import { authService, UserProfile, ProfileUpdateData } from '../services/auth';

export const ProfilePage = () => {
    const { user } = useAuth();
    const { platformStatus, connectPlatform, disconnectPlatform, isLoading } = usePlatforms();
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [profileLoading, setProfileLoading] = useState(false);
    const [profileSuccess, setProfileSuccess] = useState(false);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [profileForm, setProfileForm] = useState<ProfileUpdateData>({
        phone: '',
        location: '',
        timezone: '',
        website: '',
    });

    // Load user profile on mount
    useEffect(() => {
        const loadProfile = async () => {
            try {
                const profile = await authService.getUserProfile();
                setUserProfile(profile);
                setProfileForm({
                    phone: profile.phone || '',
                    location: profile.location || '',
                    timezone: profile.timezone || '',
                    website: profile.website || '',
                });
            } catch (err) {
                console.error('Failed to load profile:', err);
            }
        };
        loadProfile();
    }, []);

    const platformConnections = [
        {
            name: 'Gmail',
            key: 'gmail',
            description: 'Aggregate emails from your inbox into unified feed.',
            accent: '#f87171',
            connected: platformStatus.gmail,
        },
        {
            name: 'Slack',
            key: 'slack',
            description: 'Pull messages from your Slack workspace channels.',
            accent: '#60a5fa',
            connected: platformStatus.slack,
        },
        {
            name: 'Google Calendar',
            key: 'calendar',
            description: 'Sync calendar events and meeting invites.',
            accent: '#facc15',
            connected: platformStatus.calendar,
        },
    ];

    const handlePlatformAction = async (platformKey: string, isConnected: boolean) => {
        setActionLoading(platformKey);
        setError(null);
        try {
            if (isConnected) {
                await disconnectPlatform(platformKey);
            } else {
                // Open OAuth popup for connection
                await connectPlatform(platformKey);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setActionLoading(null);
        }
    };

    const handleProfileUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        setProfileLoading(true);
        setError(null);
        setProfileSuccess(false);

        try {
            const updatedProfile = await authService.updateUserProfile(profileForm);
            setUserProfile(updatedProfile);
            setProfileSuccess(true);
            setTimeout(() => setProfileSuccess(false), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update profile');
        } finally {
            setProfileLoading(false);
        }
    };

    const handleProfileChange = (field: keyof ProfileUpdateData, value: string) => {
        setProfileForm(prev => ({ ...prev, [field]: value }));
    };

    return (
        <div className="space-y-8">
            <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <p className="text-xs uppercase font-retro tracking-[0.4em] text-muted-foreground">Control Center</p>
                    <h1 className="text-4xl font-retro uppercase tracking-tight">Profile Console</h1>
                    <p className="text-sm text-muted-foreground">Tune your avatar, update coordinates, and connect more retro tech.</p>
                </div>
                <Button className="border-2 border-black shadow-retro-sm font-retro uppercase tracking-[0.2em]">
                    Save All
                </Button>
            </header>

            <Card className="border-2 border-black shadow-retro-md">
                <CardHeader className="border-b-2 border-black bg-card/70">
                    <CardTitle className="font-retro uppercase tracking-[0.3em]">Profile Signal</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row gap-8">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-28 h-28 border-2 border-black bg-muted shadow-retro-sm flex items-center justify-center font-retro text-xl">
                                {user?.username?.slice(0, 2).toUpperCase() || 'U'}
                            </div>
                            <Button variant="outline" className="border-2 border-black font-retro uppercase text-xs shadow-retro-xs">
                                Upload Avatar
                            </Button>
                        </div>
                        <form className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <Label htmlFor="username">Username</Label>
                                <Input
                                    id="username"
                                    placeholder="username"
                                    className="border-2 border-black shadow-retro-xs"
                                    value={user?.username || ''}
                                    disabled
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="user@example.com"
                                    className="border-2 border-black shadow-retro-xs"
                                    value={user?.email || ''}
                                    disabled
                                />
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <Label htmlFor="userId">User ID</Label>
                                <Input
                                    id="userId"
                                    placeholder="User ID"
                                    className="border-2 border-black shadow-retro-xs"
                                    value={user?.user_id || ''}
                                    disabled
                                />
                            </div>
                        </form>
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2 border-black shadow-retro-md">
                    <CardHeader className="border-b-2 border-black bg-card/70">
                        <CardTitle className="font-retro uppercase tracking-[0.3em]">Basic Details</CardTitle>
                    </CardHeader>
                    <CardContent className="p-6">
                        {profileSuccess && (
                            <div className="mb-4 border-2 border-black bg-green-100 px-4 py-2">
                                <p className="text-sm text-green-700">Profile updated successfully!</p>
                            </div>
                        )}
                        <form className="space-y-4" onSubmit={handleProfileUpdate}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="profile-email">Email</Label>
                                    <Input
                                        id="profile-email"
                                        type="email"
                                        placeholder="retro@hq.com"
                                        className="border-2 border-black shadow-retro-xs"
                                        value={userProfile?.email || ''}
                                        disabled
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="phone">Phone</Label>
                                    <Input
                                        id="phone"
                                        type="tel"
                                        placeholder="+1 555 123 987"
                                        className="border-2 border-black shadow-retro-xs"
                                        value={profileForm.phone}
                                        onChange={(e) => handleProfileChange('phone', e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="location">Location</Label>
                                    <Input
                                        id="location"
                                        placeholder="Neo Portland, OR"
                                        className="border-2 border-black shadow-retro-xs"
                                        value={profileForm.location}
                                        onChange={(e) => handleProfileChange('location', e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="timezone">Timezone</Label>
                                    <Input
                                        id="timezone"
                                        placeholder="PST (-08:00)"
                                        className="border-2 border-black shadow-retro-xs"
                                        value={profileForm.timezone}
                                        onChange={(e) => handleProfileChange('timezone', e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="website">Signal Boost</Label>
                                <Input
                                    id="website"
                                    placeholder="retro-ui.dev"
                                    className="border-2 border-black shadow-retro-xs"
                                    value={profileForm.website}
                                    onChange={(e) => handleProfileChange('website', e.target.value)}
                                />
                            </div>
                            <Button
                                type="submit"
                                className="border-2 border-black shadow-retro-sm font-retro uppercase tracking-[0.2em]"
                                disabled={profileLoading}
                            >
                                {profileLoading ? 'Updating...' : 'Update Details'}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                <Card className="border-2 border-black shadow-retro-md">
                    <CardHeader className="border-b-2 border-black bg-card/70">
                        <CardTitle className="font-retro uppercase tracking-[0.3em]">Platform Links</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        {error && (
                            <div className="border-b-2 border-black bg-red-100 px-4 py-2">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        )}
                        <ul className="divide-y-2 divide-black">
                            {platformConnections.map((platform) => (
                                <li key={platform.name} className="flex flex-col md:flex-row md:items-center gap-3 p-4">
                                    <div className="flex items-center gap-4 flex-1">
                                        <div
                                            className="w-10 h-10 border-2 border-black shadow-retro-xs flex items-center justify-center font-retro text-sm"
                                            style={{ backgroundColor: platform.accent }}
                                        >
                                            {platform.name.slice(0, 1)}
                                        </div>
                                        <div>
                                            <p className="font-retro uppercase tracking-[0.2em]">{platform.name}</p>
                                            <p className="text-sm text-muted-foreground">{platform.description}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span
                                            className={`text-xs font-bold uppercase ${
                                                platform.connected ? 'text-green-700' : 'text-muted-foreground'
                                            }`}
                                        >
                                            {platform.connected ? 'Connected' : 'Not connected'}
                                        </span>
                                        <Button
                                            variant={platform.connected ? 'outline' : 'default'}
                                            className={`border-2 border-black shadow-retro-xs font-retro uppercase tracking-[0.2em] ${
                                                platform.connected ? 'bg-background' : 'bg-primary text-black'
                                            }`}
                                            onClick={() => handlePlatformAction(platform.key, platform.connected)}
                                            disabled={actionLoading === platform.key || isLoading}
                                        >
                                            {actionLoading === platform.key
                                                ? 'Loading...'
                                                : platform.connected
                                                ? 'Disconnect'
                                                : 'Connect'}
                                        </Button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

