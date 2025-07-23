import { useEffect, useState } from "react";
import type { Message } from "../message";
import Loading from "../../../components/loading/Loading";
import { Box, Container, TextField } from "@mui/material";
import MessageList from "./MessageList";
import { useParams } from "react-router-dom";

type ChatBoxProps = {
    chatId: string
};

function ChatBoxDisplay({ chatId }: ChatBoxProps) {
    const [userMessage, setUserMessage] = useState("");
    const [latestMsgTimestamp, setLatestMsgTimestamp] = useState(0.0);
    const [messages, setMessages] = useState<Message[]>([]);

    const [waitingForServer, setWaitingForServer] = useState(true); 

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
        <Container>
            <Box
                sx={{
                    height: { xs: 'calc(100vh - 32px)', sm: '550px' }, // Responsive height
                }}
            >
                <MessageList messages={messages} />
            </Box>

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
            />
        </Container>
    );
}

export default function ChatBox() {
    const { chatId } = useParams();

    return (
        <ChatBoxDisplay chatId={chatId!} />
    );
}