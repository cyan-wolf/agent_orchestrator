import type { Message } from "../message";
import Markdown from "react-markdown";

type MessageComponentProps = {
    message: Message
};

export default function MessageComponent({ message }: MessageComponentProps) {
    const date = (new Date(message.timestamp * 1000)).toISOString();

    let msgContent;

    if (message.kind === "ai_message") {
        msgContent = (
            <div className="message-ai">
                <p>{message.agent_name}:</p>
                <Markdown>{message.content}</Markdown>
            </div>
        );
    }
    else if (message.kind === "human_message") {
        msgContent = (
            <div className="message-human">{`${message.username}: ${message.content}`}</div>
        );
    }
    else if (message.kind === "side_effect" && message.side_effect_kind === "image_generation") {
        msgContent = <p><img src={`data:image/jpeg;base64,${message.base64_encoded_image}`} width={"50%"} alt="AI generated image" /></p>
    }
    else {
        msgContent = <code>{JSON.stringify(message)}</code>
    }

    return (
        <div>
            <p>({date})</p>
            <div>{msgContent}</div>
        </div>
    );
}