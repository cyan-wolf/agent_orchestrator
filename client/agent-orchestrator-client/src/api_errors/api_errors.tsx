
export type DetailPayload = {
    msg: string,
};

export type ApiErrorJson = {
    detail?: DetailPayload[],
};


export function apiErrorToMessage(error: ApiErrorJson, fallbackMsg: string): string {
    return error?.detail?.map(d => d.msg)?.join('; ') ?? fallbackMsg;
} 
