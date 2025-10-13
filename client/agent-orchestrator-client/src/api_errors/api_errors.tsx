
export type DetailPayload = {
    msg: string,
};

export type ApiErrorJson = {
    detail?: DetailPayload[] | string,
};


export function apiErrorToMessage(error: ApiErrorJson, fallbackMsg: string): string {
    if (typeof error.detail === 'string') {
        return error.detail;
    }
    return error?.detail?.map(d => d.msg)?.join('; ') ?? fallbackMsg;
}
