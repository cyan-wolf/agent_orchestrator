import { Typography, Paper, Box, Collapse, Button, TextField, Stack, FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import {  useState } from "react";
import type { ToolJson } from "./agent_template";
import { useIsOnMobile } from "../../util/isOnMobile";

type AgentToolSectionProps = {
    tool: ToolJson,
    isEditing: boolean,
    onRemoveTool: (tool: ToolJson) => void,
};

type AgentToolsSectionProps = {
    tools: Record<string, ToolJson>,
    isEditing: boolean,
    onAddTool: (tool: ToolJson) => void,
    onRemoveTool: (tool: ToolJson) => void,
    allTools: Record<string, ToolJson>,
};

function AgentToolSection({ tool, isEditing, onRemoveTool }: AgentToolSectionProps) {
    const [contentVisible, setContentVisible] = useState(false);

    const isMobile = useIsOnMobile();

    return (
        <Paper 
            key={tool.id}
        >
            <Box
                sx={{
                    display: "flex",
                    flexDirection: (isMobile)? "column" : "row",
                    alignItems: (isMobile)? "flex-start" : "baseline",
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

export default function AgentToolsSection({ tools, isEditing, onAddTool, onRemoveTool, allTools }: AgentToolsSectionProps) {
    const [currSelectedTool, setCurrSelectedTool] = useState<ToolJson | null>(null);

    return (
        <Box>
            <Stack>
                {Object.keys(tools).map(toolId => (
                    <AgentToolSection key={toolId} tool={tools[toolId]} isEditing={isEditing} onRemoveTool={onRemoveTool} />
                ))}
            </Stack>

            {(isEditing)? (
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: 4,
                    }}
                >
                    <FormControl margin="normal" fullWidth>
                        <InputLabel id="label-add-tool">Add New Tool</InputLabel>
                        <Select
                            labelId="label-add-tool"
                            id="select-tool"
                            label="add-tool"
                            value={currSelectedTool?.id}
                            onChange={e => setCurrSelectedTool(allTools[e.target.value as string])}
                            sx={{
                                flexGrow: 1
                            }}
                            fullWidth
                        >
                            {Object.keys(allTools).map((toolId) => (
                                <MenuItem key={toolId} value={toolId}>
                                    {allTools[toolId].name} - {allTools[toolId].description}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button
                        onClick={() => {
                            if (currSelectedTool !== null) {
                                onAddTool(currSelectedTool);
                            }
                        }}
                        sx={{
                            flexGrow: 1,
                            whiteSpace: "nowrap",
                        }}
                        disabled={currSelectedTool === null}
                    >
                        Add New Tool
                    </Button>
                </Box>
            ) : <></>}
        </Box>
    );
}