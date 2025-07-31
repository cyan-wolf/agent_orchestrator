import { Stack } from "@mui/material";
import { useEffect, useRef } from "react";
import type { Message } from "./message";
import MessageComponent from "./MessageComponent";

type MessageListProps = {
    messages: Message[]
};

/**
 * Renders a message history as a vertical list of messages.
 */
export default function MessageList({ messages }: MessageListProps) {
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
            {messages.map(m => <MessageComponent message={m} key={m.trace_id} />)}
            
            {/* Marker for scrolling to the end of the message list. */}
            <div ref={lastMsg} />
        </Stack>
    );
};