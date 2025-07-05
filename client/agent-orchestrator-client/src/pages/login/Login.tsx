import { useState } from "react";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

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
        }
        catch (err) {
            console.log(err);
        }
    }

    return (
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
}
