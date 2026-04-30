import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Bot,
  CalendarCheck,
  Circle,
  ExternalLink,
  Loader2,
  Mail,
  Moon,
  Phone,
  Send,
  Sparkles,
  Sun,
  Trash2,
  User,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8010";

const suggestedTopics = [
  "What does Alfred Lab do?",
  "How can I contact Alfred Lab?",
  "What are the phone reception hours?",
  "How fast are asbestos reports delivered?",
  "What asbestos analysis method is used?",
  "Can I book a one-on-one session?",
];

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi, I am Alfred Lab's website assistant. Ask me about asbestos analysis, reports, contact details, or booking a one-on-one session.",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState({ status: "checking", faiss_ready: false });
  const [contact, setContact] = useState({
    phone: "+81 53-525-8422",
    email: "info.india@alfred-lab.in",
    hours: "9:00-18:00, excluding Sundays and public holidays",
  });
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");
  const [sessionForm, setSessionForm] = useState({
    name: "",
    email: "",
    organization: "",
    topic: "",
  });
  const [sessionStatus, setSessionStatus] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((response) => response.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "offline", faiss_ready: false }));

    fetch(`${API_BASE}/api/contact`)
      .then((response) => response.json())
      .then(setContact)
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function sendMessage(event, overrideMessage) {
    event?.preventDefault();
    const question = (overrideMessage ?? input).trim();
    if (!question || isLoading) return;

    setInput("");
    setMessages((current) => [...current, { role: "user", content: question, sources: [] }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Backend request failed");
      }

      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.answer, sources: data.sources ?? [] },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `Error: ${error.message}`, sources: [] },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  async function clearChat() {
    await fetch(`${API_BASE}/api/clear`, { method: "POST" }).catch(() => {});
    setMessages([
      {
        role: "assistant",
        content: "Chat cleared. What would you like to know about Alfred Lab?",
        sources: [],
      },
    ]);
  }

  async function submitSession(event) {
    event.preventDefault();
    setSessionStatus("Sending request...");

    try {
      const response = await fetch(`${API_BASE}/api/session-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sessionForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not submit request");
      }

      setSessionStatus("Request saved. Alfred Lab can follow up from the submitted details.");
      setSessionForm({ name: "", email: "", organization: "", topic: "" });
    } catch (error) {
      setSessionStatus(`Error: ${error.message}`);
    }
  }

  const ready = health.status === "ok" && health.faiss_ready;

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <section className="workspace">
        <section className="chat-panel">
          <header className="topbar">
            <div>
              <div className="eyebrow">
                <Sparkles size={15} />
                Local FAISS company assistant
              </div>
              <h1>Alfred Lab Chatbot</h1>
              <p>Ask about asbestos analysis services, reports, contact details, and booking support.</p>
            </div>
            <div className="top-actions">
              <div className={`status ${ready ? "ready" : "not-ready"}`}>
                <Circle size={10} fill="currentColor" />
                <span>{ready ? "Ready" : "Check backend"}</span>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                title="Toggle dark mode"
              >
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </header>

          <div className="suggestions" aria-label="Suggested topics">
            {suggestedTopics.map((topic) => (
              <button type="button" key={topic} onClick={() => sendMessage(null, topic)}>
                {topic}
              </button>
            ))}
          </div>

          <div className="messages" aria-live="polite">
            {messages.map((message, index) => (
              <Message key={`${message.role}-${index}`} message={message} />
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="avatar"><Bot size={18} /></div>
                <div className="bubble loading">
                  <Loader2 className="spin" size={18} />
                  Thinking
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="composer" onSubmit={sendMessage}>
            <button type="button" className="icon-button" onClick={clearChat} title="Clear chat">
              <Trash2 size={18} />
            </button>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about Alfred Lab..."
              aria-label="Message"
            />
            <button type="submit" className="send-button" disabled={isLoading || !input.trim()} title="Send">
              <Send size={18} />
            </button>
          </form>
        </section>

        <aside className="side-panel">
          <section className="panel-section contact-card">
            <h2>Contact</h2>
            <a href={`tel:${contact.phone.replaceAll(" ", "")}`} className="contact-row">
              <Phone size={18} />
              <span>{contact.phone}</span>
            </a>
            <a href={`mailto:${contact.email}`} className="contact-row">
              <Mail size={18} />
              <span>{contact.email}</span>
            </a>
            <p className="hours">Reception hours: {contact.hours}</p>
          </section>

          <section className="panel-section newsletter-card">
            <h2>Sign up for our email newsletter here!</h2>
            <p>Share your details for updates, guidance, or a one-on-one conversation.</p>
          </section>

          <section className="panel-section">
            <h2>Book a one-on-one session</h2>
            <form className="session-form" onSubmit={submitSession}>
              <label>
                Name
                <input
                  value={sessionForm.name}
                  onChange={(event) => setSessionForm({ ...sessionForm, name: event.target.value })}
                  required
                  minLength={2}
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={sessionForm.email}
                  onChange={(event) => setSessionForm({ ...sessionForm, email: event.target.value })}
                  required
                />
              </label>
              <label>
                Name of organisation
                <input
                  value={sessionForm.organization}
                  onChange={(event) => setSessionForm({ ...sessionForm, organization: event.target.value })}
                  required
                  minLength={2}
                />
              </label>
              <label>
                Topic
                <textarea
                  value={sessionForm.topic}
                  onChange={(event) => setSessionForm({ ...sessionForm, topic: event.target.value })}
                  placeholder="Example: asbestos testing for a renovation project"
                  required
                  minLength={2}
                />
              </label>
              <button type="submit" className="session-button">
                <CalendarCheck size={18} />
                Request session
              </button>
              {sessionStatus && <p className="form-status">{sessionStatus}</p>}
            </form>
          </section>
        </aside>
      </section>
    </main>
  );
}

function Message({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? <User size={18} /> : <Bot size={18} />}</div>
      <div className="message-body">
        <div className="bubble">{message.content}</div>
        {!isUser && message.sources?.length > 0 && (
          <div className="sources">
            {message.sources.map((source, index) => (
              <a key={`${source.url}-${index}`} href={source.url} target="_blank" rel="noreferrer">
                <span>{source.title || "Source"}</span>
                <ExternalLink size={14} />
              </a>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

createRoot(document.getElementById("root")).render(<App />);
