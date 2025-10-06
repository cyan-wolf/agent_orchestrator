
/**
 * Message trace types from the API.
 */
export type Message = {
    id: string,
    timestamp: number,
} & MessagePayload;

type MessagePayload = 
    | { 
        kind: "ai_message",
        agent_name: string,
        content: string,
        is_main_agent: string,
    } 
    | {
        kind: "human_message",
        username: string,
        content: string,
    }
    | {
        kind: "tool",
        called_by: string,
        name: string,
        bound_arguments: object,
        return_value: string,
    }
    | {
        kind: "image",
        base64_encoded_image: string,
        caption: string,
    };

export type MessageFilter = 'tool' | 'image' | 'ai_message' | 'human_message';