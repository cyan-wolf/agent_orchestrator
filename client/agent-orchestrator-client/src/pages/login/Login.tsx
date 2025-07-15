import { useState } from "react";
import { getCurrentUser } from "../../auth/user";
import { useAuth } from "../../auth/useAuth";
import Loading from "../../components/loading/Loading";
import { Button, Card, CardContent, Container, TextField, Typography } from "@mui/material";

const Login = () => {
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

    // TODO: Make this look good.
    const alreadyLoggedInView = (
        <>
            <h2>Login</h2>
            <p>Already logged in!</p>
        </>
    );

    const toLoginView = (
        <form onSubmit={handleFormSubmit}>
            <Container maxWidth="sm">
                <Card>
                    <CardContent>
                        <Typography variant="h3" align="center">Log In</Typography>
                        <TextField 
                            label="Username"
                            type="text"
                            sx={{ display: "block" }}
                            onChange={e => setUsername(e.target.value)}
                        />
                        <TextField 
                            label="Password"
                            type="password"
                            sx={{ display: "block" }}
                            onChange={e => setPassword(e.target.value)}
                        />
                        <Button
                            sx={{ display: "block" }}
                            type="submit"
                        >
                            Login
                        </Button>
                    </CardContent>
                </Card>
            </Container>
        </form>
    );

    return (user !== null) ? alreadyLoggedInView : toLoginView;
}

export default Login;