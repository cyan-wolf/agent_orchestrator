import { useEffect, useState } from "react";
import ChatBox from "./components/ChatBox";

type ChatJson = {
    chat_id: string
};

type ChatSelectProps = {
    onSelectChat: (chatId: string) => void
};

function PlaceholderChatSelect({ onSelectChat }: ChatSelectProps) {
    const [chats, setChats] = useState<ChatJson[]>([]);

    useEffect(() => {
        const fetchChatIds = async () => {
            const resp = await fetch("/api/chat/get-all-chats/");
            const chatJson = await resp.json();

            setChats(chatJson);
        };
        fetchChatIds();
    });

    async function handleCreateNewChat() {
        const resp = await fetch("/api/chat/create/", {
            method: "POST"
        });

        const chatJson: ChatJson = await resp.json();

        onSelectChat(chatJson.chat_id);
    }

    return (
        <div>
            <h1>Select a chat:</h1>
            <ul>
                {chats.map(c => (
                    <li key={c.chat_id}>
                        <button
                            onClick={() => onSelectChat(c.chat_id)}
                        >
                            {c.chat_id}
                        </button>
                    </li>
                ))}
            </ul>
            <button onClick={handleCreateNewChat}>
                Create New Chat
            </button>
        </div>
    );
}

export default function Chat() {
    const [selectedChatId, setSelectedChatId] = useState<string | null>(null);

    function handleChatSelect(chatId: string) {
        setSelectedChatId(chatId);
    }

    if (selectedChatId !== null) {
        return <ChatBox chatId={selectedChatId} />;
    }
    else {
        return <PlaceholderChatSelect onSelectChat={handleChatSelect}/>;
    }
}
