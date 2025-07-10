import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser, type User } from "./user";

type AuthData = {
    user: User | null,
    isLoading: boolean,
    login: (data: User) => void,
    logout: () => void,
};

const AuthContext = createContext<AuthData | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            const user = await getCurrentUser();
            setUser(user);
            setIsLoading(false);
        };
        fetchUser();
    }, [navigate]);

    const login = (data: User) => {
        setUser(data);
        navigate("/profile");
    };

    const logout = () => {
        setUser(null);

        fetch("/api/logout");

        navigate("/", { replace: true });
    };

    const value = {
        user,
        isLoading,
        login,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
