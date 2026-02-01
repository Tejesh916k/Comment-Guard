import React, { useState, useRef } from 'react';
import { Heart, MessageCircle, Send, Bookmark, MoreHorizontal, AlertOctagon, Smile } from 'lucide-react';
import { cn } from '../lib/utils';
import api from '../api';

const PostCard = ({ post }) => {
    const [commentText, setCommentText] = useState("");
    const [comments, setComments] = useState(post.comments || []);
    const [isChecking, setIsChecking] = useState(false);
    const [isToxic, setIsToxic] = useState(false);
    const [checkError, setCheckError] = useState(null);
    const [isLiked, setIsLiked] = useState(false);
    const [likeAnim, setLikeAnim] = useState(false);
    const debounceTimer = useRef(null);

    const isCeleb = post.userType === "celeb";

    const handleInputChange = (e) => {
        const text = e.target.value;
        setCommentText(text);
        setCheckError(null);

        // Debounced Agent Check
        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        if (!text.trim()) {
            setIsToxic(false);
            setIsChecking(false);
            return;
        }

        setIsChecking(true);
        debounceTimer.current = setTimeout(async () => {
            try {
                // Pass strictness based on userType
                const strictness = isCeleb ? "high" : "low";
                const response = await api.post('/analyze', { text, strictness });

                setIsToxic(response.data.is_toxic);
            } catch (error) {
                console.error("Agent check error", error);
                setCheckError("Agent unreachable");
            } finally {
                setIsChecking(false);
            }
        }, 500);
    };

    const handlePost = () => {
        if (!commentText.trim() || isToxic || isChecking) return;

        const newComment = {
            id: Date.now(),
            user: "me",
            text: commentText
        };
        setComments([...comments, newComment]);
        setCommentText("");
        setIsToxic(false);
    };

    const toggleLike = () => {
        if (!isLiked) {
            setLikeAnim(true);
            setTimeout(() => setLikeAnim(false), 300);
        }
        setIsLiked(!isLiked);
    };

    return (
        <div className="flex flex-col border-b border-gray-800 pb-5 mb-4">
            {/* Header */}
            <div className="flex items-center justify-between py-3 px-1">
                <div className="flex items-center gap-3 cursor-pointer">
                    <div className="w-[42px] h-[42px] rounded-full bg-gradient-to-tr from-yellow-400 to-fuchsia-600 p-[2px]">
                        <div className="w-full h-full rounded-full border border-black overflow-hidden bg-gray-800">
                            <img src={post.avatar} alt={post.username} className="w-full h-full object-cover" />
                        </div>
                    </div>
                    <div className="flex flex-col -space-y-[2px]">
                        <div className="flex items-center gap-1">
                            <span className="font-semibold text-sm hover:opacity-80 transition-opacity">{post.username}</span>
                            {isCeleb && <span className="w-3 h-3 bg-blue-500 rounded-full text-[8px] flex items-center justify-center text-black">✓</span>}
                            <span className="text-gray-500 text-xs text font-medium">• 1h</span>
                        </div>
                        {post.location && <span className="text-xs text-gray-400 font-normal">{post.location}</span>}
                    </div>
                </div>
                <MoreHorizontal className="w-6 h-6 text-white cursor-pointer hover:text-gray-400" />
            </div>

            {/* Image */}
            <div className="w-full rounded-md border border-gray-800 overflow-hidden bg-gray-900 aspect-[4/5] relative group">
                <img src={post.image} alt="Post" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.01]" />
            </div>

            {/* Actions */}
            <div className="flex justify-between mt-3 mb-2 px-1">
                <div className="flex gap-4 items-center">
                    <button onClick={toggleLike} className={`transition-transform duration-200 active:scale-90 focus:outline-none ${likeAnim ? 'animate-like' : ''}`}>
                        <Heart className={cn("w-7 h-7 cursor-pointer hover:text-gray-400 transition-colors", isLiked ? "fill-red-500 text-red-500" : "text-white")} strokeWidth={2} />
                    </button>
                    <MessageCircle className="w-7 h-7 hover:text-gray-400 cursor-pointer -rotate-[85deg]" strokeWidth={2} />
                    <Send className="w-7 h-7 hover:text-gray-400 cursor-pointer" strokeWidth={2} />
                </div>
                <Bookmark className="w-7 h-7 hover:text-gray-400 cursor-pointer" strokeWidth={2} />
            </div>

            {/* Likes */}
            <p className="font-semibold text-sm mb-2 px-1">{isLiked ? parseInt(post.likes.replace('M', '000000').replace('K', '000')) + 1 : post.likes} likes</p>

            {/* Caption */}
            <div className="mb-2 px-1">
                <span className="font-semibold text-sm mr-2">{post.username}</span>
                <span className="text-sm text-gray-100">{post.caption}</span>
            </div>

            {/* Comments Preview */}
            {comments.length > 0 && (
                <div className="mb-2 space-y-1 px-1">
                    <p className="text-gray-500 text-sm cursor-pointer mb-1">View all {comments.length + 15} comments</p>
                    {comments.slice(-2).map(c => (
                        <div key={c.id} className="text-sm flex gap-2">
                            <span className="font-semibold">{c.user}</span>
                            <span>{c.text}</span>
                            <Heart className="w-3 h-3 text-gray-500 ml-auto mt-1" />
                        </div>
                    ))}
                </div>
            )}

            {/* Comment Input */}
            <div className="flex items-center gap-3 mt-1 px-1">
                <div className="flex-1 relative">
                    <input
                        type="text"
                        placeholder={isToxic ? "Message removed by Agent" : "Add a comment..."}
                        className={cn(
                            "bg-transparent w-full outline-none text-sm transition-colors placeholder-gray-500 py-2",
                            isToxic ? "text-red-500 placeholder-red-500/50" : "text-white"
                        )}
                        value={commentText}
                        onChange={handleInputChange}
                    />
                    {/* Agent Status Indicator */}
                    {commentText && (
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-2">
                            {isChecking && <span className="text-[10px] text-gray-500 animate-pulse">Checking...</span>}
                            {isToxic ? (
                                <AlertOctagon className="w-4 h-4 text-red-500" />
                            ) : (
                                !isChecking && commentText && (
                                    <button
                                        onClick={handlePost}
                                        className="text-blue-500 font-semibold text-sm hover:text-white transition-colors"
                                    >
                                        Post
                                    </button>
                                )
                            )}
                        </div>
                    )}
                </div>
                {!commentText && <Smile className="w-4 h-4 text-gray-500 cursor-pointer hover:text-gray-300" />}
            </div>

            {/* Dynamic Agent Helper Text */}
            {commentText && !isChecking && (
                <div className={`text-[10px] px-1 mt-1 font-medium transition-all duration-300 ${isToxic ? 'text-red-500' : 'text-gray-600'}`}>
                    {isToxic ? (
                        <span className="flex items-center gap-1">🚫 Toxic language detected. Please be kind.</span>
                    ) : (
                        isCeleb ? "🛡️ Strict Moderation (Celeb Post)" : "☺ Friendly Moderation"
                    )}
                </div>
            )}
        </div>
    );
};

export default PostCard;

