import { Outlet} from "react-router-dom";
import ChatDrawer from "./components/chat_drawer/ChatDrawer";
import type { MessageFilter } from "./components/messages/message";
import { createContext, useContext, useState } from "react";

type ChatContextData = {
    excludeFilters: MessageFilter[],
    setExcludeFilters: (excludeFilters: MessageFilter[]) => void,
};

const ChatContext = createContext<ChatContextData | null>(null);

/**
 * Component used for rendering the chat page.
 */
export default function Chat() {
    const [excludeFilters, setExcludeFilters] = useState<MessageFilter[]>([]);

    const value: ChatContextData = {
        excludeFilters,
        setExcludeFilters,
    };

    return (
        <ChatContext.Provider value={value}>
            <ChatDrawer>
                {/* Where the `ChatBox` gets rendered. */}
                <Outlet />
            </ChatDrawer>
        </ChatContext.Provider>
    );
}

export const useChatContext = () => useContext(ChatContext);
