import { Card, CardContent, Container, Typography, Paper, Box, Collapse, Button, TextField, FormControlLabel, Checkbox, Alert } from "@mui/material";
import { useEffect, useState } from "react";
import type { AgentTemplateCreationJson, AgentTemplateJson, AgentTemplateModificationJson, ToolJson } from "./agent_template";
import { apiErrorToMessage } from "../../api_errors/api_errors";
import AgentToolsSection from "./AgentToolSection";
import Loading from "../../components/loading/Loading";
import { useIsOnMobile } from "../../util/isOnMobile";
import { resetAgentManagersForChat } from "../../util/utils";


type AgentSectionProps = {
    agentTemplateJson: AgentTemplateJson | null,
    allTools: Record<string, ToolJson>,
    onAgentCreationSuccess: () => void,
    onAgentDeletionSuccess: () => void,
};

function AgentSection({ agentTemplateJson, allTools, onAgentCreationSuccess, onAgentDeletionSuccess }: AgentSectionProps) {
    const [contentVisible, setContentVisible] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    
    const [name, setName] = useState(agentTemplateJson?.name ?? "new_agent");
    const [persona, setPersona] = useState(agentTemplateJson?.persona ?? "");
    const [purpose, setPurpose] = useState(agentTemplateJson?.purpose ?? "");
    const [isSwitchableInto, setIsSwitchableInto] = useState(true);

    const [nameErrMsg, setNameErrMsg] = useState("");
    const [personaErrMsg, setPersonaErrMsg] = useState("");
    const [purposeErrMsg, setPurposeErrMsg] = useState("");

    const [tools, setTools] = useState<Record<string, ToolJson>>({});

    const [agentIsGlobal, setAgentIsGlobal] = useState(agentTemplateJson?.is_global ?? false);

    const [gotServerError, setGotServerError] = useState(false);
    const [serverMessage, setServerMessage] = useState<string | null>(null);
    
    const isMobile = useIsOnMobile();

    const isInAgentCreationMode = agentTemplateJson === null;

    useEffect(() => {
        if (agentTemplateJson === null) {
            setContentVisible(true);
            setIsEditing(true);
            return;
        }

        setName(agentTemplateJson.name);
        setPersona(agentTemplateJson.persona);
        setPurpose(agentTemplateJson.purpose);
        setIsSwitchableInto(agentTemplateJson.is_switchable_into);

        setTools(Object.fromEntries(agentTemplateJson.tools.map(t => [t.id, t])));

        setAgentIsGlobal(agentTemplateJson.is_global);
    }, []);

    function validateName(): boolean {
        if (name.trim().length === 0) {
            setNameErrMsg("name cannot be empty");
            return false;
        }
        setNameErrMsg("");
        return true;
    }

    function validatePersona(): boolean {
        if (persona.trim().length === 0) {
            setPersonaErrMsg("persona cannot be empty");
            return false;
        }
        setPersonaErrMsg("");
        return true;
    }

    function validatePurpose(): boolean {
        if (purpose.trim().length === 0) {
            setPurposeErrMsg("purpose cannot be empty");
            return false;
        }
        setPurposeErrMsg("");
        return true;
    }


    function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        const isValid = validateName() && validatePersona() && validatePurpose();
        if (!isValid) {
            return;
        }

        if (isInAgentCreationMode) {
            postAgentCreation();
        }
        else {
            postAgentModification();
        }
    }

    async function postAgentCreation() {
        const modificationJson: AgentTemplateCreationJson = {
            name, persona, purpose,
            is_switchable_into: isSwitchableInto,
            tool_id_list: Object.keys(tools),
        };

        const resp = await fetch("/api/agent-templates/custom/create/", {
            method: "POST",
            headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(modificationJson),
        });

        if (!resp.ok) {
            const errJson = await resp.json();
            
            setGotServerError(true);
            setServerMessage(apiErrorToMessage(errJson, "Could not create agent template."));
            return;
        }

        setGotServerError(false);
        setServerMessage("Successfully created agent.");
        onAgentCreationSuccess();
    }

    async function postAgentModification() {
        const modificationJson: AgentTemplateModificationJson = {
            name, persona, purpose,
            id: agentTemplateJson!.id,
            is_switchable_into: isSwitchableInto,
            tool_id_list: Object.keys(tools),
        };

        const resp = await fetch("/api/agent-templates/custom/modify/", {
            method: "POST",
            headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(modificationJson),
        });

        if (!resp.ok) {
            const errJson = await resp.json();
            
            setGotServerError(true);
            setServerMessage(apiErrorToMessage(errJson, "Could not modify agent template."));
            return;
        }

        setGotServerError(false);
        setServerMessage("Successfully modified agent.");

        // A template was modified, so we reset all the chat agent managers.
        await resetAgentManagersForChat();
    }

    async function handleTemplateDeletion() {
        // TODO: show a confirmation modal before doing this vvvvvvvvvvvvvvvvvvvvvvvv

        const resp = await fetch(`/api/agent-templates/custom/${agentTemplateJson!.id}/`, {
            method: "DELETE"
        });

        if (!resp.ok) {
            const errJson = await resp.json();
            
            setGotServerError(true);
            setServerMessage(apiErrorToMessage(errJson, "Could not delete agent template."));
            return;
        }
        onAgentDeletionSuccess();
    }

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
                    flexDirection: (isMobile)? "column" : "row",
                    justifyContent: 'space-between',
                }}
            >
                <Typography variant="h4">
                    {name} ({(agentIsGlobal)? "Global" : "Custom"})
                </Typography>

                <Box>
                    {(agentIsGlobal) ? <></> : (
                    <Button 
                        onClick={() => {
                            setIsEditing(prev => !prev);
                            setContentVisible(true);
                        }}
                        disabled={isInAgentCreationMode}
                    >
                        {(isEditing)? "Stop Editing" : "Edit Template"}
                    </Button>
                )}

                {(agentIsGlobal) ? <></> : (
                    <Button 
                        onClick={() => handleTemplateDeletion()}
                        disabled={isInAgentCreationMode}
                    >
                        Delete
                    </Button>
                )}
                </Box>
            </Box>

            <Button 
                onClick={() => setContentVisible(prev => !prev)}
                disabled={isInAgentCreationMode}
            >
                {(contentVisible) ? "Hide Template" : "Show Template"}
            </Button>

            <Collapse in={contentVisible}>
                <form onSubmit={handleSubmit}>
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
                            mt: 1,
                            mb: 1,
                        }}
                        helperText={nameErrMsg}
                        error={!!nameErrMsg}
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
                            mt: 1,
                            mb: 1,
                        }}
                        helperText={personaErrMsg}
                        error={!!personaErrMsg}
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
                            mt: 1,
                            mb: 1,
                        }}
                        helperText={purposeErrMsg}
                        error={!!purposeErrMsg}
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
                        onAddTool={(tool) => {
                            if (Object.hasOwn(tools, tool.id)) {
                                return; // duplicate tool
                            }
                            setTools(prev => {
                                // Add the new tool along with the rest of the previous state.
                                return { [tool.id]: tool, ...prev }
                            });
                        }}
                        onRemoveTool={(tool) => {
                            setTools(prev => {
                                // Extract out the rest of the tools from the previous state.
                                const { [tool.id]: _, ...rest } = prev;
                                return rest;
                            })
                        }}
                        allTools={allTools}
                    />

                    {(isEditing)? (
                        <Button 
                            type="submit" 
                            variant="contained"
                            fullWidth
                        >
                            {(agentTemplateJson === null)? "Add New Template" : "Modify Template"}
                        </Button>
                    ) : <></>}
                </form>

                {(serverMessage !== null)? (
                    <Alert severity={(gotServerError)? "error" : "success"}>
                        {serverMessage}
                    </Alert>
                ) : <></>}
            </Collapse>
        </Paper>
    );
}

