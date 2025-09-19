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

export interface CurrentCompany {
  name?: string
  location?: string | null
}

export interface Activity {
  interaction: string
  link: string
  title: string
  img?: string
  id: string
}

export interface ProfileData {
  id: string
  name: string
  title?: string
  company?: string
  location?: string
  city?: string
  country_code?: string
  avatarUrl: string
  avatar?: string
  summary?: string
  experiences?: Experience[]
  experience?: any
  education?: Education[] | null
  skills?: string[]
  social?: SocialLinks
  current_company?: CurrentCompany
  followers?: number
  connections?: number
  url?: string
  input_url?: string
  linkedin_id?: string
  linkedin_num_id?: string
  banner_image?: string
  honors_and_awards?: any
  similar_profiles?: any[]
  default_avatar?: boolean
  memorialized_account?: boolean
  bio_links?: any[]
  first_name?: string
  last_name?: string
  timestamp?: string
  input?: {
    url: string
  }
  activity?: Activity[]
  activity_summary?: string
}

export interface LinkedInResponse {
  success: boolean
  profile_data: ProfileData | null
  formatted_output: string | null
  error: string | null
  cached: boolean
}
