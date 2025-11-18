import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

type DeleteChatConfirmationModalProps = {
    chatId: string,
    isOpen: boolean,
    onChatDelete: (chatId: string) => void,
    onClose: () => void,
};

export default function DeleteChatConfirmationModal({ chatId, isOpen, onChatDelete, onClose }: DeleteChatConfirmationModalProps) {
  return (
    <React.Fragment>
      <Dialog
        open={isOpen}
        onClose={onClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        fullWidth
      >
        <DialogTitle id="alert-dialog-title">
          {"Delete Chat Confirmation"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Warning: This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button 
            onClick={() => onChatDelete(chatId)} 
            autoFocus
        >
            Delete Chat
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}