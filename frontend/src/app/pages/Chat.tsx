import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router";
import { ArrowLeft, Send, Shield, FileText } from "lucide-react";
import ChatMessage from "../components/ChatMessage";
import { chatData } from "../services/api";
import { useAuth } from "../components/authContext/AuthContext";
import { UserRole, RBAC_CONFIG } from "../types/user";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: number;
  sources?: string[];
}

const departmentInfo: Record<string, { name: string; icon: string; color: string }> = {
  hr: { name: "Human Resources", icon: "👥", color: "bg-blue-500" },
  marketing: { name: "Marketing", icon: "📢", color: "bg-purple-500" },
  finance: { name: "Finance", icon: "💰", color: "bg-green-500" },
  engineering: { name: "Engineering", icon: "⚙️", color: "bg-orange-500" },
  general: { name: "General Data Team", icon: "📊", color: "bg-pink-500" },
};

export default function Chat() {
  const { department } = useParams<{ department: string }>();
  const navigate = useNavigate();

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 🔥 Context
  const { user, role, accessToken } = useAuth();

  const [chatRole, setChatRole] = useState<string>(department || 'hr');

  const deptInfo = chatRole ? departmentInfo[chatRole] : null;

  // 🔒 Protect route
  useEffect(() => {
    if (!user || !accessToken) {
      navigate("/");
    }
  }, [user, accessToken, navigate]);

  // Scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 🚀 SEND MESSAGE
  const handleSend = async () => {
    if (!inputText.trim() || !role || !accessToken) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: "user",
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      const response = await chatData({
        query: inputText,
        role: chatRole,
        user_role: role,
        // token: accessToken,
      });

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: "bot",
        timestamp: Date.now(),
        sources: response.sources,
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error("Chat error:", error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "❌ Error fetching response. Try again.",
        sender: "bot",
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* HEADER */}
      <header className="bg-white shadow-sm border-b-2 border-indigo-500">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>

          {deptInfo && (
            <>
              <div className={`${deptInfo.color} w-12 h-12 rounded-lg flex items-center justify-center text-2xl`}>
                {deptInfo.icon}
              </div>

              <div className="flex-1">
                <h1 className="text-xl font-semibold">{deptInfo.name}</h1>
                <p className="text-sm text-gray-600">RAG Assistant</p>
              </div>

              <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 rounded-full">
                <Shield className="w-4 h-4 text-indigo-600" />
                <span className="text-sm text-indigo-600">
                  {role === "executive" ? "Full Access" : "Team Access"}
                </span>
              </div>

              {role === "executive" && (
                <select
                  value={chatRole}
                  onChange={(e) => setChatRole(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                >
                  {Object.entries(departmentInfo).map(([key, info]) => (
                    <option key={key} value={key}>
                      {info.name}
                    </option>
                  ))}
                </select>
              )}
            </>
          )}
        </div>
      </header>

      {/* CHAT BODY */}
      <main className="flex-1 overflow-y-auto p-4 max-w-4xl mx-auto w-full">
        {messages.map((msg) => (
          <div key={msg.id}>
            <ChatMessage message={msg} />

            {/* {msg.sources?.length > 0 && (
              <div className="mt-2 bg-gray-50 border p-2 rounded">
                <div className="text-xs text-gray-600 flex items-center gap-2">
                  <FileText className="w-3 h-3" /> Sources:
                </div>
                {msg.sources.map((s, i) => (
                  <span key={i} className="text-xs mr-2">📄 {s}</span>
                ))}
              </div>
            )} */}
          </div>
        ))}

        {isLoading && <p className="text-gray-500">Typing...</p>}

        <div ref={messagesEndRef} />
      </main>

      {/* INPUT */}
      <div className="bg-white p-4 border-t">
        <div className="flex gap-2">
          <input
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask something..."
            className="flex-1 border p-3 rounded-lg"
          />

          <button
            onClick={handleSend}
            disabled={isLoading}
            className="bg-indigo-600 text-white px-4 rounded-lg"
          >
            <Send />
          </button>
        </div>
      </div>
    </div>
  );
}