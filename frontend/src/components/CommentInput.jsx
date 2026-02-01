import React, { useState, useEffect } from 'react';
import { analyzeComment } from '../api';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

const DEBOUNCE_DELAY = 500;

export default function CommentInput() {
    const [comment, setComment] = useState('');
    const [isAnalyzeLoading, setIsAnalyzeLoading] = useState(false);
    const [analysis, setAnalysis] = useState(null); // { is_toxic: bool, results: [] }
    const [error, setError] = useState(null);

    // Debounce logic
    useEffect(() => {
        const handler = setTimeout(() => {
            if (comment.trim()) {
                performAnalysis(comment);
            } else {
                setAnalysis(null);
            }
        }, DEBOUNCE_DELAY);

        return () => {
            clearTimeout(handler);
        };
    }, [comment]);

    const performAnalysis = async (text) => {
        setIsAnalyzeLoading(true);
        setError(null);
        try {
            const result = await analyzeComment(text);
            setAnalysis(result);
        } catch (err) {
            console.error(err);
            setError("Failed to analyze comment. Server might be offline.");
        } finally {
            setIsAnalyzeLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (analysis?.is_toxic) return;
        alert("Comment posted successfully! (Mock Action)");
        setComment('');
        setAnalysis(null);
    };

    const isToxic = analysis?.is_toxic;

    return (
        <div className="w-full space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                    <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-1">
                        Write a comment
                    </label>
                    <textarea
                        id="comment"
                        rows={5}
                        className={twMerge(
                            "w-full p-4 border rounded-lg focus:ring-2 focus:outline-none transition-colors resize-none",
                            isToxic
                                ? "border-red-500 focus:ring-red-200 bg-red-50"
                                : "border-gray-300 focus:ring-blue-200 focus:border-blue-500"
                        )}
                        placeholder="Share your thoughts..."
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                    />

                    {/* Analysis Status Indicator */}
                    <div className="absolute bottom-3 right-3">
                        {isAnalyzeLoading && (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        )}
                    </div>
                </div>

                {/* Feedback Section */}
                <div className="min-h-[2rem]">
                    {error && <p className="text-sm text-red-600">{error}</p>}

                    {analysis && (
                        <div className={clsx(
                            "p-3 rounded-md text-sm transition-all duration-300",
                            isToxic ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
                        )}>
                            {isToxic ? (
                                <div className="flex flex-col gap-1">
                                    <span className="font-bold flex items-center gap-2">
                                        ⚠️ {analysis.results.some(r => r.label === 'profanity_strict')
                                            ? "Prohibited Vocabulary Detected"
                                            : "Toxic Content Detected"}
                                    </span>
                                    <span className="text-xs opacity-80">
                                        {analysis.results.some(r => r.label === 'profanity_strict')
                                            ? "This comment contains restricted words."
                                            : `Flags: ${analysis.results
                                                .filter(r => r.score > 0.01)
                                                .sort((a, b) => b.score - a.score)
                                                .map(r => `${r.label} (${(r.score * 100).toFixed(0)}%)`)
                                                .join(', ')}`
                                        }
                                    </span>
                                    <p className="mt-1">Please revise your comment to be respectful.</p>
                                </div>
                            ) : (
                                <span className="flex items-center gap-2">
                                    ✅ Looks good!
                                </span>
                            )}
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={!comment.trim() || isToxic || isAnalyzeLoading}
                    className={twMerge(
                        "w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200",
                        (!comment.trim() || isToxic || isAnalyzeLoading)
                            ? "bg-gray-400 cursor-not-allowed"
                            : "bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    )}
                >
                    Post Comment
                </button>
            </form>
        </div>
    );
}
