import { useState, useEffect } from 'react';
import { chatService, ChatMessage } from '../services/chat';

export const useChat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const history = await chatService.getChatHistory();
                setMessages(history.messages);
            } catch (err: any) {
                console.error('Failed to load chat history:', err);
            }
        };

        loadHistory();
    }, []);

    const sendMessage = async (message: string) => {
        try {
            setIsLoading(true);
            setError(null);

            // Add user message immediately
            const userMessage: ChatMessage = {
                role: 'user',
                content: message,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, userMessage]);

            // Send to backend
            const response = await chatService.sendMessage(message);

            // Add assistant response
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: response.message,
                timestamp: response.timestamp,
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to send message');
            // Remove the user message if sending failed
            setMessages((prev) => prev.slice(0, -1));
        } finally {
            setIsLoading(false);
        }
    };

    const clearHistory = async () => {
        try {
            await chatService.clearChatHistory();
            setMessages([]);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to clear history');
        }
    };

    return { messages, isLoading, error, sendMessage, clearHistory };
};
