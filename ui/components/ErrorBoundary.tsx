import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught code error:", error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="absolute inset-0 bg-background flex items-center justify-center p-8 z-[200]">
                    <div className="bg-surface border border-error/30 p-10 rounded-3xl shadow-2xl text-center w-full max-w-xl space-y-6">
                        <div className="w-16 h-16 bg-error/10 text-error rounded-full flex items-center justify-center mx-auto">
                            <AlertTriangle size={32} />
                        </div>
                        <div className="space-y-4">
                            <h2 className="text-2xl font-bold">UI Component Crashed</h2>
                            <p className="text-text-dim text-sm overflow-auto max-h-32 p-4 bg-background/50 rounded-lg text-left font-mono">
                                {this.state.error?.message || "Unknown error occurred"}
                            </p>
                        </div>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full flex items-center justify-center gap-2 py-4 bg-error hover:bg-error/80 text-white font-bold rounded-2xl transition-all active:scale-95"
                        >
                            <RefreshCcw size={18} />
                            Reload App
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
