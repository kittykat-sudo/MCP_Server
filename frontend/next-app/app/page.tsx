"use client";

import { useState } from "react";
import ChatComponent from "./components/ChatComponent";
import EmailComponent from "./components/EmailComponent";
import ResumeUpload from "./components/ResumeUpload";

export default function Home() {
  const [activeTab, setActiveTab] = useState("chat");

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            MCP Server Playground
          </h1>
          <p className="text-gray-600">
            AI-powered chat about your CV with email notification capabilities
          </p>
        </header>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-sm p-1">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === "chat"
                  ? "bg-blue-500 text-white"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              CV Chat
            </button>
            <button
              onClick={() => setActiveTab("email")}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === "email"
                  ? "bg-blue-500 text-white"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Send Email
            </button>
            <button
              onClick={() => setActiveTab("upload")}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === "upload"
                  ? "bg-blue-500 text-white"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Upload Resume
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-4xl mx-auto">
          {activeTab === "chat" && <ChatComponent />}
          {activeTab === "email" && <EmailComponent />}
          {activeTab === "upload" && <ResumeUpload />}
        </div>
      </div>
    </main>
  );
}
