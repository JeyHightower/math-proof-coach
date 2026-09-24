'use client';

import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Message } from "@/types/chat";


interface MessageBubbleProps {
    message: Message;
}


export const MessageBubble = ({ message }: MessageBubbleProps) => {
    const isUser = message.role === "user";

    return (
        <div className={`flex w-full my-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${isUser
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-zinc-800 text-zinc-100 border border-zinc-700 rounded-bl-none'
                    }`}
            >
                <div className={`text-xs mb-1 font-medium ${isUser ? 'text-blue-200' : 'text-zinc-400'}`}>
                    {isUser ? 'You' : 'Math Coach'}
                </div>

                <div className="text-sm leading-relaxed overflow-x-auto">
                    <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                    >
                        {message.content}
                    </ReactMarkdown>
                </div>

            </div>

        </div>
    )

}