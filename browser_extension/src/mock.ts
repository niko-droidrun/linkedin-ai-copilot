import type { ProfileData } from "./types";

export const profile: ProfileData = {
  name: "Jane Doe",
  title: "Software Engineer",
  company: "TechCorp",
  location: "San Francisco, CA",
  avatarUrl: "https://placekitten.com/50/50",
  summary: "AI enthusiast & frontend developer",
  skills: ["TypeScript", "React", "TailwindCSS"],
  experiences: [
    { role: "Frontend Engineer", company: "TechCorp", period: "2022 - Present", location: "SF" },
    { role: "Intern", company: "StartupX", period: "2021", location: "Remote" }
  ],
  education: [
    { school: "MIT", degree: "B.Sc. Computer Science", period: "2018 - 2022" }
  ],
  social: {
    linkedin: "https://linkedin.com/in/janedoe",
    github: "https://github.com/janedoe",
    twitter: "https://twitter.com/janedoe"
  }
}