import { Outlet} from "react-router-dom";
import ChatDrawer from "./components/ChatDrawer";

export default function Chat() {
    return (
        <>
            {/* <PlaceholderChatSelect onSelectChat={handleChatSelect}/> */}
            <ChatDrawer>
                {/* Where the `ChatBox` gets rendered. */}
                <Outlet />
            </ChatDrawer>
        </>
    );
}
