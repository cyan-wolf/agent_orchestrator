import { useState } from "react";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        console.log(`usr: ${username}`);
        // console.log(`pas: ${password}`);
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
