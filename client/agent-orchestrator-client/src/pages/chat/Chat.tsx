import { Outlet} from "react-router-dom";
import ChatDrawer from "./components/chat_drawer/ChatDrawer";
import type { MessageFilter } from "./components/messages/message";
import { createContext, useContext, useState } from "react";

type ChatContextData = {
    excludeFilters: MessageFilter[],
    setExcludeFilters: (excludeFilters: MessageFilter[]) => void,
    toggleCurrentChatRefresh: () => void,
    currentChatRefreshToggle: boolean,
};

const ChatContext = createContext<ChatContextData | null>(null);

/**
 * Component used for rendering the chat page.
 */
export default function Chat() {
    const [excludeFilters, setExcludeFilters] = useState<MessageFilter[]>([]);
    const [currentChatRefreshToggle, setCurrentChatRefreshToggle] = useState(false);

    const value: ChatContextData = {
        excludeFilters,
        setExcludeFilters,
        currentChatRefreshToggle,
        toggleCurrentChatRefresh: () => setCurrentChatRefreshToggle(prev => !prev),
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
