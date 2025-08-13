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

    const [usernameErrMsg, setUsernameErrMsg] = useState("");
    const [emailErrMsg, setEmailErrMsg] = useState("");
    const [fullNameErrMsg, setFullNameErrMsg] = useState("");
    const [passwordErrMsg, setPasswordErrMsg] = useState("");
    const [formErrMsg, setFormErrMsg] = useState("");

    if (isLoading) {
        return <Loading />;
    }

    function validateUsername(): boolean {
        if (username.trim().length === 0) {
            setUsernameErrMsg("Username cannot be empty.");
            return false;
        }
        setUsernameErrMsg("");
        return true;
    }

    function validateEmail(): boolean {
        if (email.trim().length === 0) {
            setEmailErrMsg("Email cannot be empty.");
            return false;
        }
        setEmailErrMsg("");
        return true;
    }

    function validateFullname(): boolean {
        if (fullName.trim().length === 0) {
            setFullNameErrMsg("Full name cannot be empty.");
            return false;
        }
        setFullNameErrMsg("");
        return true;
    }

    function validatePassword(): boolean {
        if (password.trim().length === 0) {
            setPasswordErrMsg("Password cannot be empty.");
            return false;
        }
        setPasswordErrMsg("");
        return true;
    }

    async function handleFormSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        if (!validateUsername() || !validateEmail() || !validateFullname() || !validatePassword()) {
            return;
        }

        try {
            const response = await fetch("/api/register/", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username.trim(),
                    email: email.trim(),
                    fullName: fullName.trim(),
                    password: password.trim(),
                }),
            });

            if (!response.ok) {
                const detailBody = await response.json();
                // NOTE: It may be dangerous to assume this detail field exists.
                setFormErrMsg(detailBody.detail);
                return;
            }

            const user = await getCurrentUser();
            
            // Login the user; must exist since the API returned a successful response.
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
                    Try <Link to="/logout">logging out</Link> if you meant to register as another user.
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
                        <Typography variant="h3" align="center">Register</Typography>
                        <TextField 
                            label="Username"
                            type="text"
                            value={username}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setUsername(e.target.value)}
                            helperText={usernameErrMsg}
                        />
                        <TextField 
                            label="Email"
                            type="text"
                            value={email}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setEmail(e.target.value)}
                            helperText={emailErrMsg}
                        />
                        <TextField 
                            label="Full Name"
                            type="text"
                            value={fullName}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setFullName(e.target.value)}
                            helperText={fullNameErrMsg}
                        />
                        <TextField 
                            label="Password"
                            type="password"
                            value={password}
                            sx={{ display: "block" }}
                            margin="normal"
                            onChange={e => setPassword(e.target.value)}
                            helperText={passwordErrMsg}
                        />
                        <Button
                            sx={{ display: "block" }}
                            variant="outlined"
                            type="submit"
                            fullWidth
                        >
                            Register
                        </Button>
                    </form>
                </CardContent>
            </Card>
            {(formErrMsg.length !== 0) ? 
                <Alert severity="error">
                    <AlertTitle>Server Error</AlertTitle>
                    {formErrMsg}
                </Alert> 
                : <></>}
        </Container>
    );

    return (user !== null) ? alreadyLoggedInView : toLoginView;
}