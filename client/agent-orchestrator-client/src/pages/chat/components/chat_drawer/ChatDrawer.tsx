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
import { useNavigate } from 'react-router-dom';
import type { ChatJson, NewChatData } from './chat';
import ChatSelectionList from './components/ChatSelectionList';
import NewChatConfirmationFormModal from './components/NewChatConfirmationModal';

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

  // Used for forcing the chat list to re-render.
  const [chatListRefreshTriggerToggle, setChatListTriggerToggle] = useState(false);

  function handleChatSelect(chatId: string) {
      navigate(chatId);
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

    handleChatSelect(chatJson.chat_id);

    // Close the modal.
    setNewChatModalOpen(false);

    // Refresh the chat list by forcing a prop change.
    // This state variable is a boolean, and (prev => !prev) just toggles it.
    setChatListTriggerToggle(prev => !prev);
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
      <Divider />
      <ChatSelectionList 
        onSelectChat={handleChatSelect} 
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
            M
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
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
      >
        <Toolbar />
        {children}
      </Box>

      <NewChatConfirmationFormModal 
        isOpen={newChatModalOpen} 
        onSubmit={chatData => handleCreatingNewChat(chatData)} 
        onClose={() => setNewChatModalOpen(false)}
      />
    </Box>
  );
}

export default ChatDrawer;
