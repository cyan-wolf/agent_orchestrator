import { useState } from "react";
import { getCurrentUser } from "../../auth/user";
import { useAuth } from "../../auth/useAuth";
import Loading from "../components/loading/Loading";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { isLoading, user, login } = useAuth()!;

    if (isLoading) {
        return <Loading />;
    }

    async function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        // Needed for 'application/x-www-form-urlencoded'.
        const formData = new URLSearchParams({
            username, password
        });

        try {
            await fetch("/api/token/", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            const user = await getCurrentUser();
            
            if (user !== null) {
                // Login the user.
                login(user);
            }
            else {
                // TODO: authentication was not successful
            }

        }
        catch (err) {
            console.log(err);
        }
    }

    const toLoginView = (
        <>
            <h1>Login</h1>
            
            <form onSubmit={handleFormSubmit}>

                <label htmlFor="login-username">Username: </label>
                <input 
                    type="text" 
                    id="login-username"
                    onChange={e => setUsername(e.target.value)}
                />

                <label htmlFor="login-password">Password: </label>
                <input 
                    type="password"
                    id="login-password"
                    onChange={e => setPassword(e.target.value)}
                    />

                <button type="submit">Login</button>
            </form>
        </>
    );

    const alreadyLoggedInView = (
        <>
            <h2>Login</h2>
            <p>Already logged in!</p>
        </>
    );

    return (user !== null) ? alreadyLoggedInView : toLoginView;
}
