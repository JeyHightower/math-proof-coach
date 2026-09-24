'use client';

import { useState } from 'react';

interface MessageInputProps {
    onSendMessage: (content: string) => void;
    disabled: boolean;
}

export const MessageInput = ({ onSendMessage, disabled }: MessageInputProps) => {
    const [input, setInput] = useState("");

    const handleSubmit = (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        const trimmed = input.trim();
        if (!trimmed || disabled) return;

        onSendMessage(trimmed);
        setInput("");
    };


    return (
        <form onSubmit={handleSubmit} className="p-4 bg-zinc-900 border-t border-zinc-800">
            <div className="flex items-end gap-2 max-w-4xl max-auto bg-zinc-800 rounded-xl p-2 border border-zinc-700 focus-within:border-blue-500 transition-colors">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                        }
                    }}
                    placeholder="Write your proof step or question... (e.g., Let $f(x) > 0$ on $[a,b]$"
                    disabled={disabled}
                    rows={1}
                    className="flex-1 bg-transparent text-zinc-100 placeholder-zinc-500 resize-none outline-jnone px-2 py-1 text-sm min-h-[40px] max-h-[160px]"
                />
                <button
                    type="submit"
                    disabled={disabled || !input.trim()}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
                >
                    Send
                </button>
            </div>
        </form>
    );


};