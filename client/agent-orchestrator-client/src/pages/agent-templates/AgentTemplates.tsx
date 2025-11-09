import { Card, CardContent, Container, Typography, Paper, Box, Collapse, Button, TextField, FormControlLabel, Checkbox, Stack } from "@mui/material";
import { useEffect, useState } from "react";
import type { AgentTemplateJson, ToolJson } from "./agent_template";

type AgentToolSectionProps = {
    tool: ToolJson,
    isEditing: boolean,
    onRemoveTool: (tool: ToolJson) => void,
};

type AgentToolsSectionProps = {
    tools: ToolJson[],
    isEditing: boolean,
    onAddTool: (tool: ToolJson) => void,
    onRemoveTool: (tool: ToolJson) => void,
};

function AgentToolSection({ tool, isEditing, onRemoveTool }: AgentToolSectionProps) {
    const [contentVisible, setContentVisible] = useState(false);

    return (
        <Paper 
            key={tool.id}
        >
            <Box
                sx={{
                    display: "flex",
                    justifyContent: 'space-between',
                }}
            >
                <Typography variant="h6">
                    {tool.name}
                </Typography>
                {(isEditing)? (
                    <Button onClick={() => onRemoveTool(tool)}>
                        Remove Tool
                    </Button>
                ) : <></>}
            </Box>
            <Button onClick={() => setContentVisible(prev => !prev)}>
                {(contentVisible) ? "Hide Tool Information" : "Show Tool Information"}
            </Button>

            <Collapse in={contentVisible}>
                <TextField
                    label="ID"
                    type="text"
                    value={tool.id}
                    slotProps={{
                        input: {
                            readOnly: true
                        }
                    }}
                    fullWidth
                    multiline
                    sx={{
                        m: 1
                    }}
                />
                <TextField
                    label="Description"
                    type="text"
                    value={tool.description}
                    slotProps={{
                        input: {
                            readOnly: true
                        }
                    }}
                    fullWidth
                    multiline
                    sx={{
                        m: 1
                    }}
                />
            </Collapse>
        </Paper>
    );
}

function AgentToolsSection({ tools, isEditing, onAddTool, onRemoveTool }: AgentToolsSectionProps) {    
    return (
        <Stack>
            {tools.map(tool => (
                <AgentToolSection tool={tool} isEditing={isEditing} onRemoveTool={onRemoveTool} />
            ))}
        </Stack>
    );
}

type AgentSectionProps = {
    agentTemplateJson: AgentTemplateJson,
};

function AgentSection({ agentTemplateJson }: AgentSectionProps) {
    const [contentVisible, setContentVisible] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    
    const [name, setName] = useState("");
    const [persona, setPersona] = useState("");
    const [purpose, setPurpose] = useState("");
    const [isSwitchableInto, setIsSwitchableInto] = useState(true);

    const [tools, setTools] = useState<ToolJson[]>([]);

    useEffect(() => {
        setName(agentTemplateJson.name);
        setPersona(agentTemplateJson.persona);
        setPurpose(agentTemplateJson.purpose);
        setIsSwitchableInto(agentTemplateJson.is_switchable_into);

        setTools(agentTemplateJson.tools);
    }, []);

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
            <Box 
            sx={{
                display: "flex",
                justifyContent: 'space-between',
            }}
        >
            <Typography variant="h4">
                    {agentTemplateJson.name} ({(agentTemplateJson.is_global)? "Global" : "Custom"})
                </Typography>
                {(agentTemplateJson.is_global) ? <></> : (
                    <Button onClick={() => setIsEditing(prev => !prev)}>
                        {(isEditing)? "Stop Editing" : "Edit Template"}
                    </Button>
                )}
            </Box>

            <Button onClick={() => setContentVisible(prev => !prev)}>
                {(contentVisible) ? "Hide Template" : "Show Template"}
            </Button>

            <Collapse in={contentVisible}>
                <form>
                    <TextField
                        label="Name"
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        slotProps={{
                            input: {
                                readOnly: !isEditing
                            }
                        }}
                        fullWidth
                        multiline
                        sx={{
                            m: 1
                        }}
                    />
                    <TextField
                        label="Persona"
                        type="text"
                        value={persona}
                        onChange={e => setPersona(e.target.value)}
                        slotProps={{
                            input: {
                                readOnly: !isEditing
                            }
                        }}
                        fullWidth
                        multiline
                        sx={{
                            m: 1
                        }}
                    />
                    <TextField
                        label="Purpose"
                        type="text"
                        value={purpose}
                        onChange={e => setPurpose(e.target.value)}
                        slotProps={{
                            input: {
                                readOnly: !isEditing
                            }
                        }}
                        fullWidth
                        multiline
                        sx={{
                            m: 1
                        }}
                    />

                    <FormControlLabel 
                        label="Is Switchable Into?" 
                        control={
                            <Checkbox 
                                checked={isSwitchableInto}
                                onChange={() => setIsSwitchableInto(prev => !prev)} 
                                disabled={!isEditing}
                            />
                        } 
                    />

                    <AgentToolsSection 
                        tools={tools}
                        isEditing={isEditing}
                        onAddTool={(tool) => console.log(`adding tool ${tool.id}`)}
                        onRemoveTool={(tool) => console.log(`removing tool ${tool.id}`)}
                    />

                    {(isEditing)? (
                        <Button 
                            type="submit" 
                            variant="contained"
                            fullWidth
                        >
                            Modify Template
                        </Button>
                    ) : <></>}
                </form>
            </Collapse>
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

