import { useAuth } from "../../auth/useAuth";
import Loading from "../../components/loading/Loading";
import { Alert, AlertTitle, Button, Card, CardContent, Container, Link, Paper, Typography } from "@mui/material";

export default function Logout() {
    const { user, logout, isLoading } = useAuth()!;

    if (isLoading) {
        return <Loading />;
    }

    function handleButtonClick() {
        logout();
    }

    const toLogoutView = (
        <Container maxWidth="sm">
            <Card>
                <CardContent sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center"
                }}>
                    <Typography variant="h3" align="center">Logout</Typography>
                    <Button 
                        variant="outlined" 
                        onClick={handleButtonClick}
                    >
                        Are you sure?
                    </Button>
                </CardContent>
            </Card>
        </Container>
    );
    
    const alreadyLoggedOutView = (
        <Container>
            <Paper>
                <Alert severity="error">
                    <AlertTitle>Already Logged Out</AlertTitle>
                    Cannot logout as you are not currently logged in. Please click <Link href="/login">here</Link> to login.
                </Alert>
            </Paper>
        </Container>
    );

    return (user !== null) ? toLogoutView : alreadyLoggedOutView;
}