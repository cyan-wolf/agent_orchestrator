import { Stack } from "@mui/material";
import type { Message } from "../message";
import MessageComponent from "./Message";

type MessageListProps = {
    messages: Message[]
};

const MessageList = ({ messages }: MessageListProps) => {
    return (
        <Stack spacing={4}>
            {messages.map(m => <MessageComponent message={m} key={m.timestamp} />)}
        </Stack>
    );
};

export default MessageList;
