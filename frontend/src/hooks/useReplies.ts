import { useState, useEffect } from 'react';
import { replyService, SmartReply } from '../services/replies';

export const usePendingReplies = () => {
    const [replies, setReplies] = useState<SmartReply[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchReplies = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await replyService.getPendingReplies();
            setReplies(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch pending replies');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchReplies();
    }, []);

    const generateReply = async (messageId: string) => {
        try {
            const reply = await replyService.generateSmartReply(messageId);
            setReplies((prev) => [...prev, reply]);
            return reply;
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to generate reply');
        }
    };

    const approveReply = async (replyId: string) => {
        try {
            await replyService.approveReply(replyId);
            setReplies((prev) => prev.filter((r) => r.id !== replyId));
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to approve reply');
        }
    };

    const editReply = async (replyId: string, draftContent: string) => {
        try {
            const updatedReply = await replyService.editReply(replyId, draftContent);
            setReplies((prev) => prev.map((r) => (r.id === replyId ? updatedReply : r)));
            return updatedReply;
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to edit reply');
        }
    };

    const rejectReply = async (replyId: string, reason?: string) => {
        try {
            await replyService.rejectReply(replyId, reason);
            setReplies((prev) => prev.filter((r) => r.id !== replyId));
        } catch (err: any) {
            throw new Error(err.response?.data?.detail || 'Failed to reject reply');
        }
    };

    return {
        replies,
        isLoading,
        error,
        generateReply,
        approveReply,
        editReply,
        rejectReply,
        refetch: fetchReplies,
    };
};
