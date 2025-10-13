import { Dialog, DialogTitle, DialogContent, DialogContentText, TextField, DialogActions, Button } from "@mui/material";
import { useState } from "react";
import type { NewChatData } from "../chat";

type NewChatConfirmationFormModalProps = {
  isOpen: boolean
  onSubmit: (chatData: NewChatData) => void,
  onClose: () => void,
};

/**
 * Modal that appears when the user wants to create a new chat. Requests 
 * information like the new chat's name.
 */
export default function NewChatConfirmationFormModal({ isOpen, onSubmit, onClose }: NewChatConfirmationFormModalProps) {
  const [chatName, setChatName] = useState("");

  function validateFormSubmission(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (chatName.trim().length > 0) {
      onSubmit({ chatName: chatName.trim() });
    }
  }

  return (
    <>
      <Dialog 
        open={isOpen} 
        onClose={onClose}
        aria-labelledby="new-chat-dialog-title" 
        aria-describedby="new-chat-dialog-description"
      >
        <DialogTitle id="new-chat-dialog-title">Create New Chat</DialogTitle>
        <DialogContent sx={{ paddingBottom: 0 }}>
          <DialogContentText id="new-chat-dialog-description">
            Enter a name for the chat.
          </DialogContentText>
          <form onSubmit={validateFormSubmission}>
            <TextField
              autoFocus
              required
              margin="dense"
              id="name"
              name="chat-name"
              label="Chat Name"
              type="text"
              onChange={e => setChatName(e.target.value)}
              slotProps={{ htmlInput: { pattern: "^.{1,15}$" } }}
              fullWidth
              variant="standard"
            />
            <DialogActions>
              <Button onClick={onClose}>Cancel</Button>
              <Button type="submit">Create</Button>
            </DialogActions>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}