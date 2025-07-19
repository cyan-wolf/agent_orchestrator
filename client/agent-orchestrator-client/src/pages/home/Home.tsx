import { Card, CardContent, Container, Divider, Typography } from "@mui/material";


export default function Home() {
    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography align="center" variant="h1">Agent Orchestrator</Typography>
                    <Divider />

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