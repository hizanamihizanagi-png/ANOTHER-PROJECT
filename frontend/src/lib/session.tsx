"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface UserSession {
    userId: string | null;
    displayName: string | null;
    referralCode: string | null;
}

const SESSION_KEY = "scorai_session";

const SessionCtx = createContext<{
    session: UserSession;
    setSession: (s: UserSession) => void;
    clearSession: () => void;
}>({
    session: { userId: null, displayName: null, referralCode: null },
    setSession: () => { },
    clearSession: () => { },
});

export function SessionProvider({ children }: { children: ReactNode }) {
    const [session, setSessionState] = useState<UserSession>({
        userId: null,
        displayName: null,
        referralCode: null,
    });

    // Load from localStorage on mount
    useEffect(() => {
        try {
            const raw = localStorage.getItem(SESSION_KEY);
            if (raw) setSessionState(JSON.parse(raw));
        } catch { /* ignore */ }
    }, []);

    const setSession = (s: UserSession) => {
        setSessionState(s);
        localStorage.setItem(SESSION_KEY, JSON.stringify(s));
    };

    const clearSession = () => {
        setSessionState({ userId: null, displayName: null, referralCode: null });
        localStorage.removeItem(SESSION_KEY);
    };

    return (
        <SessionCtx.Provider value={{ session, setSession, clearSession }}>
            {children}
        </SessionCtx.Provider>
    );
}

export function useSession() {
    return useContext(SessionCtx);
}
