import { Button } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

type ChatJson = {
    chat_id: string
};

type ChatSelectProps = {
    onSelectChat: (chatId: string) => void
};

function ChatSelectionList({ onSelectChat }: ChatSelectProps) {
    const [chats, setChats] = useState<ChatJson[]>([]);

    useEffect(() => {
        const fetchChatIds = async () => {
            const resp = await fetch("/api/chat/get-all-chats/");
            const chatJson = await resp.json();

            setChats(chatJson);
        };
        fetchChatIds();
    }, []);

    return (
      <List>
        {chats.map((c) => (
          <ListItem key={c.chat_id} disablePadding>
            <ListItemButton onClick={() => onSelectChat(c.chat_id)}>
              <ListItemIcon>
                C
              </ListItemIcon>
              {/* Placeholder text */}
              <ListItemText primary={c.chat_id.slice(0, 5)} /> 
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
}

const drawerWidth = 240;

type ChatDrawerProps = {
  children: React.ReactNode
};

function ChatDrawer({ children }: ChatDrawerProps) {
  const navigate = useNavigate();

  function handleChatSelect(chatId: string) {
      navigate(chatId);
  }

  async function handleCreateNewChat() {
    const resp = await fetch("/api/chat/create/", {
        method: "POST"
    });

    const chatJson: ChatJson = await resp.json();

    handleChatSelect(chatJson.chat_id);
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
      <ChatSelectionList onSelectChat={handleChatSelect} />
      <Divider />
      <Button 
        sx={{ width: "100%" }}
        variant="contained"
        onClick={handleCreateNewChat}
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
    </Box>
  );
}

export default ChatDrawer;
