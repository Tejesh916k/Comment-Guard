import React, { useState } from 'react';
import { Home, Search, Compass, Heart, MessageCircle, PlusSquare, Menu, User, Film, Shield } from 'lucide-react';
import PostCard from './PostCard';
import mockFeed from '../data/mockFeed.json';

const FeedLayout = () => {
    return (
        <div className="flex min-h-screen bg-black text-white font-sans">
            {/* Sidebar (Desktop) */}
            <div className="w-[245px] hidden md:flex flex-col border-r border-gray-800 p-3 pt-8 pb-5 fixed h-full bg-black z-20">
                <div className="px-3 mb-8">
                    {/* Comment Guard Logo with Shield */}
                    <div className="flex items-center gap-3">
                        <Shield className="w-8 h-8 text-blue-500" fill="currentColor" strokeWidth={2} />
                        <h1 className="text-2xl font-bold font-serif italic tracking-wider">Comment Guard</h1>
                    </div>
                </div>

                <nav className="flex-1 space-y-1">
                    <NavItem icon={<Home size={28} strokeWidth={2.5} />} label="Home" active />
                    <NavItem icon={<Search size={28} strokeWidth={2.5} />} label="Search" />
                    <NavItem icon={<Compass size={28} strokeWidth={2.5} />} label="Explore" />
                    <NavItem icon={<Film size={28} strokeWidth={2.5} />} label="Reels" />
                    <NavItem icon={<MessageCircle size={28} strokeWidth={2.5} />} label="Messages" />
                    <NavItem icon={<Heart size={28} strokeWidth={2.5} />} label="Notifications" />
                    <NavItem icon={<PlusSquare size={28} strokeWidth={2.5} />} label="Create" />
                    <NavItem icon={<User size={28} strokeWidth={2.5} />} label="Profile" />
                </nav>

                <div className="mt-auto">
                    <NavItem icon={<Menu size={28} strokeWidth={2.5} />} label="More" />
                </div>
            </div>

            {/* Bottom Nav (Mobile) */}
            <div className="md:hidden fixed bottom-0 w-full bg-black border-t border-gray-800 flex justify-around p-3 z-20">
                <Home size={28} strokeWidth={2} />
                <Compass size={28} strokeWidth={2} />
                <Film size={28} strokeWidth={2} />
                <PlusSquare size={28} strokeWidth={2} />
                <MessageCircle size={28} strokeWidth={2} />
                <div className="w-7 h-7 rounded-full bg-gray-500 overflow-hidden">
                    <img src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop" className="w-full h-full object-cover" />
                </div>
            </div>

            {/* Main Feed Area */}
            <div className="flex-1 md:ml-[245px] flex justify-center w-full">
                <div className="w-full max-w-[630px] py-8 flex flex-col items-center">
                    {/* Stories Bar */}
                    <div className="w-full flex gap-4 overflow-x-auto pb-4 mb-4 no-scrollbar px-2 max-w-[630px]">
                        {mockFeed.map(user => (
                            <div key={user.id} className="flex flex-col items-center flex-shrink-0 cursor-pointer space-y-1">
                                <div className="w-[66px] h-[66px] rounded-full p-[3px] bg-gradient-to-tr from-yellow-400 via-red-500 to-fuchsia-600">
                                    <div className="w-full h-full rounded-full border-2 border-black overflow-hidden bg-gray-800">
                                        <img src={user.avatar} className="w-full h-full object-cover" alt={user.username} />
                                    </div>
                                </div>
                                <span className="text-xs text-center truncate w-[70px]">{user.username}</span>
                            </div>
                        ))}
                    </div>

                    {/* Feed Posts */}
                    <div className="w-full max-w-[470px] space-y-4">
                        {mockFeed.map(post => (
                            <PostCard key={post.id} post={post} />
                        ))}
                    </div>
                </div>
            </div>

            {/* Right Sidebar (Suggestions) */}
            <div className="hidden lg:block w-[320px] pl-10 pt-8 mr-10 sticky top-0 h-screen">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-700">
                            <img src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop" className="w-full h-full object-cover" />
                        </div>
                        <div>
                            <p className="font-semibold text-sm">my_profile_name</p>
                            <p className="text-gray-400 text-sm">My Name</p>
                        </div>
                    </div>
                    <button className="text-blue-500 text-xs font-semibold hover:text-white">Switch</button>
                </div>

                <div className="flex justify-between items-center mb-4">
                    <p className="text-gray-400 font-bold text-sm">Suggested for you</p>
                    <button className="text-white text-xs font-semibold hover:text-gray-300">See All</button>
                </div>

                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gray-800 overflow-hidden">
                                    <img src={`https://images.unsplash.com/photo-${1500000000000 + i}?w=50&h=50&fit=crop`} className="w-full h-full object-cover opacity-70" alt="suggested" />
                                </div>
                                <div>
                                    <p className="font-semibold text-sm">suggested_user_{i}</p>
                                    <p className="text-gray-400 text-xs">New to Instagram</p>
                                </div>
                            </div>
                            <button className="text-blue-500 text-xs font-semibold hover:text-white">Follow</button>
                        </div>
                    ))}
                </div>

                <div className="mt-8 text-xs text-gray-500 space-y-4">
                    <p>About · Help · Press · API · Jobs · Privacy · Terms · Locations · Language · Meta Verified</p>
                    <p>© 2026 INSTAGRAM FROM META</p>
                </div>
            </div>
        </div>
    );
};

const NavItem = ({ icon, label, active }) => (
    <div className={`flex items-center gap-4 p-3 my-1 rounded-lg hover:bg-white/10 cursor-pointer transition-all group ${active ? 'font-bold' : ''}`}>
        <div className="group-hover:scale-105 transition-transform duration-200">
            {icon}
        </div>
        <span className={`text-[16px] ${active ? 'font-bold' : 'font-normal'}`}>{label}</span>
    </div>
);

export default FeedLayout;
