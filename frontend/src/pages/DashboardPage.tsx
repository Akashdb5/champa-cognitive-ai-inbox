import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Mail, MessageSquare, Activity, AlertTriangle, Shield, ExternalLink } from 'lucide-react';
import { useOverviewStats } from '../hooks/useStats';
import { useSpamStats } from '../hooks/useSpamStats';
import { usePriorityDistribution } from '../hooks/usePriorityDistribution';
import { useActionableStats } from '../hooks/useActionableStats';
import { useMessages } from '../hooks/useMessages';
import { Button } from '@/components/ui/button';
import { MessageWithReplies } from '../components/MessageWithReplies';

const StatCard = ({ title, value, icon: Icon, trend, color = 'bg-accent' }: any) => (
    <Card className="flex flex-col justify-between">
        <CardContent className="p-6 flex flex-col gap-2">
            <div className="flex justify-between items-start">
                <span className="text-muted-foreground font-bold text-sm uppercase">{title}</span>
                <div className={`p-2 ${color} border-2 border-black rounded-none shadow-retro-sm`}>
                    <Icon size={20} />
                </div>
            </div>
            <div className="text-3xl font-bold">{value}</div>
            <div className="text-sm font-bold text-green-600 flex items-center gap-1">
                <TrendingUp size={14} /> {trend}
            </div>
        </CardContent>
    </Card>
);

