'use client';

import { useEffect, useRef } from 'react';
import { Message, ChatStatus } from '@/types/chat';
import { MessageBubble } from './MessageBubble';


interface MessageListProps {
    messages: Message[];
    status: ChatStatus;
}

export const MessageList = ({ messages, status }: MessageListProps) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, status]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {messages.length === 0 ? (
                <div className="flex flex-col item-center justify-center h-full text-zinc-500 text-center px-4">
                    <p className="text-base font-medium text-zinc-300">Welcome to Math Proof Coach</p>
                    <p className="text-sm mt-1 max-w-md">
                        Enter a Theorem, proof problem, or mathematical statement below to start your coaching session.
                    </p>
                </div>
            ) : (
                messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))
            )}

            {status === 'loading' && (
                <div className="flex justify-start my-2">
                    <div className="bg-zinc-800 border border-zinc-700 rounded-2xl rounded-bl-none px-4 py-3 text-zinc-400 text-sm flex items-center space-x-2 shadow-sm">
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
                        <span>Coach is analyzing your proof...</span>
                    </div>
                </div>
            )}
            <div ref={bottomRef} />
        </div>
    );

};
