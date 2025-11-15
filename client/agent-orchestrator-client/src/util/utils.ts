import { apiErrorToMessage, type ApiErrorJson } from "../api_errors/api_errors";

export async function resetAgentManagersForChat() {
    const resp = await fetch("/api/chat/reset-agent-managers/all/", {
        method: "POST",
    });

    if (!resp.ok) {
        const errJson: ApiErrorJson = await resp.json();
        const errMsg = apiErrorToMessage(errJson, "error while resetting agent managers for that");
        console.error(errMsg);
    }
}