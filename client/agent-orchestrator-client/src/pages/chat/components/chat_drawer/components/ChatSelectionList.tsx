import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { useEffect, useState } from 'react';
import type { ChatJson } from '../chat';

type ChatSelectProps = {
    onSelectChat: (chatId: string) => void,
    // For forcing the chat list to re-render.
    refreshTriggerToggle: boolean,
};

/**
 * Drawer list for selecting between available chats.
 */
export default function ChatSelectionList({ onSelectChat, refreshTriggerToggle }: ChatSelectProps) {
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
          <ListItem key={c.chat_id} disablePadding>
            <ListItemButton onClick={() => onSelectChat(c.chat_id)}>
              <ListItemIcon>
                C
              </ListItemIcon>
              <ListItemText primary={c.name} /> 
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
}