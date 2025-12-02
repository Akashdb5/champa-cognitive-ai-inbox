import api from './api';

export interface PlatformStatus {
    gmail: boolean;
    slack: boolean;
    calendar: boolean;
}

export interface PlatformConnectionResponse {
    platform: string;
    status: string; // 'pending', 'connected', 'disconnected'
    message: string;
    redirect_url?: string; // OAuth redirect URL for user authorization
    connection_request_id?: string; // Temporary ID for pending connections
}

export interface TokenStatus {
    status: string;
    message: string;
    expires_at?: string;
}

export const platformService = {
    async getPlatformStatus(): Promise<PlatformStatus> {
        const response = await api.get<PlatformStatus>('/api/platforms/');
        return response.data;
    },

    async getAuthUrl(platform: string): Promise<PlatformConnectionResponse> {
        const response = await api.get<PlatformConnectionResponse>(
            `/api/platforms/${platform}/auth-url`
        );
        return response.data;
    },

    async disconnectPlatform(platform: string): Promise<PlatformConnectionResponse> {
        const response = await api.delete<PlatformConnectionResponse>(`/api/platforms/${platform}/disconnect`);
        return response.data;
    },

    async refreshPlatformToken(platform: string): Promise<{ message: string }> {
        const response = await api.post<{ message: string }>(`/api/platforms/${platform}/refresh`);
        return response.data;
    },

    async getTokenStatus(platform: string): Promise<TokenStatus> {
        const response = await api.get<TokenStatus>(`/api/platforms/${platform}/token-status`);
        return response.data;
    },
};
