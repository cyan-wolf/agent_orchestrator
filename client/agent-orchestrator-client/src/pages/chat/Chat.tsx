import { useEffect, useState } from "react";

export default function Chat() {
    const [userMessage, setUserMessage] = useState("");

    useEffect(() => {
        const fetchChatHistory = async () => {
            const resp = await fetch("/api/history/");
            const history = await resp.json();

            console.log(history);
        };
        fetchChatHistory();
    });

    async function handleChatSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

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

        const respJson = await resp.json();
        console.log(respJson);
    }

    return (
        <>
            <h1>Chat</h1>
            <form onSubmit={handleChatSubmit}>
                <input 
                    type="text" 
                    id="chat-user-message"
                    value={userMessage}
                    onChange={e => setUserMessage(e.target.value)}
                />
                <button type="submit">Submit</button>
            </form>
        </>
    );
}