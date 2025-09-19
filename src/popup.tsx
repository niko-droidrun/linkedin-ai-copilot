import { useState, useRef, useEffect } from "react"
import "./output.css" // Make sure TailwindCSS is imported
import Header from "./Header"
import { profile } from "./mock"
import ProfileSummary from "./ProfileSummary"
import { inputMessageInput } from "./utils"

type Message = {
  role: "user" | "bot"
  content: string
}

type View = "chat" | "profile"

export default function IndexPopup() {
  const [currentView, setCurrentView] = useState<View>("chat")
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hello! Ask me anything 🚀" }
  ])
  const [prompt, setPrompt] = useState("")
  const chatEndRef = useRef<HTMLDivElement>(null)

  const examplePrompts = [
    "Summarize Profile",
    "Ask for a job"
  ]

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = () => {
    if (!prompt.trim()) return

    const rawHtml = document.documentElement.outerHTML
    const rawText = document.body.innerText

    console.log("Prompt:", prompt)
    console.log("Raw HTML:", rawHtml)
    console.log("Raw Text:", rawText)

    setPrompt("")
  }

  const handleExampleClick = (prompt: string) => {
    setPrompt(prompt)
  }

  return (
  <div className="w-80 h-[500px] flex flex-col font-sans border border-gray-200 rounded-lg overflow-hidden">
    {currentView === "profile" ? (
      <div>
        <Header title="Profile" onBack={() => setCurrentView("chat")} />
        <ProfileSummary profile={profile} />
      </div>
    ) : (
      <div className="flex flex-col h-full">
        <Header title="LinkedIn AI Assistant" />
        
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2 bg-white">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[70%] px-3 py-2 rounded-lg break-words ${
                msg.role === "user"
                  ? "self-end bg-blue-500 text-white"
                  : "self-start bg-gray-100 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>

        <div className="flex flex-wrap gap-2 p-2 border-b border-gray-200 bg-gray-50">
          {examplePrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleExampleClick(prompt)}
              className="bg-gray-100 border border-gray-300 rounded-lg px-2 py-1 text-xs hover:bg-gray-200"
            >
              {prompt}
            </button>
          ))}
        </div>

        <button
          onClick={() => setCurrentView("profile")}
          className="bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 mx-2 my-1"
        >
          Open Profile Summary
        </button>

        <button onClick={() => inputMessageInput("Hello")}>
          Text
        </button>

        {/* Chat Input */}
        <div className="border-t border-gray-200 p-2 flex gap-2 bg-gray-50">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message..."
            className="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </div>
    )}
  </div>
);

}