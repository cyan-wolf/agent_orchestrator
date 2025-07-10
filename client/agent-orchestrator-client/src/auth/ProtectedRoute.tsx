import type { ReactNode } from "react";
import { useAuth } from "./useAuth";
import { Navigate } from "react-router-dom";
import Loading from "../components/loading/Loading";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
    const { user, isLoading } = useAuth()!;

    if (isLoading) {
        return <Loading />;
    }
    else if (user === null) {
        return <Navigate to="/login" replace />;
    }
    return children;
}
