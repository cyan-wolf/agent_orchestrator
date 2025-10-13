import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { useEffect, useState } from 'react';
import type { ChatJson } from '../chat';
import { Tooltip } from '@mui/material';

import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

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
          <ListItem 
            key={c.id} 
            disablePadding 
            sx={{
              width: '100%',
              display: 'flex', 
              alignItems: 'center', 
            }}
          >
            <ListItemButton 
              onClick={() => onSelectChat(c.id)}
              sx={{
                flexShrink: 0,
                width: '70%', 
                minWidth: 0, // Prevent text overflow issues.
              }}
              aria-label={`Select chat '${c.name}'`}
            >
              <ListItemText primary={c.name} /> 
            </ListItemButton>
            <Tooltip title="Edit Chat">
              <ListItemButton 
                onClick={() => onTryEditChat(c.id)}
                sx={{
                  flexShrink: 0,
                  p: 0.5,
                }}
                aria-label={`Edit chat '${c.name}'`}
              >
                <ListItemIcon sx={{ minWidth: 0 }}>
                  <EditIcon color="primary" />
                </ListItemIcon>
              </ListItemButton>
            </Tooltip>
            <Tooltip title="Delete Chat">
              <ListItemButton 
                onClick={() => onTryDeleteChat(c.id)}
                sx={{
                  flexShrink: 0,
                  p: 0.5,
                }}
                aria-label={`Delete chat '${c.name}'`}
              >
                <ListItemIcon sx={{ minWidth: 0 }}>
                  <DeleteIcon color="primary" />
                </ListItemIcon>
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    );
}