// src/api.ts
import type { LinkedInResponse } from "./types"

const API_BASE_URL = "http://localhost:8001"

export class LinkedInAPI {
  static async scrapeProfile(username: string): Promise<LinkedInResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/scrape/${username}`, {
        method: "GET",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json"
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: LinkedInResponse = await response.json()
      return data
    } catch (error) {
      console.error("Error scraping LinkedIn profile:", error)
      throw error
    }
  }

  static async scrapeProfileByUrl(url: string): Promise<LinkedInResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/scrape`, {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          url: url,
          user_id: "browser_extension_user"
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: LinkedInResponse = await response.json()
      return data
    } catch (error) {
      console.error("Error scraping LinkedIn profile by URL:", error)
      throw error
    }
  }

  static async healthCheck(): Promise<{ status: string; rams_connection: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: {
          "Accept": "application/json"
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Error checking API health:", error)
      throw error
    }
  }

  static extractUsernameFromUrl(url: string): string | null {
    try {
      // Extract username from LinkedIn URL
      const match = url.match(/linkedin\.com\/in\/([^\/\?]+)/i)
      return match ? match[1] : null
    } catch (error) {
      console.error("Error extracting username from URL:", error)
      return null
    }
  }
}