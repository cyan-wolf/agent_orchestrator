import { useState } from "react";
import { getCurrentUser } from "../../auth/user";
import { useAuth } from "../../auth/useAuth";
import Loading from "../../components/loading/Loading";
import { Alert, AlertTitle, Button, Card, CardContent, Container, Paper, TextField, Typography } from "@mui/material";
import { Link } from "react-router-dom";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { isLoading, user, login } = useAuth()!;

    const [userNameValidationErrorMsg, setUserNameValidationErrorMsg] = useState("");
    const [passwordValidationErrorMsg, setPasswordValidationErrorMsg] = useState("");
    const [formErrorMessage, setFormErrorMessage] = useState("");

    if (isLoading) {
        return <Loading />;
    }

    function validateUsernameOnClient(): boolean {
        if (username.trim().length == 0) {
            setUserNameValidationErrorMsg("Username cannot be empty.");
            return false;
        }
        setUserNameValidationErrorMsg("");
        return true;
    }

    function validatePasswordOnClient(): boolean {
        if (password.trim().length < 8) {
            setPasswordValidationErrorMsg("Password is too short.");
            return false;
        }
        setPasswordValidationErrorMsg("");
        return true;
    }

    async function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        // Needed for 'application/x-www-form-urlencoded'.
        const formData = new URLSearchParams({
            username, password
        });

        if (!validateUsernameOnClient() || !validatePasswordOnClient()) {
            // Invalid form fields.
            return;
        }

        try {
            const response = await fetch("/api/token/", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                if (response.statusText === "Unauthorized") {
                    setFormErrorMessage("Could not complete authentication. Invalid credentials.");
                }
                else {
                    console.log(response);
                }
                return;
            }
            setFormErrorMessage("");

            const user = await getCurrentUser();
            // Login the user. The user cannot be null, as we have just logged in.
            login(user!);
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
                    Try <Link to="/logout">logging out</Link> if you meant to login as another user.
                </Alert>
            </Paper>
        </Container>
    );

    const toLoginView = (
        <Container maxWidth="sm">
            <Card>
                <CardContent sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center"
                }}>
                    <form onSubmit={handleFormSubmit}>
                        <Typography variant="h3" align="center">Log In</Typography>
                        <TextField 
                            label="Username"
                            type="text"
                            value={username}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setUsername(e.target.value)}
                            helperText={userNameValidationErrorMsg}
                        />
                        <TextField 
                            label="Password"
                            type="password"
                            value={password}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setPassword(e.target.value)}
                            helperText={passwordValidationErrorMsg}
                        />
                        <Button
                            sx={{ display: "block" }}
                            variant="outlined"
                            type="submit"
                            fullWidth
                        >
                            Login
                        </Button>
                    </form>
                    {(formErrorMessage.length !== 0) ? 
                        <Alert severity="error">
                            <AlertTitle>Authentication Error</AlertTitle>
                            {formErrorMessage}
                        </Alert> 
                        : <></>}
                </CardContent>
            </Card>
        </Container>
    );

    return (user !== null) ? alreadyLoggedInView : toLoginView;
}

export default Login;