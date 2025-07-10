import type { ReactNode } from "react";
import { useAuth } from "./useAuth";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
    const { user } = useAuth()!;

    if (user === null) {
        return <Navigate to="/login" replace />;
    }
    return children;
}
