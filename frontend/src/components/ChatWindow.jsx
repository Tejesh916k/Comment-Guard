import React, { useState, useEffect, useRef } from 'react';
import { MoreVertical, Search, Paperclip, Smile, Mic, Send, AlertCircle } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { cn } from '../lib/utils';
import api from '../api';

const ChatWindow = ({ chat }) => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Hello! Thank you for your application.", isOwn: true, timestamp: Date.now() - 1000000, isRead: true },
        { id: 2, text: chat.lastMessage, isOwn: false, timestamp: Date.now() - 500000, isRead: true },
    ]);
    const [inputText, setInputText] = useState("");
    const [isToxic, setIsToxic] = useState(false);
    const [isChecking, setIsChecking] = useState(false);
    const messagesEndRef = useRef(null);
    const debounceTimerRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, chat]);

    // Real-time validation
    useEffect(() => {
        if (!inputText.trim()) {
            setIsToxic(false);
            setIsChecking(false);
            return;
        }

        setIsChecking(true);
        if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

        debounceTimerRef.current = setTimeout(async () => {
            try {
                const response = await api.post('/analyze', { text: inputText });
                setIsToxic(response.data.is_toxic);
            } catch (error) {
                console.error("Check failed:", error);
            } finally {
                setIsChecking(false);
            }
        }, 500); // 500ms delay

        return () => {
            if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
        };
    }, [inputText]);

    const handleSend = async () => {
        if (!inputText.trim() || isToxic || isChecking) return;

        // Send User Message
        const newMessage = {
            id: Date.now(),
            text: inputText,
            isOwn: true,
            timestamp: Date.now(),
            isRead: false
        };

        setMessages(prev => [...prev, newMessage]);
        const userMessageText = inputText; // capture current text
        setInputText("");
        setIsToxic(false);

        // Auto-Reply Logic
        setTimeout(() => {
            let replyText = "I acknowledge receipt of your message.";
            const lowerText = userMessageText.toLowerCase();

            // Simple Contextual Replies
            if (lowerText.includes("hello") || lowerText.includes("hi")) {
                replyText = `Hello! How are things going with ${chat.name.split(' ')[0]}?`;
            } else if (lowerText.includes("interview")) {
                replyText = "I am available for an interview anytime this week.";
            } else if (lowerText.includes("resume") || lowerText.includes("cv")) {
                replyText = "I can send my updated resume if needed.";
            } else if (lowerText.includes("thanks") || lowerText.includes("thank you")) {
                replyText = "You're welcome!";
            } else if (lowerText.includes("?")) {
                replyText = "That's a good question. Let me check and get back to you.";
            } else {
                const genericReplies = [
                    "That sounds good.",
                    "I understand.",
                    "Could you elaborate on that?",
                    "Okay, noted.",
                    "I will get back to you shortly."
                ];
                replyText = genericReplies[Math.floor(Math.random() * genericReplies.length)];
            }

            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: replyText,
                isOwn: false,
                timestamp: Date.now(),
                isRead: true
            }]);
        }, 1500);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#EFEAE2]">
            {/* Header */}
            <div className="px-4 py-2 bg-[#F0F2F5] flex justify-between items-center border-l border-gray-300">
                <div className="flex items-center cursor-pointer">
                    <div className="w-10 h-10 rounded-full overflow-hidden mr-3">
                        <img src={chat.avatar} alt={chat.name} className="w-full h-full object-cover" />
                    </div>
                    <div>
                        <h3 className="text-[#111B21] text-base font-normal">{chat.name}</h3>
                        <p className="text-[#667781] text-xs">online</p>
                    </div>
                </div>
                <div className="flex gap-4 text-[#54656F]">
                    <Search className="w-6 h-6 cursor-pointer" />
                    <MoreVertical className="w-6 h-6 cursor-pointer" />
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 bg-[url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')] bg-repeat">
                <div className="flex justify-center mb-4">
                    <div className="bg-[#FFEECD] text-[#54656F] text-[12.5px] px-3 py-1.5 rounded-lg shadow-sm text-center max-w-[80%]">
                        Messages are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them.
                    </div>
                </div>

                {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} isOwn={msg.isOwn} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="px-4 py-2 bg-[#F0F2F5] flex items-center gap-2">
                <Smile className="w-6 h-6 text-[#54656F] cursor-pointer" />
                <Paperclip className="w-6 h-6 text-[#54656F] cursor-pointer" />

                <div className={cn(
                    "flex-1 rounded-lg px-4 py-2 ml-1 flex items-center bg-white border transition-colors duration-200",
                    isToxic ? "border-red-500 bg-red-50" : "border-transparent"
                )}>
                    <input
                        type="text"
                        className={cn(
                            "w-full bg-transparent border-none outline-none text-[15px] placeholder:text-[#667781]",
                            isToxic ? "text-red-600" : "text-[#111B21]"
                        )}
                        placeholder={isToxic ? "⚠️ Message contains toxic content" : "Type a message"}
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={handleKeyPress}
                    />
                    {isChecking && <span className="text-xs text-gray-400 ml-2 animate-pulse">Checking...</span>}
                    {isToxic && <AlertCircle className="w-5 h-5 text-red-500 ml-2" />}
                </div>

                {inputText && !isToxic && !isChecking ? (
                    <Send onClick={handleSend} className="w-6 h-6 text-[#54656F] cursor-pointer" />
                ) : (
                    <div className="w-6 h-6 flex items-center justify-center">
                        {isToxic ? (
                            <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center cursor-not-allowed">
                                <span className="text-red-500 text-xs font-bold">!</span>
                            </div>
                        ) : (
                            <Mic className="w-6 h-6 text-[#54656F] cursor-pointer" />
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatWindow;
