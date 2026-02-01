import React, { useState } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import mockChats from '../data/mockChats.json';

const ChatLayout = () => {
    const [selectedChat, setSelectedChat] = useState(null);

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-[#d1d7db] font-sans">
            {/* Main Container - Centered for desktop look if needed, or full screen */}
            <div className="flex w-full h-full max-w-[1700px] mx-auto bg-white shadow-lg overflow-hidden relative">
                <div className="green-header absolute top-0 left-0 w-full h-[127px] bg-[#00a884] -z-10 hidden md:block"></div>

                <Sidebar
                    onSelectChat={setSelectedChat}
                    selectedChatId={selectedChat?.id}
                />

                {selectedChat ? (
                    <div className="flex-1 w-[70%] h-full">
                        <ChatWindow chat={selectedChat} />
                    </div>
                ) : (
                    <div className="flex-1 w-[70%] h-full bg-[#F0F2F5] flex flex-col justify-center items-center border-l border-gray-300 border-b-[6px] border-b-[#25D366]">
                        {/* WhatsApp Web Default Welcome Screen Clone */}
                        <div className="text-center">
                            <h1 className="text-[#41525d] text-[32px] font-light mt-10">WhatsApp Web</h1>
                            <p className="text-[#667781] mt-4 text-sm font-normal">
                                Send and receive messages without keeping your phone online.<br />
                                Use WhatsApp on up to 4 linked devices and 1 phone.
                            </p>
                            <div className="mt-10 text-[#8696a0] text-xs flex items-center justify-center gap-1">
                                Locks are end-to-end encrypted
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatLayout;