export const DashboardPage = () => {
    const { stats, isLoading } = useOverviewStats();
    const { stats: spamStats } = useSpamStats();
    const { distribution: priorityDist } = usePriorityDistribution();
    const { stats: actionableStats } = useActionableStats();
    const { messages, refetch: refetchMessages } = useMessages({ 
        exclude_spam: true, 
        min_priority: 0.3,
        limit: 10 
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="font-retro uppercase tracking-[0.3em]">Loading...</p>
                </div>
            </div>
        );
    }

    // Prepare priority distribution data for chart
    const priorityData = priorityDist ? [
        { name: 'High', value: priorityDist.high_priority, color: '#ff6b6b' },
        { name: 'Medium', value: priorityDist.medium_priority, color: '#ffe66d' },
        { name: 'Low', value: priorityDist.low_priority, color: '#4ecdc4' }
    ] : [];

    // Prepare spam type data for chart
    const spamTypeData = spamStats ? Object.entries(spamStats.spam_by_type).map(([type, count]) => ({
        name: type.charAt(0).toUpperCase() + type.slice(1),
        count
    })) : [];

    return (
        <div className="flex flex-col gap-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold font-retro">Dashboard</h1>
                <div className="text-sm font-bold bg-background border-2 border-black px-3 py-1 shadow-retro-sm">
                    {new Date().toLocaleDateString()}
                </div>
            </div>

            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard 
                    title="New Messages" 
                    value={stats?.new_messages_count.toString() || '0'} 
                    icon={Mail} 
                    trend="+24h"
                    color="bg-blue-200"
                />
                <StatCard 
                    title="Pending Drafts" 
                    value={stats?.pending_drafts_count.toString() || '0'} 
                    icon={MessageSquare} 
                    trend="Awaiting"
                    color="bg-yellow-200"
                />
                <StatCard 
                    title="Today's Tasks" 
                    value={stats?.actionables_today_count.toString() || '0'} 
                    icon={Activity} 
                    trend="Due Today"
                    color="bg-green-200"
                />
                <StatCard 
                    title="Spam Filtered" 
                    value={spamStats?.total_spam_count.toString() || '0'} 
                    icon={Shield} 
                    trend={`${spamStats?.spam_percentage.toFixed(1) || '0'}%`}
                    color="bg-red-200"
                />
            </div>

            {/* Priority Distribution & Spam Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Priority Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px] w-full flex items-center justify-center">
                            {priorityData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={priorityData}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            label={({ name, value }) => `${name}: ${value}`}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            dataKey="value"
                                            stroke="hsl(var(--border))"
                                            strokeWidth={2}
                                        >
                                            {priorityData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Pie>
                                        <Tooltip 
                                            contentStyle={{
                                                backgroundColor: 'hsl(var(--card))',
                                                color: 'hsl(var(--card-foreground))',
                                                border: '2px solid hsl(var(--border))',
                                                boxShadow: '4px 4px 0px 0px rgba(0,0,0,1)'
                                            }}
                                        />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <p className="text-muted-foreground">No data available</p>
                            )}
                        </div>
                        <div className="mt-4 text-center">
                            <p className="text-sm font-bold">
                                Average Priority: {priorityDist?.avg_priority.toFixed(2) || '0.00'}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Spam by Type</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px] w-full">
                            {spamTypeData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={spamTypeData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.2} />
                                        <XAxis 
                                            dataKey="name" 
                                            stroke="hsl(var(--border))" 
                                            tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }} 
                                        />
                                        <YAxis 
                                            stroke="hsl(var(--border))" 
                                            tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }} 
                                        />
                                        <Tooltip
                                            cursor={{ fill: 'transparent' }}
                                            contentStyle={{
                                                backgroundColor: 'hsl(var(--card))',
                                                color: 'hsl(var(--card-foreground))',
                                                border: '2px solid hsl(var(--border))',
                                                boxShadow: '4px 4px 0px 0px rgba(0,0,0,1)'
                                            }}
                                        />
                                        <Bar dataKey="count" fill="#ff6b6b" stroke="hsl(var(--border))" strokeWidth={2} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex items-center justify-center h-full">
                                    <p className="text-muted-foreground">No spam detected</p>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Recent Messages with Smart Replies */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent Messages - Review & Reply</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {messages && messages.length > 0 ? (
                            messages.slice(0, 5).map((message) => (
                                <MessageWithReplies 
                                    key={message.id} 
                                    message={message}
                                    onReplyUsed={refetchMessages}
                                />
                            ))
                        ) : (
                            <p className="text-muted-foreground text-center py-8">No messages to review</p>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Actionable Items & Spam Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Upcoming Deadlines</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {actionableStats?.upcoming_deadlines && actionableStats.upcoming_deadlines.length > 0 ? (
                                actionableStats.upcoming_deadlines.slice(0, 5).map((item) => (
                                    <div key={item.id} className="flex items-start gap-3 p-3 border-2 border-border bg-accent/10 dark:bg-accent/5">
                                        <AlertTriangle size={20} className="text-accent-foreground mt-1" />
                                        <div className="flex-1">
                                            <p className="font-bold text-sm">{item.description}</p>
                                            <p className="text-xs text-muted-foreground">
                                                Due: {new Date(item.deadline).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted-foreground text-center py-8">No upcoming deadlines</p>
                            )}
                        </div>
                        {actionableStats && actionableStats.upcoming_deadlines.length > 5 && (
                            <div className="mt-4 text-center">
                                <p className="text-sm text-muted-foreground">
                                    +{actionableStats.upcoming_deadlines.length - 5} more
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Recent Spam - Unsubscribe</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {spamStats?.recent_spam && spamStats.recent_spam.length > 0 ? (
                                spamStats.recent_spam.slice(0, 5).map((spam) => (
                                    <div key={spam.message_id} className="flex items-start gap-3 p-3 border-2 border-border bg-destructive/10 dark:bg-destructive/5">
                                        <Shield size={20} className="text-destructive mt-1 shrink-0" />
                                        <div className="flex-1 min-w-0">
                                            <p className="font-bold text-sm truncate">{spam.sender}</p>
                                            <p className="text-xs text-muted-foreground truncate">{spam.subject}</p>
                                            <span className="text-xs bg-destructive/20 dark:bg-destructive/10 border border-border px-2 py-0.5 mt-1 inline-block">
                                                {spam.spam_type}
                                            </span>
                                        </div>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={() => window.open(spam.unsubscribe_link, '_blank')}
                                            className="shrink-0"
                                        >
                                            <ExternalLink size={14} />
                                        </Button>
                                    </div>
                                ))
                            ) : (
                                <p className="text-muted-foreground text-center py-8">No spam with unsubscribe links</p>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};
