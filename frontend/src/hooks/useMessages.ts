import { useState, useEffect } from 'react';
import { messagesApi, NormalizedMessage } from '../services/messages';

export type Message = NormalizedMessage;

export interface MessageAnalysis {
  message_id: string;
  summary: string;
  intent: string;
  priority_score: number;
  is_spam: boolean;
  spam_score: number;
  spam_type: string;
  actionable_items: Array<{
    id: string;
    type: string;
    description: string;
    deadline?: string;
    completed: boolean;
  }>;
}

export interface SmartReplySuggestion {
  id: string;
  draft_content: string;
  status: string;
  created_at: string;
}

export const useMessages = (filters?: {
  platform?: string;
  exclude_spam?: boolean;
  min_priority?: number;
  limit?: number;
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (filters?.platform) params.platform = filters.platform;
      if (filters?.exclude_spam !== undefined) params.exclude_spam = filters.exclude_spam;
      if (filters?.min_priority !== undefined) params.min_priority = filters.min_priority;
      if (filters?.limit) params.limit = filters.limit;
      
      const data = await messagesApi.getMessages(params);
      setMessages(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch messages');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [filters?.platform, filters?.exclude_spam, filters?.min_priority, filters?.limit]);

  return { messages, isLoading, error, refetch: fetchMessages };
};

export const useMessageAnalysis = (messageId: string | null) => {
  const [analysis, setAnalysis] = useState<MessageAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!messageId) {
      setAnalysis(null);
      return;
    }

    const fetchAnalysis = async () => {
      try {
        setIsLoading(true);
        const data = await messagesApi.getMessageAnalysis(messageId);
        setAnalysis(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch analysis');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [messageId]);

  return { analysis, isLoading, error };
};

export const useMessageReplies = (messageId: string | null) => {
  const [replies, setReplies] = useState<SmartReplySuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReplies = async () => {
    if (!messageId) {
      setReplies([]);
      return;
    }

    try {
      setIsLoading(true);
      const data = await messagesApi.getMessageReplies(messageId);
      setReplies(data.replies);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch replies');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReplies();
  }, [messageId]);

  return { replies, isLoading, error, refetch: fetchReplies };
};
