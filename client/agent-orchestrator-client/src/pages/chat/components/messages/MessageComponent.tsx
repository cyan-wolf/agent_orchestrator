import { Alert, AlertTitle, Box, Paper, Typography } from "@mui/material";
import type { Message } from "./message";
import Markdown from "react-markdown";

type MessageComponentProps = {
    message: Message
};

/**
 * Component for rendering a message from the API.
 */
export default function MessageComponent({ message }: MessageComponentProps) {
    let msgContent;

    if (message.kind === "ai_message") {
        if (message.is_main_agent) {
            msgContent = (
                <Box>
                    <Typography 
                        style={{
                            fontWeight: "bold"
                        }} 
                        component="span"
                    >
                        {message.agent_name}
                    </Typography>
                    <Markdown>{message.content}</Markdown>
                </Box>
            );
        }
        else {
            msgContent = (
                <Alert severity="info">
                    <AlertTitle variant="h6">Helper Agent</AlertTitle>
                    <Typography 
                        component="span"
                        style={{
                            fontWeight: "bold"
                        }} 
                    >
                        {message.agent_name}
                    </Typography>
                    <Markdown>{message.content}</Markdown>
                </Alert>
            );
        }
    }
    else if (message.kind === "human_message") {
        msgContent = (
            <Box display="flex" justifyContent="flex-end">
                <Paper style={{ maxWidth: "40%", padding: "8px" }}>
                    <Typography style={{ wordBreak: "break-word" }}>
                        <Typography style={{fontWeight: "bold"}} component="span">
                            {message.username}
                        </Typography>: {message.content}
                    </Typography>
                </Paper>
            </Box>
        );
    }
    else if (message.kind === "image") {
        msgContent = (
            <Box sx={{ width: '50%', textAlign: 'center' }}>
                <img src={`data:image/jpeg;base64,${message.base64_encoded_image}`} alt={message.caption} style={{ maxWidth: '100%' }} />
                <Typography variant="caption" display="block" sx={{ color: 'text.secondary', marginTop: '4px' }}>
                    {message.caption}
                </Typography>
            </Box>
        );
    }
    else if (message.kind === "tool") {
        const dateObj = new Date(message.timestamp * 1000);
        const date = dateObj.toLocaleDateString();
        const time = dateObj.toLocaleTimeString();

        const args = JSON.stringify(message.bound_arguments, null, 4);

        const ToolLabel = ({ text }: { text: string }) => (
            <Typography component="span" style={{ fontWeight: "bold" }}>
                {text}
            </Typography>
        );

        msgContent = (
            <Alert severity="info">
                <AlertTitle variant="h6">Tool Call</AlertTitle>

                <Typography><ToolLabel text="Called By: "/>{message.called_by}</Typography>
                <Typography><ToolLabel text="Called At:"/> {date} : {time}</Typography>
                <Typography><ToolLabel text="Tool Name:"/> {message.name}</Typography>
                <Typography component="div">
                    <ToolLabel text="Arguments:"/>
                    <pre>
                        <code>{args}</code>
                    </pre>
                </Typography>
                <Typography><ToolLabel text="Return Value:"/> {message.return_value}</Typography>
            </Alert>
        );
    }
    else {
        // Placeholder rendering.
        msgContent = <code>{JSON.stringify(message)}</code>
    }

    return msgContent;
}