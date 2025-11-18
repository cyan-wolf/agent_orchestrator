import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";

type AgentTemplateDeletionModalProps = {
    templateId: string,
    isOpen: boolean,
    onTemplateDelete: (templateId: string) => void,
    onClose: () => void,
};

export default function AgentTemplateDeletionModal({ templateId, isOpen, onTemplateDelete, onClose }: AgentTemplateDeletionModalProps) {
    return (
        <Dialog
            open={isOpen}
            onClose={onClose}
            fullWidth
        >
            <DialogTitle>
                Delete Template Confirmation
            </DialogTitle>

            <DialogContent>
                <DialogContentText>
                    Warning: This action cannot be undone.
                </DialogContentText>
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>
                    Cancel
                </Button>
                <Button
                    onClick={() => onTemplateDelete(templateId)}
                    autoFocus
                >
                    Delete Template
                </Button>
            </DialogActions>
        </Dialog>
    );
}
