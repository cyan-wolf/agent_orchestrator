import { useEffect, useState } from "react";
import type { Message } from "./message";
import MessageComponent from "./components/Message";
import Loading from "../../components/loading/Loading";

export default function Chat() {
    const [userMessage, setUserMessage] = useState("");
    const [latestMsgTimestamp, setLatestMsgTimestamp] = useState(0.0);
    const [messages, setMessages] = useState<Message[]>([]);
    const [waitingForServer, setWaitingForServer] = useState(false); 

    useEffect(() => {
        const fetchChatHistory = async () => {
            const resp = await fetch("/api/history/");
            const history = await resp.json();

            processMessages(history);
        };
        fetchChatHistory();
    }, []);

    function processMessages(newMessages: Message[]) {
        if (newMessages.length > 0) {
            setLatestMsgTimestamp(newMessages.at(-1)!.timestamp);
        }
        setMessages([...messages, ...newMessages]);
    }

    async function fetchNewestChatMessages() {
        const resp = await fetch(`/api/get-latest-messages/${latestMsgTimestamp}/`);
        const latestMessages: Message[] = await resp.json();

        processMessages(latestMessages);
    }

    async function handleChatSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        setWaitingForServer(true);
        const resp = await fetch("/api/send-message/", {
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

    return (
        <>
            <h1>Chat</h1>
            <div>
                {messages.map(m => <MessageComponent message={m} key={m.timestamp} />)}
            </div>
            <form onSubmit={handleChatSubmit}>
                {(waitingForServer) ? <Loading /> : <></>}
                <input 
                    type="text" 
                    id="chat-user-message"
                    value={userMessage}
                    readOnly={waitingForServer}
                    onChange={e => setUserMessage(e.target.value)}
                />
                <button type="submit" 
                    disabled={waitingForServer}
                >
                    Submit
                </button>
            </form>
        </>
    );
}