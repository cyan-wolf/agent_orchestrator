
/**
 * Public chat type from the API.
 */
export type ChatJson = {
    chat_id: string,
    name: string,
};

/**
 * Data for creating a new chat from the client.
 */
export type NewChatData = {
  chatName: string
};
