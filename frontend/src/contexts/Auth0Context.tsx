import React, { ReactNode } from 'react';
import { Auth0Provider } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';

const auth0Domain = import.meta.env.VITE_AUTH0_DOMAIN;
const auth0ClientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
const auth0Audience = import.meta.env.VITE_AUTH0_AUDIENCE;
const redirectUri = import.meta.env.VITE_AUTH0_REDIRECT_URI || window.location.origin + '/callback';

export const Auth0ProviderWithNavigate: React.FC<{ children: ReactNode }> = ({ children }) => {
    const navigate = useNavigate();

    const onRedirectCallback = (appState: any) => {
        navigate(appState?.returnTo || '/dashboard');
    };

    if (!auth0Domain || !auth0ClientId) {
        throw new Error('Auth0 configuration is missing. Please set VITE_AUTH0_DOMAIN and VITE_AUTH0_CLIENT_ID in your .env file.');
    }

    return (
        <Auth0Provider
            domain={auth0Domain}
            clientId={auth0ClientId}
            authorizationParams={{
                redirect_uri: redirectUri,
                audience: auth0Audience,
                scope: "openid profile email offline_access"
            }}
            onRedirectCallback={onRedirectCallback}
            cacheLocation="localstorage"
            useRefreshTokens={true}
        >
            {children}
        </Auth0Provider>
    );
};
