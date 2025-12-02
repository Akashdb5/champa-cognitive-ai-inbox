import api from './api';

export interface NormalizedMessage {
    id: string;
    user_id: string;
    platform: string;
    platform_message_id: string;
    sender: string;
    content: string;
    subject?: string;
    timestamp: string;
    thread_id?: string;
    metadata: Record<string, any>;
}

export interface MessageFilters {
    platform?: string;
    start_date?: string;
    end_date?: string;
    exclude_spam?: boolean;
    min_priority?: number;
    limit?: number;
    offset?: number;
}

export interface ThreadContext {
    thread_id: string;
    messages: NormalizedMessage[];
    participant_count: number;
}

export interface MessageSearchRequest {
    query: string;
    limit?: number;
}

export interface MessageSearchResponse {
    query: string;
    results: NormalizedMessage[];
    total_count: number;
}

export const messagesApi = {
    async getMessages(filters?: MessageFilters): Promise<NormalizedMessage[]> {
        const params = new URLSearchParams();
        if (filters?.platform) params.append('platform', filters.platform);
        if (filters?.start_date) params.append('start_date', filters.start_date);
        if (filters?.end_date) params.append('end_date', filters.end_date);
        if (filters?.exclude_spam !== undefined) params.append('exclude_spam', filters.exclude_spam.toString());
        if (filters?.min_priority !== undefined) params.append('min_priority', filters.min_priority.toString());
        if (filters?.limit) params.append('limit', filters.limit.toString());
        if (filters?.offset) params.append('offset', filters.offset.toString());

        const response = await api.get<NormalizedMessage[]>(`/api/messages?${params.toString()}`);
        return response.data;
    },

    async getMessage(messageId: string): Promise<NormalizedMessage> {
        const response = await api.get<NormalizedMessage>(`/api/messages/${messageId}`);
        return response.data;
    },

    async getMessageThread(messageId: string): Promise<ThreadContext> {
        const response = await api.get<ThreadContext>(`/api/messages/${messageId}/thread`);
        return response.data;
    },

    async searchMessages(request: MessageSearchRequest): Promise<MessageSearchResponse> {
        const response = await api.post<MessageSearchResponse>('/api/messages/search', request);
        return response.data;
    },

    async getMessageAnalysis(messageId: string): Promise<any> {
        const response = await api.get(`/api/messages/${messageId}/analysis`);
        return response.data;
    },

    async getMessageReplies(messageId: string): Promise<any> {
        const response = await api.get(`/api/messages/${messageId}/replies`);
        return response.data;
    },

    async useSuggestion(suggestionId: string): Promise<any> {
        const response = await api.post(`/api/replies/suggestions/${suggestionId}/use`);
        return response.data;
    },

    async deleteSuggestion(suggestionId: string): Promise<any> {
        const response = await api.delete(`/api/replies/suggestions/${suggestionId}`);
        return response.data;
    },
};

// Keep backward compatibility
export const messageService = messagesApi;
