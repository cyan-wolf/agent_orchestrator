
/**
 * Message trace types from the API.
 */
export type Message = {
    trace_id: string,
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
    | ({ kind: "side_effect" } & SideEffectPayload);

type SideEffectPayload = 
    | {
        side_effect_kind: "image_generation",
        base64_encoded_image: string,
    }
    | {
        side_effect_kind: "program_execution",
        source_code: string,
        language: string,
        output: string,
    };