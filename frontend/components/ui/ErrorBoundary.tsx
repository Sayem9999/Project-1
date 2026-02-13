'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/Button';

interface Props {
    children: ReactNode;
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
        console.error('[ErrorBoundary] Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="flex flex-col items-center justify-center min-h-[50vh] p-8 text-center bg-obsidian-900/50 rounded-[32px] border border-red-500/20 m-4">
                    <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center mb-6">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                    </div>
                    <h2 className="text-xl font-black text-white mb-2 uppercase tracking-widest">Component Node Fault</h2>
                    <p className="text-gray-500 text-sm mb-8 max-w-xs">{this.state.error?.message || 'A critical rendering error occurred in this section.'}</p>
                    <Button
                        variant="secondary"
                        onClick={() => {
                            this.setState({ hasError: false });
                            window.location.reload();
                        }}
                    >
                        Reset Interface Node
                    </Button>
                </div>
            );
        }

        return this.props.children;
    }
}
