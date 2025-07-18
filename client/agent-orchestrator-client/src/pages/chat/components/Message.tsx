import { Box, Paper, Typography } from "@mui/material";
import type { Message } from "../message";
import Markdown from "react-markdown";

type MessageComponentProps = {
    message: Message
};

export default function MessageComponent({ message }: MessageComponentProps) {
    let msgContent;

    if (message.kind === "ai_message") {
        msgContent = (
            <Box>
                <Typography 
                    style={{
                        fontWeight: (message.is_main_agent) ? "bold" : "normal"
                    }} 
                    component="span"
                >
                    {message.agent_name}{(message.is_main_agent) ? "" : " (helper agent)"}
                </Typography>
                <Markdown>{message.content}</Markdown>
            </Box>
        );
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
    else if (message.kind === "side_effect" && message.side_effect_kind === "image_generation") {
        msgContent = <p><img src={`data:image/jpeg;base64,${message.base64_encoded_image}`} width={"50%"} alt="AI generated image" /></p>
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
            <Paper>
                <Typography><ToolLabel text="Called At:"/> {date} : {time}</Typography>
                <Typography><ToolLabel text="Tool Name:"/> {message.name}</Typography>
                <Typography>
                    <ToolLabel text="Arguments:"/>
                    <pre>
                        <code>{args}</code>
                    </pre>
                </Typography>
                <Typography><ToolLabel text="Return Value:"/> {message.return_value}</Typography>
            </Paper>
        );
    }
    else {
        msgContent = <code>{JSON.stringify(message)}</code>
    }

    return msgContent;
}