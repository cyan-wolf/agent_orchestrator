import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { useEffect, useState } from 'react';
import type { ChatJson } from '../chat';
import { Tooltip } from '@mui/material';

type ChatSelectProps = {
    onSelectChat: (chatId: string) => void,
    onTryEditChat: (chatId: string) => void,
    onTryDeleteChat: (chatId: string) => void, 
    // For forcing the chat list to re-render.
    refreshTriggerToggle: boolean,
};

/**
 * Drawer list for selecting between available chats.
 */
export default function ChatSelectionList({ onSelectChat, onTryEditChat, onTryDeleteChat, refreshTriggerToggle }: ChatSelectProps) {
    const [chats, setChats] = useState<ChatJson[]>([]);

    useEffect(() => {
        const fetchChatIds = async () => {
            const resp = await fetch("/api/chat/get-all-chats/");
            const chatJson = await resp.json();

            setChats(chatJson);
        };
        fetchChatIds();
    }, [refreshTriggerToggle]); // re-fetch the chats whenever the chat list is forced to "refresh"

    return (
      <List>
        {chats.map((c) => (
          <ListItem key={c.id} disablePadding>
            <ListItemButton 
              onClick={() => onSelectChat(c.id)}
              sx={{
                width: "50%"
              }}
            >
              <ListItemText primary={c.name} /> 
            </ListItemButton>
            <Tooltip title="Edit Chat">
              <ListItemButton onClick={() => onTryEditChat(c.id)}>
                <ListItemIcon
                  sx={{
                    display: "inline-block",
                    textAlign: "center",
                  }}
                >
                  E
                </ListItemIcon>
              </ListItemButton>
            </Tooltip>
            <Tooltip title="Delete Chat">
              <ListItemButton onClick={() => onTryDeleteChat(c.id)}>
                <ListItemIcon
                  sx={{
                    display: "inline-block",
                    textAlign: "center",
                  }}
                >
                  X
                </ListItemIcon>
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    );
}