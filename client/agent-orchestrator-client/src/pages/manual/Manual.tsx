import { Box, Card, CardContent, Container, Paper, Stack, Typography } from "@mui/material";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

function BoldSpan(props: { children: ReactNode }) {
    return <Typography fontWeight="bold" component="span">{props.children}</Typography>
}

export default function Manual() {
    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography variant="h1">Agent Orchestrator Manual</Typography>

                    <Typography variant="h2">Table of Contents</Typography>
                    <Box>
                        <ol>
                            <li>
                                <Link to="#section-terms">Terms</Link>
                            </li>
                            <li>
                                <Link to="#section-agents">Agents</Link>
                            </li>
                        </ol>
                    </Box>

                    <Typography variant="h2" id="section-terms">Terms</Typography>
                    <Stack spacing={2} padding={4}>
                        <Paper>
                            <BoldSpan>Agent</BoldSpan>: An artificial intelligence (AI) model with the ability to call specialized tools. 
                        </Paper>
                        <Paper>
                            <BoldSpan>Tool</BoldSpan>: Functions that can be called by an AI model to perform an arbitary task.
                        </Paper>
                        <Paper>
                            <BoldSpan>Agent orchestration</BoldSpan>: The management of multiple agent to accomplish one or more tasks.
                        </Paper>
                    </Stack>

                    <Typography variant="h2" id="section-agents">Agents</Typography>
                    <Stack spacing={2} padding={4}>
                        <Paper>
                            <BoldSpan>Supervisor</BoldSpan>: Serves as the entry point for the application. When the user first 
                            starts a new chat, they start talking to the supervisor. Depending on the user's needs, the supervisor may then 
                            hand off the user to a more qualified agent, such as the coding or content generation agents.
                        </Paper>
                        <Paper>
                            <BoldSpan>Coding Agent</BoldSpan>: Has access to an isolated sandbox Linux environment. 
                            Can interact with its environment through the use of tools. It has tools for creating/overwritting files and 
                            for running terminal commands. It can combine these tools to create and run scripts. Currently it only supports 
                            the Python programming language.
                        </Paper>
                        <Paper>
                            <BoldSpan>Creator Agent</BoldSpan>: Can create images through the use of tools. 
                        </Paper>
                        <Paper>
                            <BoldSpan>Research Agent</BoldSpan>: Has access to external and up-to-date information through the 
                            use of its web search tool. This is a way of implementing retrieval-augment-generation (RAG), where 
                            the output of the model is expanded to include data outside of its original training data.
                        </Paper>
                        <Paper>
                            <BoldSpan>Planner Agent</BoldSpan>: Saves events on a schedule to help the user plan out tasks.
                        </Paper>
                        <Paper>
                            <BoldSpan>Math Agent</BoldSpan>: Helps with math.
                        </Paper>
                    </Stack>
                </CardContent>
            </Card>
        </Container>
    );
}