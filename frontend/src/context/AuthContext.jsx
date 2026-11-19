import {
    useCallback,
    useEffect,
    useState,
} from "react";

import { AuthContext } from "./auth";

function decodeToken(token) {
    try {
        if (!token || typeof token !== "string") {
            return null;
        }

        const parts = token.split(".");

        if (parts.length !== 3) {
            return null;
        }

        const base64 = parts[1]
            .replace(/-/g, "+")
            .replace(/_/g, "/");

        const padded = base64.padEnd(
            Math.ceil(base64.length / 4) * 4,
            "="
        );

        const payload = JSON.parse(atob(padded));

        if (
            !Number.isInteger(payload.user_id) ||
            payload.user_id <= 0 ||
            typeof payload.role !== "string" ||
            typeof payload.exp !== "number" ||
            payload.exp <= Date.now() / 1000
        ) {
            return null;
        }

        return payload;
    } catch {
        return null;
    }
}

function getInitialSession() {
    const storedToken = localStorage.getItem("token");

    if (!storedToken) {
        return { token: null, user: null };
    }

    const decodedUser = decodeToken(storedToken);

    if (!decodedUser) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        return { token: null, user: null };
    }

    return {
        token: storedToken,
        user: decodedUser,
    };
}

export function AuthProvider({ children }) {
    const [session, setSession] = useState(getInitialSession);

    const logout = useCallback(() => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        setSession({
            token: null,
            user: null,
        });
    }, []);

    const login = (accessToken) => {
        const decodedUser = decodeToken(accessToken);

        if (!decodedUser) {
            throw new Error("Invalid or expired access token.");
        }

        localStorage.setItem("token", accessToken);

        setSession({
            token: accessToken,
            user: decodedUser,
        });
    };

    // Subscribe to the expiry timer.
    useEffect(() => {
        if (!session.user?.exp) {
            return;
        }

        const remainingTime =
            session.user.exp * 1000 - Date.now();

        const timeoutId = setTimeout(() => {
            logout();
        }, Math.max(remainingTime, 0));

        return () => clearTimeout(timeoutId);
    }, [session.token, session.user, logout]);

    // Subscribe to unauthorized API responses.
    useEffect(() => {
        window.addEventListener("auth:logout", logout);

        return () => {
            window.removeEventListener("auth:logout", logout);
        };
    }, [logout]);

    return (
        <AuthContext.Provider
            value={{
                token: session.token,
                user: session.user,
                login,
                logout,
                isAuthenticated: Boolean(
                    session.token && session.user
                ),
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}