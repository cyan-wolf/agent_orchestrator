import { Card, CardContent, Container, Typography, Paper, Box } from "@mui/material";
import { useEffect, useState } from "react";
import type { AgentTemplateJson, ToolJson } from "./agent_template";

type AgentToolsSectionProps = {
    toolsJson: ToolJson[],
};

function AgentToolsSection({ toolsJson }: AgentToolsSectionProps) {
    return (
        <div>
            {toolsJson.map(tool => (<Paper key={tool.id} elevation={2}>
                <p style={{margin: 0}}>Tool ID: <span style={{fontWeight: 'bold'}}>{tool.id}</span></p>
                <p>Tool Name: {tool.name}</p>
                <p>{tool.description}</p>
            </Paper>))}
        </div>
    );
}

type AgentSectionProps = {
    agentTemplateJson: AgentTemplateJson,
};

function AgentSection({ agentTemplateJson }: AgentSectionProps) {
    return (
        <Paper
            elevation={8}
            sx={{
                ml: { xs: 0, md: 12 }, // 0 margin on 'xs' screens, 12 on 'md' and up
                mr: { xs: 0, md: 12 }, // 0 margin on 'xs' screens, 12 on 'md' and up

                // Padding all sides
                p: { xs: 2, md: 5 },            
            }}
        >
            <Typography variant="h4">{agentTemplateJson.name} ({(agentTemplateJson.is_global)? "Global" : "Custom"})</Typography>

            <Typography variant="body1">{agentTemplateJson.persona}</Typography>

            <Typography variant="body1" p={4}>{agentTemplateJson.purpose}</Typography>

            <AgentToolsSection toolsJson={agentTemplateJson.tools} />
        </Paper>
    );
}

export default function AgentTemplates() {
    const [templates, setTemplates] = useState<AgentTemplateJson[]>([]);

    useEffect(() => {
        const fetchAgentTemplates = async () => {
            const resp = await fetch("/api/agent-templates/all/");

            const json: AgentTemplateJson[] = await resp.json();

            setTemplates(json);
        };
        fetchAgentTemplates();
    }, []);

    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography variant="h1" align="center">Agent Templates</Typography>

                    <Box>
                        {templates.map(t => <AgentSection key={t.id} agentTemplateJson={t} />)}
                    </Box>
                </CardContent>
            </Card>
        </Container>
    );
}

