"use client";
import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  name?: string;
}

interface State {
  hasError: boolean;
  errorMsg: string;
}

export class RehealErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, errorMsg: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMsg: error.message };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[Reheal Boundary: ${this.props.name || "Unknown"}]`, error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-center">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
          <h3 className="text-sm font-bold text-white/90 mb-1">خطایی در {this.props.name || "کامپوننت"} رخ داد</h3>
          <p className="text-xs text-rose-200/60 mb-4">{this.state.errorMsg}</p>
          <button
            onClick={() => this.setState({ hasError: false, errorMsg: "" })}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" /> بازیابی مجدد
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
