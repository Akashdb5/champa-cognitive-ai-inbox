import api from './api';

export interface UserInfo {
    user_id: string;
    email: string;
    username: string;
}

export interface UserProfile {
    id: string;
    auth0_id: string;
    email: string;
    username: string;
    phone?: string;
    location?: string;
    timezone?: string;
    website?: string;
    created_at: string;
    updated_at: string;
}

export interface ProfileUpdateData {
    phone?: string;
    location?: string;
    timezone?: string;
    website?: string;
}

export const authService = {
    async logout(refreshToken?: string): Promise<void> {
        try {
            await api.post('/api/auth/logout', { refresh_token: refreshToken });
        } finally {
            localStorage.removeItem('access_token');
        }
    },

    async getCurrentUser(): Promise<UserInfo> {
        const response = await api.get<UserInfo>('/api/auth/me');
        return response.data;
    },

    async getUserProfile(): Promise<UserProfile> {
        const response = await api.get<UserProfile>('/api/auth/profile');
        return response.data;
    },

    async updateUserProfile(data: ProfileUpdateData): Promise<UserProfile> {
        const response = await api.patch<UserProfile>('/api/auth/profile', data);
        return response.data;
    },
};
