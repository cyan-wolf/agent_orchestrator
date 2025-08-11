import { Box, Button, Card, CardContent, Container, Divider, Paper, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";


export default function Home() {
    const navigate = useNavigate();

    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography align="center" variant="h1">Agent Orchestrator</Typography>
                    <Divider />
                    
                    <Box
                        sx={{
                            display: "flex",
                            justifyContent: "center",
                            padding: "20px"
                        }}
                    >
                        <Button 
                            variant="contained" 
                            size="large"
                            onClick={() => navigate("/chat")}
                        >
                            Start Chat
                        </Button>
                    </Box>

                    <Typography align="center" variant="h2">Aims</Typography>
                    <Typography>
                        Agent Orchestrator is a web app that allows the user to use AI in a more efficient way. 
                        Instead of using a single general purpose model for different tasks, this web app determines 
                        the best model to use depending on the given task. 
                    </Typography>

                    <Stack spacing={2} padding={4}>
                        <Paper elevation={4}>
                            For example, when faced with a coding task, the app will switch to a specialized coding model 
                            with access to a secure sandbox Linux envivironment where it can run terminal commands along 
                            with writing and executing programs.
                        </Paper>
                        <Paper elevation={4}>
                            When asked about information or events outside of its initial training data, the app can switch to a 
                            researcher model with access to a web search tool. The model can use the tool to get up to date 
                            information from the internet.   
                        </Paper>
                        <Paper elevation={4}>
                            When needing to generate specialized content (such as images), the app can switch to a specialized 
                            mutli-modal model that can generate images from textual prompts.
                        </Paper>
                    </Stack>

                    <Typography align="center" variant="h2">Logging and Transparency</Typography>
                    <Typography>
                        The web app comes with a robust logging system that separates itself from other AI systems.
                        Most AI systems function as a black box, where it is difficult, if not impossible, to determine 
                        how the AI got its answer or how it performed a task. The Agent Orchestrator web app logs every action performed 
                        by every AI model (agent). Every AI agent is capable of interacting with other agents or with the outside world using 
                        tools. Each tool performs a specialized task, such as running a Python script or generating an image. Tools can also 
                        switch the currently active agent or get help from other agents without switching. The system displays every tool call 
                        and agent switch, displaying what agent called it and when.
                    </Typography>

                    <Typography align="center" variant="h2">Technology</Typography>
                    <Typography>
                        Agent Orchestrator is a web app that aims to test out the capabilities of agentic orchestration.
                        The user can chat with an AI agent (dubbed the "supervisor agent") that supervises several other agents. 
                        The supervisor agent can request help from more specialized agents (dubbed "helper agents"). These helper agents 
                        are equipped with tools to perform actions on behalf of the user, such as running programs, setting up 
                        calendar events, generating images, or performing web searches. These tools also augment the agents in a process 
                        known as retrieval augmented generation (RAG). RAG can allow agents to expand their knowledge base past what was 
                        present in their original training data. For example, one of the helper agents is a research agent that can perform 
                        web searches on the spot to gain up to date information about the world, despite its underlying model having been 
                        trained several months or years in the past. 
                    </Typography>
                </CardContent>
            </Card>
        </Container>
    );
}