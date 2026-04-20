import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
};

export default function MessageBubble({
  role,
  content,
  pending = false,
}: MessageBubbleProps) {
  return (
    <div className={`message-row ${role === "user" ? "message-row-user" : "message-row-assistant"}`}>
      <div className={`message ${role === "user" ? "message-user" : "message-assistant"}`}>
        {content ? (
          role === "assistant" ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          ) : (
            content
          )
        ) : pending ? (
          <span className="assistant-thinking">Pensando...</span>
        ) : null}
      </div>
    </div>
  );
}