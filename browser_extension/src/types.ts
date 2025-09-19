// src/types.ts
export interface Experience {
  role: string
  company: string
  period: string
  location?: string
}

export interface Education {
  school: string
  degree: string
  period: string
}

export interface SocialLinks {
  linkedin?: string
  twitter?: string
  github?: string
  website?: string
}

export interface ProfileData {
  name: string
  title: string
  company?: string
  location?: string
  avatarUrl: string
  summary?: string
  experiences?: Experience[]
  education?: Education[]
  skills?: string[]
  social?: SocialLinks
}
