import api from './api';

export interface ChatRequest {
    message: string;
}

export interface ChatResponse {
    message: string;
    timestamp: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface ChatHistory {
    messages: ChatMessage[];
    user_id: string;
    total_count: number;
}

export const chatService = {
    async sendMessage(message: string): Promise<ChatResponse> {
        const response = await api.post<ChatResponse>('/api/chat/message', { message });
        return response.data;
    },

    async getChatHistory(limit: number = 50): Promise<ChatHistory> {
        const response = await api.get<ChatHistory>(`/api/chat/history?limit=${limit}`);
        return response.data;
    },

    async clearChatHistory(): Promise<{ message: string }> {
        const response = await api.delete<{ message: string }>('/api/chat/history');
        return response.data;
    },
};
