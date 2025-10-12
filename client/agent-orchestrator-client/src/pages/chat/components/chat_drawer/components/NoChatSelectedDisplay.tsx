import { Alert, Card, CardContent, Container, Typography, useMediaQuery, useTheme } from "@mui/material";

export default function NoChatSelectedDisplay() {
    const theme = useTheme();

    function chatDrawerIsOpenByDefault(): boolean {
        const isMobile = useMediaQuery(theme.breakpoints.down('md'));
        return !isMobile;
    }

    const chatDrawerOpenByDefault = chatDrawerIsOpenByDefault();
    const extraMessageContentWhenModalNotVisibleByDefault = (chatDrawerOpenByDefault) ? <></> :
        <Alert severity="info">
            You must open the drawer on the left hand side first.
        </Alert>;

    return (
        <Container maxWidth="sm">
            <Card>
                <CardContent sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center"
                }}>
                    <Typography variant="h3" align="center">No Chat Selected</Typography>

                    {extraMessageContentWhenModalNotVisibleByDefault}

                    <Typography variant="body1" align="center" mt={2}>
                        To create a new chat, click on the Create New Chat button. Otherwise, 
                        select an existing chat.
                    </Typography>

                </CardContent>
            </Card>

        </Container>
    );
}

