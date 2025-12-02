import api from './api';

export interface OverviewStats {
    new_messages_count: number;
    pending_drafts_count: number;
    actionables_today_count: number;
    total_messages: number;
    connected_platforms: string[];
}

export interface SpamStats {
    total_spam_count: number;
    spam_by_type: Record<string, number>;
    spam_percentage: number;
    recent_spam: Array<{
        message_id: string;
        sender: string;
        subject: string;
        spam_type: string;
        spam_score: number;
        unsubscribe_link: string;
        timestamp: string;
    }>;
}

export interface PriorityDistribution {
    high_priority: number;
    medium_priority: number;
    low_priority: number;
    avg_priority: number;
}

export interface ActionableStats {
    total_actionables: number;
    completed_count: number;
    pending_count: number;
    overdue_count: number;
    by_type: Record<string, number>;
    upcoming_deadlines: Array<{
        id: string;
        description: string;
        type: string;
        deadline: string;
        message_id: string;
    }>;
}

export const statsService = {
    async getOverviewStats(): Promise<OverviewStats> {
        const response = await api.get('/api/stats/overview');
        return response.data;
    },

    async getSpamStats(): Promise<SpamStats> {
        const response = await api.get('/api/stats/spam');
        return response.data;
    },

    async getPriorityDistribution(): Promise<PriorityDistribution> {
        const response = await api.get('/api/stats/priority-distribution');
        return response.data;
    },

    async getActionableStats(): Promise<ActionableStats> {
        const response = await api.get('/api/stats/actionables');
        return response.data;
    }
};
