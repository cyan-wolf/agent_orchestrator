
/**
 * Public chat type from the API.
 */
export type ChatJson = {
    id: string,
    name: string,
};

/**
 * Chat modification type from the API.
 */
export type ChatModificationJson = {
  name: string | null,
};

/**
 * Data for creating a new chat from the client.
 */
export type NewChatData = {
  chatName: string
};
