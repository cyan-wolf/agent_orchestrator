import { useEffect, useState } from "react";
import Loading from "../../../../../components/loading/Loading";
import { Alert, AlertTitle, Box, Stack, TextField } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import type { Message } from "../../messages/message";
import MessageList from "../../messages/MessageList";
import { useChatContext } from "../../../Chat";
import type { ChatJson } from "../chat";

type ChatBoxProps = {
    chat: ChatJson
};

/**
 * Displays the chat box UI that allows the user to enter messages
 * and view the message history. Renders within the broader chat drawer UI.
 */
function ChatBoxDisplay({ chat }: ChatBoxProps) {
    const [userMessage, setUserMessage] = useState("");
    const [latestMsgTimestamp, setLatestMsgTimestamp] = useState(0.0);
    const [messages, setMessages] = useState<Message[]>([]);

    const [waitingForServer, setWaitingForServer] = useState(true); 

    const { excludeFilters, currentChatRefreshToggle } = useChatContext()!;

    const navigate = useNavigate();

    useEffect(() => {
        // Reset the chat state since it might still be lingering.
        // This effect fires whenever the chat is told to refresh, to ensure 
        // that it is actually refreshed, the state must be reset.
        const resetTimestamp = 0.0;
        resetChatState(resetTimestamp);

        const controller = new AbortController();
        const signal = controller.signal;

        const fetchChatHistory = async () => {
            // This always fetches the entire history for this chat.
            await fetchNewestChatMessages(resetTimestamp, signal);

            setWaitingForServer(false);
        };
        fetchChatHistory();

        // Cleanup function. Required to avoid state issues with React.
        return () => {
            controller.abort();
        };

        // The dependency on chatId on useEffect is required so that 
        // the component re-fetches the chat history whenever a parent component 
        // changes the chat ID.
    }, [chat.id, currentChatRefreshToggle]);

    function resetChatState(resetTimestamp: number) {
        setWaitingForServer(true);
        setMessages([]);
        setLatestMsgTimestamp(resetTimestamp);
    }

    function processMessages(newMessages: Message[]) {
        if (newMessages.length > 0) {
            setLatestMsgTimestamp(newMessages.at(-1)!.timestamp);
        }
        setMessages(prevMessages => [...prevMessages, ...newMessages]);
    }

    function buildChatMessageExcludeFilterQueryUrlParams() {
        if (excludeFilters.length === 0) {
            return "";
        }

        const excludeFilterQueries = new URLSearchParams();
        for (const filter of excludeFilters) {
            excludeFilterQueries.append("exclude_filters", filter);
        }
        
        return `?${excludeFilterQueries.toString()}`;
    }

    function buildFetchNewstMessagesUrl(timestamp: number) {
        const basePath = `/api/chat/${chat.id}/get-latest-messages/${timestamp}/`;
        const excludeFilterParams = buildChatMessageExcludeFilterQueryUrlParams();

        return `${basePath}${excludeFilterParams}`;
    }

    async function fetchNewestChatMessages(timestamp: number, abortSignal?: AbortSignal) {
        const fetchUrl = buildFetchNewstMessagesUrl(timestamp);

        const resp = await fetch(fetchUrl, { signal: abortSignal });
        const latestMessages: Message[] = await resp.json();

        processMessages(latestMessages);
    }

    async function submitUserMessage() {
        setWaitingForServer(true);
        const resp = await fetch(`/api/chat/${chat.id}/send-message/`, {
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

        await fetchNewestChatMessages(latestMsgTimestamp);
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
        <Box sx={{ p: { xs: 1, sm: 3 }, height: '100%' }}>
            <Stack spacing={1} sx={{
                // Width and height are determined by the outermost parent component, 
                // which in this case is the `Box` component in the `ChatDrawer` which holds its children.
                height: '100%',
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
    const [chat, setChat] = useState<ChatJson | null | undefined>();

    useEffect(() => {
        const fetchChat = async () => {
            const resp = await fetch(`/api/chat/${chatId}/info/`);
            if (!resp.ok) {
                setChat(null);
                return;
            }
            const chatInfo: ChatJson = await resp.json();
            setChat(chatInfo);
        };
        fetchChat();

    }, [chatId]);

    let content;

    // Chat data fetching failed.
    if (chat === null) {
        content = (
            <Alert severity="error">
                <AlertTitle>Error Loading Chat</AlertTitle>
                Could not fetch chat with ID {chatId}.
            </Alert>
        );
    }
    // No chat data has been loaded yet.
    else if (chat === undefined) {
        content = <Loading />;
    }
    // Chat data was able to be fetched.
    else {
        content = (
            // Load the actual chat box UI.
            //
            // Making the chat ID be part of the chat box display's key 
            // guarantees that the display re-renders when the chat ID changes.
            <ChatBoxDisplay chat={chat} key={chatId} />
        );
    }
    return content;
}