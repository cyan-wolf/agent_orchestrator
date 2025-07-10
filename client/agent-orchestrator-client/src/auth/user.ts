
export type User = {
    username: string,
};

export async function getCurrentUser(): Promise<User | null> {
    try {
        const resp = await fetch("/api/auth-check/");

        const payload = await resp.json();

        if (typeof(payload) === "object" && payload !== null) {
            const { user } = payload;
            return user;
        }
        return null;
    }
    catch (err) {
        console.error(err);
        return null;
    }
}