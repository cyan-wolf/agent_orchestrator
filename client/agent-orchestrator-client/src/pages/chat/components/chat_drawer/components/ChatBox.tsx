import { useEffect, useState } from "react";
import Loading from "../../../../../components/loading/Loading";
import { Box, Stack, TextField } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import type { Message } from "../../messages/message";
import MessageList from "../../messages/MessageList";

type ChatBoxProps = {
    chatId: string
};

/**
 * Displays the chat box UI that allows the user to enter messages
 * and view the message history. Renders within the broader chat drawer UI.
 */
function ChatBoxDisplay({ chatId }: ChatBoxProps) {
    const [userMessage, setUserMessage] = useState("");
    const [latestMsgTimestamp, setLatestMsgTimestamp] = useState(0.0);
    const [messages, setMessages] = useState<Message[]>([]);

    const [waitingForServer, setWaitingForServer] = useState(true); 

    const navigate = useNavigate();

    useEffect(() => {
        const fetchChatHistory = async () => {
            const resp = await fetch(`/api/chat/${chatId}/history/`);
            const history = await resp.json();

            processMessages(history);

            setWaitingForServer(false);
        };
        fetchChatHistory();

        // The dependency on chatId on useEffect is required so that 
        // the component re-fetches the chat history whenever a parent component 
        // changes the chat ID.
    }, [chatId]);

    function processMessages(newMessages: Message[]) {
        if (newMessages.length > 0) {
            setLatestMsgTimestamp(newMessages.at(-1)!.timestamp);
        }
        setMessages([...messages, ...newMessages]);
    }

    async function fetchNewestChatMessages() {
        const resp = await fetch(`/api/chat/${chatId}/get-latest-messages/${latestMsgTimestamp}/`);
        const latestMessages: Message[] = await resp.json();

        processMessages(latestMessages);
    }

    async function submitUserMessage() {
        setWaitingForServer(true);
        const resp = await fetch(`/api/chat/${chatId}/send-message/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_message: userMessage,
            }),
        });
        if (!resp.ok) {
            if (resp.statusText === "Unauthorized") {
                // Force redirect to the login page, since the user's authentication expired.
                navigate("/login");
            }
            return;
        }

        setUserMessage("");
        setWaitingForServer(false);

        const respJson = await resp.json();
        console.log(respJson);  // this response does not contain useful info

        await fetchNewestChatMessages();
    }

    async function handleChatTextFieldKeyDown(e: React.KeyboardEvent<HTMLDivElement>) {
        // Do nothing if the client is waiting for the server to process the last message.
        if (waitingForServer) {
            e.preventDefault();
            return;
        }

        if (e.key === "Enter" && !e.shiftKey) {
            // Prevents cursor from moving to next line when pressing enter.
            e.preventDefault();

            submitUserMessage();
        }
    }

    return (
        <Box sx={{ p: { xs: 1, sm: 3 } }}>
            <Stack spacing={1} sx={{
                height: { xs: 'calc(100vh - 32px)', sm: '550px' }, // Responsive height
                width: '100%',
            }}>
                <Box
                    sx={{
                        border: '1px solid',
                        flexGrow: 1,

                        minWidth: 0,
                        maxWidth: '100%',
                        overflowX: 'hidden',

                        borderColor: 'primary.main', // Uses a color from your theme
                        borderRadius: '8px',
                        p: 2, // Adds padding for better visual spacing

                        overflowY: "auto", // Adds vertical scrollbar

                        // Custom scrollbar styling
                        scrollbarWidth: 'thin', 
                        scrollbarColor: 'rgba(0, 0, 0, 0.2) transparent',
                    }}
                >
                    <MessageList messages={messages} />
                </Box>
                <Box>
                    {(waitingForServer) ? <Loading /> : <></>}
                    <TextField 
                        fullWidth
                        multiline 
                        maxRows={4} 
                        variant="outlined"
                        placeholder="Type your message"
                        value={userMessage}
                        onChange={(e) => setUserMessage(e.target.value)}
                        onKeyDown={handleChatTextFieldKeyDown}
                        autoFocus

                        // Gives more space for the 'waiting for server' loading component.
                        sx={{
                            marginTop: '10px'
                        }}
                    />
                </Box>
            </Stack>
        </Box>
    );
}

/**
 * A wrapper around the `ChatBoxDisplay` component. This component 
 * reads the current URL to get the chat ID.
 */
export default function ChatBox() {
    // Read the chat ID from the URL.
    const { chatId } = useParams();

    return (
        // Load the actual chat box UI.
        //
        // Making the chat ID be part of the chat box display's key 
        // guarantees that the display re-renders when the chat ID changes.
        <ChatBoxDisplay chatId={chatId!} key={chatId} />
    );
}