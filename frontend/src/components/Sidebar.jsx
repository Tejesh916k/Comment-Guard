import React, { useState } from 'react';
import { Search, MoreVertical, MessageSquare, Users, CircleDashed } from 'lucide-react';
import { cn } from '../lib/utils';
import mockChats from '../data/mockChats.json';

const Sidebar = ({ onSelectChat, selectedChatId }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredChats = mockChats.filter(chat =>
        chat.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="w-[30%] h-full flex flex-col border-r border-gray-200 bg-white">
            {/* Header */}
            <div className="px-4 py-3 bg-[#F0F2F5] flex justify-between items-center border-b border-gray-200">
                <div className="w-10 h-10 rounded-full bg-gray-300 overflow-hidden cursor-pointer">
                    <img src="https://ui-avatars.com/api/?name=Me" alt="Profile" className="w-full h-full object-cover" />
                </div>
                <div className="flex gap-4 text-[#54656F]">
                    <Users className="w-6 h-6 cursor-pointer" />
                    <CircleDashed className="w-6 h-6 cursor-pointer" />
                    <MessageSquare className="w-6 h-6 cursor-pointer" />
                    <MoreVertical className="w-6 h-6 cursor-pointer" />
                </div>
            </div>

            {/* Search */}
            <div className="p-2 border-b border-gray-100 bg-white">
                <div className="flex items-center bg-[#F0F2F5] rounded-lg px-3 py-1.5">
                    <Search className="w-5 h-5 text-[#54656F] mr-3" />
                    <input
                        type="text"
                        placeholder="Search or start new chat"
                        className="bg-transparent border-none outline-none w-full text-sm placeholder:text-[#54656F]"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Filter Chips (Optional - Archive/Unread) */}
            <div className="flex gap-2 px-3 py-2 overflow-x-auto no-scrollbar">
                <button className="px-3 py-1 bg-[#E7FCE3] text-[#008069] rounded-full text-xs font-medium">All</button>
                <button className="px-3 py-1 bg-[#F0F2F5] text-[#54656F] rounded-full text-xs font-medium">Unread</button>
                <button className="px-3 py-1 bg-[#F0F2F5] text-[#54656F] rounded-full text-xs font-medium">Groups</button>
            </div>

            {/* Chat List */}
            <div className="flex-1 overflow-y-auto">
                {filteredChats.map((chat) => (
                    <div
                        key={chat.id}
                        onClick={() => onSelectChat(chat)}
                        className={cn(
                            "flex items-center px-3 py-3 cursor-pointer hover:bg-[#F5F6F6] transition-colors border-b border-gray-100",
                            selectedChatId === chat.id && "bg-[#F0F2F5]"
                        )}
                    >
                        <div className="w-12 h-12 rounded-full overflow-hidden mr-3 flex-shrink-0">
                            <img src={chat.avatar} alt={chat.name} className="w-full h-full object-cover" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-baseline mb-1">
                                <h3 className="text-[#111B21] text-base font-normal truncate">{chat.name}</h3>
                                <span className={cn(
                                    "text-xs",
                                    chat.unread > 0 ? "text-[#25D366] font-medium" : "text-[#667781]"
                                )}>{chat.time}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <p className="text-[#667781] text-sm truncate mr-2">
                                    {chat.lastMessage}
                                </p>
                                {chat.unread > 0 && (
                                    <span className="bg-[#25D366] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center">
                                        {chat.unread}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Sidebar;
