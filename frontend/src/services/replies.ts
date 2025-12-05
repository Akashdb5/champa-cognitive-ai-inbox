import api from './api';

export interface SmartReply {
    id: string;
    message_id: string;
    user_id: string;
    draft_content: string;
    status: 'pending' | 'approved' | 'rejected' | 'sent' | 'suggestion';
    created_at: string;
    reviewed_at?: string;
    sent_at?: string;
    // Message context
    message_subject?: string;
    message_sender?: string;
    message_platform?: string;
    message_preview?: string;
}

export interface SmartReplyRequest {
    message_id: string;
}

export interface SmartReplyApproval {
    approved: boolean;
}

export interface SmartReplyEdit {
    draft_content: string;
}

export interface SmartReplyRejection {
    reason?: string;
}

export interface SmartReplyResponse {
    id: string;
    status: string;
    message: string;
}

export const repliesApi = {
    async generateSmartReply(messageId: string): Promise<SmartReply> {
        const response = await api.post<SmartReply>('/api/replies/generate', {
            message_id: messageId,
        });
        return response.data;
    },

    async getPendingReplies(): Promise<SmartReply[]> {
        const response = await api.get<SmartReply[]>('/api/replies/pending');
        return response.data;
    },

    async getReply(replyId: string): Promise<SmartReply> {
        const response = await api.get<SmartReply>(`/api/replies/${replyId}`);
        return response.data;
    },

    async approveReply(replyId: string): Promise<SmartReplyResponse> {
        const response = await api.put<SmartReplyResponse>(`/api/replies/${replyId}/approve`, {
            approved: true,
        });
        return response.data;
    },

    async editReply(replyId: string, draftContent: string): Promise<SmartReply> {
        const response = await api.put<SmartReply>(`/api/replies/${replyId}/edit`, {
            draft_content: draftContent,
        });
        return response.data;
    },

    async rejectReply(replyId: string, reason?: string): Promise<SmartReplyResponse> {
        const response = await api.put<SmartReplyResponse>(`/api/replies/${replyId}/reject`, {
            reason,
        });
        return response.data;
    },
};

// Keep backward compatibility
export const replyService = repliesApi;
