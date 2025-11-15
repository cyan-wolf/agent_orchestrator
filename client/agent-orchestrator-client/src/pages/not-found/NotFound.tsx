import { Alert, Button, Card, CardContent, Container, Stack, Typography } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";


export default function NotFound() {
    const location = useLocation();
    const navigate = useNavigate();

    return (
        <Container maxWidth="sm">
            <Card>
                <CardContent sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center"
                }}>
                    <Stack spacing={4}>
                        <Typography variant="h3" align="center">Not Found</Typography>
                        
                        <Alert severity="error">
                            Page '{location.pathname}' was not found.
                        </Alert>

                        <Button
                            variant="outlined"
                            onClick={() => {
                                navigate("/");
                            }}
                        >
                            Go Back to Home Page
                        </Button>
                    </Stack>
                </CardContent>

            </Card>
        </Container>
    );
}