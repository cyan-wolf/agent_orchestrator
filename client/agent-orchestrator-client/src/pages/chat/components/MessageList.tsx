import { Stack } from "@mui/material";
import type { Message } from "../message";
import MessageComponent from "./Message";
import { useEffect, useRef } from "react";

type MessageListProps = {
    messages: Message[]
};

const MessageList = ({ messages }: MessageListProps) => {
    const lastMsg = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Scrolls to the end of the message list.
        lastMsg.current!.scrollIntoView({ behavior: "smooth" });
    }, [messages]); // only scroll when the messages change

    return (
        <Stack 
            spacing={4} 
            style={{
                maxHeight: "100%",
                overflowY: "auto",
            }}
        >
            {messages.map(m => <MessageComponent message={m} key={m.timestamp} />)}
            
            {/* Marker for scrolling to the end of the message list. */}
            <div ref={lastMsg} />
        </Stack>
    );
};

export default MessageList;
