import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import type { ChatJson, ChatModificationJson } from '../chat';
import { Alert, AlertTitle, TextField } from '@mui/material';

type ChatModificationModalProps = {
    chatId: string | null, // the chat ID can be `null` due to React-isms
    isOpen: boolean,
    errorMsg: string | null,
    onChatEdit: (chatId: string, chatModification: ChatModificationJson) => void,
    onClose: () => void,
};

export default function ChatModificationModal({ chatId, isOpen, errorMsg, onChatEdit, onClose }: ChatModificationModalProps) {
  // If the chat ID ever technically is null, then do not try to render anything.
  if (chatId === null) {
    return null;
  }

  const [name, setName] = React.useState("");
  const [nameErrMsg, setNameErrMsg] = React.useState("");

  React.useEffect(() => {
    // Autofill the form fields with the current values of the chat.
    const fetchChatData = async () => {
      const resp = await fetch(`/api/chat/${chatId}/info/`);
      const chat: ChatJson = await resp.json();

      setName(chat.name);
    };
    fetchChatData();
  }, [chatId]);

  function validateFormFields(): boolean {
    if (name.trim().length === 0 || name.trim().length > 20) {
      setNameErrMsg("Name length must be between 1 and 19 characters in length.");
      return false;
    }
    setNameErrMsg("");
    return true;
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!validateFormFields()) {
      return;
    }

    const chatModification: ChatModificationJson = {
      name: name.trim(),
    };

    onChatEdit(chatId!, chatModification)
  }

  return (
    <React.Fragment>
      <Dialog
        open={isOpen}
        onClose={onClose}
        aria-labelledby="alert-dialog-title"
        fullWidth
      >
        <DialogTitle id="alert-dialog-title">
          Chat Modification
        </DialogTitle>
        <form onSubmit={handleSubmit}>
            <DialogContent>
                <TextField
                    autoFocus
                    margin="dense"
                    label="Chat Name"
                    type="text"
                    fullWidth
                    variant="standard"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                    helperText={nameErrMsg}
                    error={!!nameErrMsg}
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

        {(errorMsg === null)? <></> : (
          <Alert severity="error">
            <AlertTitle>Server Error</AlertTitle>
            {errorMsg}
          </Alert>
        )}
      </Dialog>
    </React.Fragment>
  );
}