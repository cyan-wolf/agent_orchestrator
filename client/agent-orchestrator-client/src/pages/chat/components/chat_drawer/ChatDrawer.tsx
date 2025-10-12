import { Button } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import type { ChatJson, ChatModificationJson, NewChatData } from './chat';
import ChatSelectionList from './components/ChatSelectionList';
import NewChatConfirmationFormModal from './components/NewChatConfirmationModal';
import DeleteChatConfirmationModal from './components/DeleteChatModalConfirmation';
import ChatExcludeFilterSelectionList from './components/ChatExcludeFilterSelectionList';
import { useChatContext } from '../../Chat';
import ChatModificationModal from './components/ChatModificationModal';

import TryIcon from '@mui/icons-material/Try';

const drawerWidth = 240;

type ChatDrawerProps = {
  children: React.ReactNode
};

/**
 * Drawer for displaying the chat selection list.
 * Embeds the chat box UI within the drawer.
 */
function ChatDrawer({ children }: ChatDrawerProps) {
  const navigate = useNavigate();
  const [newChatModalOpen, setNewChatModalOpen] = useState(false);

  // For managing the chat modification modal.
  const [chatEditModalChatId, setChatEditModalChatId] = useState<string | null>(null);
  const [chatEditModalOpen, setChatEditModalOpen] = useState(false);

  // For managing the chat delete modal.
  const [chatDeleteModalChatId, setChatDeleteModalChatId] = useState<string | null>(null);
  const [chatDeleteModalOpen, setChatDeleteModalOpen] = useState(false);

  // Used for forcing the chat list to re-render.
  const [chatListRefreshTriggerToggle, setChatListTriggerToggle] = useState(false);

  // For forcing the chat box UI (the one with the messages) to refresh.
  const { toggleCurrentChatRefresh } = useChatContext()!;

  const location = useLocation();

  function handleChatSelect(chatId: string) {
      // Change the URL to include the chat ID.
      // React Router and the chat box UI automatically render the correct chat based on the URL.
      navigate(chatId);
  }

  function getCurrentlySelectedChatId(): string | null {
    const fields = location.pathname.split('/');

    if (fields.length === 2) {
      return null;
    }
    return fields[2];
  }

  function handleChatEditAttempt(chatId: string) {
    setChatEditModalChatId(chatId);
    setChatEditModalOpen(true);
  }

  function handleChatDeleteAttempt(chatId: string) {
    setChatDeleteModalChatId(chatId);
    setChatDeleteModalOpen(true);
  }

  async function handleActualChatModification(chatId: string, chatModification: ChatModificationJson) {
    const resp = await fetch(`/api/chat/${chatId}/modify/`, {
      method: "PATCH",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chatModification),
    });
    const respJson = await resp.json();

    console.log(respJson);

    closeChatEditModal();

    // Refresh the chat list by forcing a prop change.
    // This state variable is a boolean, and (prev => !prev) just toggles it.
    setChatListTriggerToggle(prev => !prev);
  }

  async function handleActualChatDeletion(chatId: string) {
    const resp = await fetch(`/api/chat/${chatId}/delete/`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const respJson = await resp.json();

    console.log(respJson);

    closeChatDeleteModal();

    // Refresh the chat list by forcing a prop change.
    // This state variable is a boolean, and (prev => !prev) just toggles it.
    setChatListTriggerToggle(prev => !prev);

    if (chatId === getCurrentlySelectedChatId()) {
      // Unselect the chat if it was the one we just deleted.
      navigate('/chat');
    }
  }

  function closeChatEditModal() {
    setChatEditModalOpen(false);
    setChatEditModalChatId(null);
  }

  function closeChatDeleteModal() {
    setChatDeleteModalOpen(false);
    setChatDeleteModalChatId(null);
  }

  async function handleOpenModalForNewChat() {
    setNewChatModalOpen(true);
  }

  async function handleCreatingNewChat({ chatName }: NewChatData) {
    const resp = await fetch("/api/chat/create/", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: chatName
        }),
    });

    const chatJson: ChatJson = await resp.json();

    handleChatSelect(chatJson.id);

    // Close the modal.
    setNewChatModalOpen(false);

    // Refresh the chat list by forcing a prop change.
    // This state variable is a boolean, and (prev => !prev) just toggles it.
    setChatListTriggerToggle(prev => !prev);
  }

  function handleRefreshCurrentChatButtonClick() {
    toggleCurrentChatRefresh();
  }

  const [mobileOpen, setMobileOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const handleDrawerClose = () => {
    setIsClosing(true);
    setMobileOpen(false);
  };

  const handleDrawerTransitionEnd = () => {
    setIsClosing(false);
  };

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  const drawer = (
    <div>
      <Toolbar />
      <Button 
        sx={{ width: "100%" }}
        variant="outlined"
        onClick={() => navigate("/")}
      >
        Go Back to Home
      </Button>
      <Divider />
      <ChatSelectionList 
        onSelectChat={handleChatSelect} 
        onTryEditChat={handleChatEditAttempt}
        onTryDeleteChat={handleChatDeleteAttempt}
        refreshTriggerToggle={chatListRefreshTriggerToggle} 
      />
      <Divider />
      <Button 
        sx={{ width: "100%" }}
        variant="contained"
        onClick={handleOpenModalForNewChat}
      >
        Create New Chat
      </Button>
      <Divider />
      <Button 
        sx={{ width: "100%" }}
        variant="outlined"
        onClick={handleRefreshCurrentChatButtonClick}
      >
        Refresh Current Chat
      </Button>
      <Divider />

      <ChatExcludeFilterSelectionList />
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' }, zIndex: 9 }}
          >
            <TryIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Chat
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="chats"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          // container={container}
          variant="temporary"
          open={mobileOpen}
          onTransitionEnd={handleDrawerTransitionEnd}
          onClose={handleDrawerClose}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          slotProps={{
            root: {
              keepMounted: true, // Better open performance on mobile.
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box                // <--- this is the Box that contains the chat box UI (!)
        component="main"
        sx={{
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },

          height: '85vh', // <--- forces this Box to be a fixed-height 85% of the viewport's height

          minWidth: 0, // <--- prevents the inner content from growing out of control
        }}
      >
        <Toolbar />
        {children}
      </Box>

      <NewChatConfirmationFormModal 
        isOpen={newChatModalOpen} 
        onSubmit={chatData => handleCreatingNewChat(chatData)} 
        onClose={() => setNewChatModalOpen(false)}
      />

      <ChatModificationModal 
        chatId={chatEditModalChatId!}
        isOpen={chatEditModalOpen}
        onChatEdit={handleActualChatModification}
        onClose={closeChatEditModal}
      />

      <DeleteChatConfirmationModal 
        chatId={chatDeleteModalChatId!}
        isOpen={chatDeleteModalOpen}
        onChatDelete={handleActualChatDeletion}
        onClose={closeChatDeleteModal}
      />
    </Box>
  );
}

export default ChatDrawer;
