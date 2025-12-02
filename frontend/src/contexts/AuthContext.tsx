import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { authService, UserInfo } from '../services/auth';

interface AuthContextType {
    user: UserInfo | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { isAuthenticated: auth0IsAuthenticated, isLoading: auth0IsLoading, user: auth0User, getAccessTokenSilently } = useAuth0();
    const [user, setUser] = useState<UserInfo | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            if (auth0IsLoading) {
                return;
            }

            if (auth0IsAuthenticated && auth0User) {
                try {
                    // Get Auth0 token
                    const token = await getAccessTokenSilently();
                    localStorage.setItem('access_token', token);
                    
                    // Fetch user info from our backend
                    const userInfo = await authService.getCurrentUser();
                    setUser(userInfo);
                } catch (error) {
                    console.error('Failed to fetch user info:', error);
                    localStorage.removeItem('access_token');
                }
            } else {
                setUser(null);
                localStorage.removeItem('access_token');
            }
            
            setIsLoading(false);
        };

        initAuth();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [auth0IsAuthenticated, auth0IsLoading, auth0User]);

    const logout = async () => {
        await authService.logout();
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                isLoading: isLoading || auth0IsLoading,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
