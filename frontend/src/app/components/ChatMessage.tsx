interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: number;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isBot = message.sender === "bot";

  return (
    <div className={`flex ${isBot ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 ${
          isBot
            ? "bg-white border border-gray-200 text-gray-800"
            : "bg-indigo-600 text-white"
        }`}
      >
        <p className="text-sm leading-relaxed">{message.text}</p>
        <p
          className={`text-xs mt-1 ${
            isBot ? "text-gray-500" : "text-indigo-200"
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