export default function AgentTemplates() {
    const [templates, setTemplates] = useState<AgentTemplateJson[]>([]);
    const [allTools, setAllTools] = useState<Record<string, ToolJson>>({});

    const [waitingForServer, setWaitingForServer] = useState(true);

    const [addingNewAgent, setAddingNewAgent] = useState(false);

    const [refreshToggle, setRefreshToggle] = useState(false);

    useEffect(() => {
        const fetchAgentTemplates = async () => {
            const resp = await fetch("/api/agent-templates/all/");

            const json: AgentTemplateJson[] = await resp.json();

            setTemplates(json);
        };
        const fetchAllTools = async () => {
            const resp = await fetch("/api/agent-templates/tools/all/");

            const json: ToolJson[] = await resp.json();

            setAllTools(Object.fromEntries(json.map(t => [t.id, t])));
        };

        const fetchAgentTemplatesAndTools = async () => {
            await fetchAgentTemplates();
            await fetchAllTools();

            setWaitingForServer(false);
        };

        fetchAgentTemplatesAndTools();
    }, [refreshToggle]);

    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography variant="h1" align="center">Agent Templates</Typography>

                    {(waitingForServer)? (<Loading />) : (
                        <Box>
                            {templates.map(t => (
                                <AgentSection 
                                    key={t.id} 
                                    agentTemplateJson={t} 
                                    allTools={allTools} 
                                    onAgentCreationSuccess={() => {}} // unreachable
                                    onAgentDeletionSuccess={async () => {
                                        setRefreshToggle(prev => !prev);

                                        // A template was deleted, so we reset all the chat agent managers.
                                        await resetAgentManagersForChat();
                                    }}
                                />
                            ))}
                        </Box>
                    )}

                    {(addingNewAgent)? (
                        <AgentSection 
                            agentTemplateJson={null} 
                            allTools={allTools} 
                            onAgentCreationSuccess={async () => {
                                setAddingNewAgent(false);
                                setRefreshToggle(prev => !prev);

                                // A new template was added, so we reset all the chat agent managers.
                                await resetAgentManagersForChat();
                            }}
                            onAgentDeletionSuccess={() => {}} // unreachable
                        />
                    ) : <></>}

                    <Button 
                        variant="contained" 
                        fullWidth
                        onClick={() => setAddingNewAgent(true)}
                        disabled={addingNewAgent}
                    >
                        Add New Agent
                    </Button>
                </CardContent>
            </Card>
        </Container>
    );
}

