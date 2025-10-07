import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import type { ChatModificationJson } from '../chat';
import { TextField } from '@mui/material';

type ChatModificationModalProps = {
    chatId: string,
    isOpen: boolean,
    onChatEdit: (chatId: string, chatModification: ChatModificationJson) => void,
    onClose: () => void,
};

export default function ChatModificationModal({ chatId, isOpen, onChatEdit, onClose }: ChatModificationModalProps) {
  const [name, setName] = React.useState("");

  React.useEffect(() => {
    // TODO: make this fetch the name (and possibly other fields) of the chat, 
    // to autofill the form fields with the current values.
    setName("");
  }, [chatId]);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const chatModification: ChatModificationJson = {
        name
    };

    onChatEdit(chatId, chatModification)
  }

  return (
    <React.Fragment>
      <Dialog
        open={isOpen}
        onClose={onClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          Chat Modification
        </DialogTitle>
        <form onSubmit={handleSubmit}>
            <DialogContent>
                <TextField
                    autoFocus
                    margin="dense"
                    label="New Chat Name"
                    type="text"
                    fullWidth
                    variant="standard"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                />
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button 
                    type="submit"
                    autoFocus
                >
                    Modify Chat
                </Button>
            </DialogActions>
        </form>
      </Dialog>
    </React.Fragment>
  );
}