import { useState } from "react";
import { getCurrentUser } from "../../auth/user";
import { useAuth } from "../../auth/useAuth";
import Loading from "../../components/loading/Loading";
import { Alert, AlertTitle, Button, Card, CardContent, Container, Paper, TextField, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export default function Register() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [fullName, setFullName] = useState("");
    const [password, setPassword] = useState("");
    const { isLoading, user, login } = useAuth()!;

    if (isLoading) {
        return <Loading />;
    }

    async function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        try {
            await fetch("/api/register/", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    email,
                    fullName,
                    password,
                }),
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

    const alreadyLoggedInView = (
        <Container>
            <Paper>
                <Alert severity="error">
                    <AlertTitle>Already Logged In</AlertTitle>
                    Cannot login as you are already logged in as user 
                    <Typography component="span" fontWeight="bold">{` ${user?.username}`}.</Typography>
                    Try <Link to="/logout">logging out</Link> if you meant to register as another user.
                </Alert>
            </Paper>
        </Container>
    );

    const toLoginView = (
        <form onSubmit={handleFormSubmit}>
            <Container maxWidth="sm">
                <Card>
                    <CardContent sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center"
                    }}>
                        <Typography variant="h3" align="center">Register</Typography>
                        <TextField 
                            label="Username"
                            type="text"
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setUsername(e.target.value)}
                        />
                        <TextField 
                            label="Email"
                            type="text"
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setEmail(e.target.value)}
                        />
                        <TextField 
                            label="Full Name"
                            type="text"
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setFullName(e.target.value)}
                        />
                        <TextField 
                            label="Password"
                            type="password"
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setPassword(e.target.value)}
                        />
                        <Button
                            sx={{ display: "block" }}
                            variant="outlined"
                            type="submit"
                            fullWidth
                        >
                            Register
                        </Button>
                    </CardContent>
                </Card>
            </Container>
        </form>
    );

    return (user !== null) ? alreadyLoggedInView : toLoginView;
}