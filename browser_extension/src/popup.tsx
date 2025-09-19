import { useState, useRef, useEffect } from "react"
import "./output.css" // Make sure TailwindCSS is imported
import Header from "./Header"
import { profile } from "./mock"
import ProfileSummary from "./ProfileSummary"
import { inputMessageInput } from "./utils"
import { LinkedInAPI } from "./api"
import type { ProfileData, LinkedInResponse } from "./types"

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
  const [profileData, setProfileData] = useState<ProfileData>(profile) // Start with mock data
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const examplePrompts = [
    "Summarize Profile",
    "Ask for a job"
  ]

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Function to get current LinkedIn profile from the page
  const getCurrentLinkedInProfile = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Get current tab URL using Chrome extension API
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
      const currentTab = tabs[0]
      
      if (!currentTab?.url) {
        throw new Error("Could not access current tab URL")
      }

      const username = LinkedInAPI.extractUsernameFromUrl(currentTab.url)
      
      if (!username) {
        throw new Error("Current page is not a LinkedIn profile. Please navigate to a LinkedIn profile page.")
      }

      // Fetch profile data from our Python server
      const response: LinkedInResponse = await LinkedInAPI.scrapeProfile(username)
      
      if (response.success && response.profile_data) {
        setProfileData(response.profile_data)
        setMessages(prev => [...prev,
          { role: "bot", content: `✅ Successfully loaded profile for ${response.profile_data.name}! ${response.cached ? "(cached)" : "(fresh)"}` }
        ])
      } else {
        throw new Error(response.error || "Failed to fetch profile data")
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMsg)
      setMessages(prev => [...prev,
        { role: "bot", content: `❌ Error: ${errorMsg}` }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // Function to scrape a specific LinkedIn profile by username
  const scrapeLinkedInProfile = async (username: string) => {
    try {
      setIsLoading(true)
      setError(null)

      const response: LinkedInResponse = await LinkedInAPI.scrapeProfile(username)
      
      if (response.success && response.profile_data) {
        setProfileData(response.profile_data)
        setMessages(prev => [...prev,
          { role: "bot", content: `✅ Successfully scraped profile for ${response.profile_data.name}! ${response.cached ? "(from cache)" : "(fresh data)"}` }
        ])
      } else {
        throw new Error(response.error || "Failed to scrape profile")
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMsg)
      setMessages(prev => [...prev,
        { role: "bot", content: `❌ Error: ${errorMsg}` }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    if (!prompt.trim()) return

    // Add user message
    setMessages(prev => [...prev, { role: "user", content: prompt }])
    
    // Handle different commands
    if (prompt.toLowerCase().includes("scrape") || prompt.toLowerCase().includes("load profile")) {
      await getCurrentLinkedInProfile()
    } else if (prompt.toLowerCase().startsWith("scrape ")) {
      // Extract username from command like "scrape niels-schmidt-890b96303"
      const username = prompt.split(" ")[1]
      if (username) {
        await scrapeLinkedInProfile(username)
      } else {
        setMessages(prev => [...prev,
          { role: "bot", content: "Please provide a username. Example: 'scrape niels-schmidt-890b96303'" }
        ])
      }
    } else if (prompt.toLowerCase().includes("summarize profile")) {
      // Generate profile summary
      const summary = `📊 Profile Summary for ${profileData.name}:
• Location: ${profileData.city || profileData.location || "Unknown"}
• Network: ${profileData.followers} followers, ${profileData.connections} connections
• Activity: ${profileData.activity_summary || "No recent activity data"}
• LinkedIn ID: ${profileData.linkedin_id}`
      
      setMessages(prev => [...prev, { role: "bot", content: summary }])
    } else {
      // Default response
      setMessages(prev => [...prev,
        { role: "bot", content: "I can help you scrape LinkedIn profiles! Try: 'scrape username' or 'load profile' for current page." }
      ])
    }

    setPrompt("")
  }

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt)
  }

  return (
  <div className="w-80 h-[500px] flex flex-col font-sans border border-gray-200 rounded-lg overflow-hidden">
    {currentView === "profile" ? (
      <div>
        <Header title="Profile" onBack={() => setCurrentView("chat")} />
        <ProfileSummary profile={profileData} />
      </div>
    ) : (
      <div className="flex flex-col h-full">
        <Header title="LinkedIn AI Assistant" />
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="bg-blue-50 text-blue-700 text-xs p-2 text-center">
            🔄 Loading LinkedIn data...
          </div>
        )}

        {/* Error indicator */}
        {error && (
          <div className="bg-red-50 text-red-700 text-xs p-2 text-center">
            ❌ {error}
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2 bg-white">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[70%] px-3 py-2 rounded-lg break-words text-xs ${
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
          {examplePrompts.map((examplePrompt) => (
            <button
              key={examplePrompt}
              onClick={() => handleExampleClick(examplePrompt)}
              className="bg-gray-100 border border-gray-300 rounded-lg px-2 py-1 text-xs hover:bg-gray-200"
            >
              {examplePrompt}
            </button>
          ))}
          <button
            onClick={() => handleExampleClick("scrape niels-schmidt-890b96303")}
            className="bg-blue-100 border border-blue-300 rounded-lg px-2 py-1 text-xs hover:bg-blue-200"
          >
            Load Niels Profile
          </button>
          <button
            onClick={getCurrentLinkedInProfile}
            className="bg-green-100 border border-green-300 rounded-lg px-2 py-1 text-xs hover:bg-green-200"
            disabled={isLoading}
          >
            Load Current Page
          </button>
        </div>

        <button
          onClick={() => setCurrentView("profile")}
          className="bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 mx-2 my-1"
        >
          View Profile ({profileData.name})
        </button>

        {/* Chat Input */}
        <div className="border-t border-gray-200 p-2 flex gap-2 bg-gray-50">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Try: 'scrape username' or 'load profile'"
            className="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
            disabled={isLoading}
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
      </div>
    )}
  </div>
);

}