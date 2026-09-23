export type MessageRole = 'user' | 'assistant';



export interface Message {
    id: string;
    role: MessageRole;
    content: string;
    createdAt: Date;
}

export type ChatStatus = 'idle' | 'loading' | 'error';

export interface SessionState{
    sessionId: string;
    status: ChatStatus;
    error?: string
}