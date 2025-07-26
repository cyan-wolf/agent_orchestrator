import { Outlet} from "react-router-dom";
import ChatDrawer from "./components/chat_drawer/ChatDrawer";

/**
 * Component used for rendering the chat page.
 */
export default function Chat() {
    return (
        <ChatDrawer>
            {/* Where the `ChatBox` gets rendered. */}
            <Outlet />
        </ChatDrawer>
    );
}
