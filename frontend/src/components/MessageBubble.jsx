import React from 'react';
import { cn } from '../lib/utils';
import { Check, CheckCheck } from 'lucide-react';

const MessageBubble = ({ message, isOwn }) => {
    return (
        <div className={cn(
            "flex mb-1",
            isOwn ? "justify-end" : "justify-start"
        )}>
            <div className={cn(
                "max-w-[65%] px-2 pt-1.5 pb-1 rounded-lg text-[#111B21] text-sm relative shadow-sm",
                isOwn ? "bg-[#D9FDD3] rounded-tr-none" : "bg-white rounded-tl-none"
            )}>
                <p className="pr-2 break-words leading-relaxed">
                    {message.text}
                </p>
                <div className="flex justify-end items-end gap-1 mt-0.5">
                    <span className="text-[11px] text-[#667781] min-w-fit">
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {isOwn && (
                        <span className={cn(
                            "text-[16px]",
                            message.isRead ? "text-[#53bdeb]" : "text-[#667781]"
                        )}>
                            {message.isRead ? <CheckCheck size={14} /> : <Check size={14} />}
                        </span>
                    )}
                </div>

                {/* Tail SVG - optional, simplified with CSS rounded corners above for now */}
            </div>
        </div>
    );
};

export default MessageBubble;
