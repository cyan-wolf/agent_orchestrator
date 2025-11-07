

export type ToolJson = {
    id: string,
    name: string,
    description: string,
};

export type AgentTemplateJson = {
    id: string,
    name: string,
    persona: string,
    purpose: string,
    is_switchable_into: boolean,
    is_global: boolean,
    tools: ToolJson[],
};