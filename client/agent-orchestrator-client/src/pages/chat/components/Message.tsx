import { Box, Paper, Typography } from "@mui/material";
import type { Message } from "../message";
import Markdown from "react-markdown";

type MessageComponentProps = {
    message: Message
};

export default function MessageComponent({ message }: MessageComponentProps) {
    // const date = (new Date(message.timestamp * 1000)).toISOString();

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
                    {message.agent_name}
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
    else {
        msgContent = <code>{JSON.stringify(message)}</code>
    }

    return msgContent;
}