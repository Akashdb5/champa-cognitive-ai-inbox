import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollText, MessageCircle, Mail } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { usePendingReplies } from '../hooks/useReplies';
import { useState, useRef, useEffect } from 'react';

export const ChatPage = () => {
    const { messages, isLoading, error, sendMessage } = useChat();
    const { replies, approveReply, rejectReply } = usePendingReplies();
    const [inputMessage, setInputMessage] = useState('');
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isLoading) return;

        const message = inputMessage;
        setInputMessage('');
        await sendMessage(message);
    };

    const handleApproveReply = async (replyId: string) => {
        setActionLoading(replyId);
        try {
            await approveReply(replyId);
        } catch (err: any) {
            console.error('Failed to approve reply:', err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleRejectReply = async (replyId: string) => {
        setActionLoading(replyId);
        try {
            await rejectReply(replyId);
        } catch (err: any) {
            console.error('Failed to reject reply:', err);
        } finally {
            setActionLoading(null);
        }
    };

    const getPlatformIcon = () => {
        // In a real implementation, you'd look up the message to get its platform
        // For now, return a default icon
        return Mail;
    };

    return (
        <div className="space-y-8">
            <header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                    <p className="text-xs uppercase font-retro tracking-[0.4em] text-muted-foreground">Mission Console</p>
                    <h1 className="text-4xl font-retro uppercase tracking-tight">Chat & Orchestration</h1>
                    <p className="text-sm text-muted-foreground">
                        Ask questions about your messages, request smart replies, and manage AI-generated drafts.
                    </p>
                </div>
            </header>

            <Card className="border-2 border-black shadow-retro-md flex flex-col">
                <CardHeader className="border-b-2 border-black bg-card/70">
                    <CardTitle className="font-retro uppercase tracking-[0.3em] flex items-center gap-2">
                        <ScrollText size={18} /> Live Chat
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0 flex flex-col h-[600px]">
                    <div className="flex-1 p-6 space-y-6 overflow-y-auto">
                        {error && (
                            <div className="border-2 border-black bg-red-100 px-4 py-2 shadow-retro-xs">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        )}
                        
                        {messages.length === 0 && (
                            <div className="text-center py-12">
                                <MessageCircle size={48} className="mx-auto mb-4 text-muted-foreground" />
                                <p className="font-retro uppercase tracking-[0.3em] text-muted-foreground mb-2">
                                    Start a conversation
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    Try: "Show me my unread messages" or "Generate a reply for my latest email"
                                </p>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className="space-y-4 max-w-2xl w-full">
                                    <div
                                        className={`border-2 border-black px-4 py-3 shadow-retro-xs ${
                                            msg.role === 'user' ? 'bg-primary/20' : 'bg-muted'
                                        }`}
                                    >
                                        <p className="text-xs font-retro uppercase tracking-[0.3em] text-muted-foreground">
                                            {msg.role === 'user' ? 'You' : 'Champa AI'}
                                        </p>
                                        <p className="text-sm mt-1 whitespace-pre-wrap">{msg.content}</p>
                                    </div>

                                    {msg.role === 'assistant' && replies.length > 0 && idx === messages.length - 1 && (
                                        <section>
                                            <h2 className="font-retro uppercase tracking-[0.3em] text-xs mb-2">Pending Approvals</h2>
                                            <div className="space-y-3">
                                                {replies.map((reply) => {
                                                    const PlatformIcon = getPlatformIcon();
                                                    return (
                                                        <div key={reply.id} className="border-2 border-black p-4 shadow-retro-xs bg-background space-y-3">
                                                            <div className="flex items-center gap-3">
                                                                <div className="w-10 h-10 border-2 border-black shadow-retro-xs flex items-center justify-center bg-muted">
                                                                    <PlatformIcon size={18} />
                                                                </div>
                                                                <div>
                                                                    <p className="font-retro uppercase tracking-[0.2em]">Smart Reply</p>
                                                                    <p className="text-sm text-muted-foreground">Status: {reply.status}</p>
                                                                </div>
                                                            </div>
                                                            <p className="text-sm bg-muted px-3 py-2 border border-black whitespace-pre-wrap">
                                                                {reply.draft_content}
                                                            </p>
                                                            <div className="flex gap-2">
                                                                <Button
                                                                    className="border-2 border-black bg-green-400 shadow-retro-xs font-retro uppercase tracking-[0.2em] flex-1"
                                                                    onClick={() => handleApproveReply(reply.id)}
                                                                    disabled={actionLoading === reply.id}
                                                                >
                                                                    {actionLoading === reply.id ? 'Approving...' : 'Approve'}
                                                                </Button>
                                                                <Button
                                                                    variant="outline"
                                                                    className="border-2 border-black bg-red-400 shadow-retro-xs font-retro uppercase tracking-[0.2em] flex-1"
                                                                    onClick={() => handleRejectReply(reply.id)}
                                                                    disabled={actionLoading === reply.id}
                                                                >
                                                                    {actionLoading === reply.id ? 'Rejecting...' : 'Reject'}
                                                                </Button>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </section>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                    <div className="border-t-2 border-black p-4">
                        <form onSubmit={handleSendMessage} className="flex gap-3">
                            <Input
                                placeholder="Ask about your messages, request actions..."
                                className="flex-1 border-2 border-black shadow-retro-xs"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                disabled={isLoading}
                            />
                            <Button
                                type="submit"
                                className="border-2 border-black font-retro uppercase tracking-[0.2em]"
                                disabled={isLoading || !inputMessage.trim()}
                            >
                                {isLoading ? 'Sending...' : 'Send'}
                            </Button>
                        </form>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};
