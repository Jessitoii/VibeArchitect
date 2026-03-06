import React from 'react';
import { useStore } from '../store';
import { Check, X, FileEdit } from 'lucide-react';
import { DiffEditor } from '@monaco-editor/react';

interface DiffViewerProps {
    filePath: string;
    original: string;
    modified: string;
    isDeletion?: boolean;
    onApprove: () => void;
    onReject: () => void;
}

export default function DiffViewer({ filePath, original, modified, isDeletion, onApprove, onReject }: DiffViewerProps) {
    return (
        <div className="absolute inset-0 bg-background/95 backdrop-blur-md z-[150] flex flex-col p-8">
            <div className="bg-surface border border-border rounded-xl shadow-2xl flex-1 flex flex-col overflow-hidden">
                <div className="p-6 border-b border-border flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <FileEdit className="text-primary" />
                            File Modification Request
                        </h2>
                        <p className="text-sm font-mono text-text-dim mt-1">{filePath}</p>
                    </div>
                </div>

                {isDeletion && (
                    <div className="bg-error/20 text-error p-4 text-center font-bold tracking-widest uppercase text-sm border-b border-error/50">
                        Warning: This action will permanently delete this file.
                    </div>
                )}

                <div className="flex-1 min-h-0 bg-background pt-2">
                    <DiffEditor
                        height="100%"
                        language={filePath.endsWith('.json') ? 'json' : filePath.endsWith('.py') ? 'python' : 'typescript'}
                        theme="vs-dark"
                        original={original}
                        modified={modified}
                        options={{
                            renderSideBySide: true,
                            readOnly: true,
                            minimap: { enabled: false },
                            automaticLayout: true,
                            fontSize: 14,
                        }}
                    />
                </div>

                <div className="p-6 border-t border-border flex justify-end gap-4 bg-background">
                    <button
                        onClick={onReject}
                        className="flex items-center gap-2 px-6 py-3 border border-error text-error hover:bg-error/10 rounded-lg font-bold"
                    >
                        <X size={18} />
                        Reject
                    </button>
                    <button
                        onClick={onApprove}
                        className="flex items-center gap-2 px-6 py-3 bg-success hover:bg-success/80 text-white rounded-lg font-bold shadow-lg shadow-success/20"
                    >
                        <Check size={18} />
                        Approve Change
                    </button>
                </div>
            </div>
        </div>
    );
}
