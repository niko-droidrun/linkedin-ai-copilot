// src/components/ProfileSummary.tsx
import type { ProfileData } from "./types"

interface ProfileSummaryProps {
  profile: ProfileData
}

export default function ProfileSummary({ profile }: ProfileSummaryProps) {
  return (
    <div className="flex flex-col p-3 border-b border-gray-200 bg-gray-50 space-y-2">
      {/* Top: Avatar and Basic Info */}
      <div className="flex items-center gap-3">
        <img
          src={profile.avatarUrl || profile.avatar || "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"}
          alt={profile.name}
          className="rounded-full w-12 h-12 object-cover"
        />
        <div>
          <div className="font-bold text-sm">{profile.name}</div>
          <div className="text-gray-500 text-xs">
            {profile.title || "LinkedIn User"} {profile.company || profile.current_company?.name ? `at ${profile.company || profile.current_company?.name}` : ""}
          </div>
          {(profile.location || profile.city) && (
            <div className="text-gray-400 text-xs">{profile.location || profile.city}</div>
          )}
        </div>
      </div>

      {/* LinkedIn Stats */}
      <div className="flex gap-4 text-xs text-gray-600">
        {profile.followers !== undefined && (
          <div>
            <span className="font-semibold">{profile.followers}</span> followers
          </div>
        )}
        {profile.connections !== undefined && (
          <div>
            <span className="font-semibold">{profile.connections}</span> connections
          </div>
        )}
      </div>

      {/* Summary */}
      {profile.summary && (
        <div className="text-gray-500 text-xs">{profile.summary}</div>
      )}

      {/* Activity Summary */}
      {profile.activity_summary && (
        <div className="text-gray-500 text-xs bg-blue-50 p-2 rounded">
          <span className="font-semibold">Recent Activity:</span> {profile.activity_summary}
        </div>
      )}

      {/* Skills */}
      {profile.skills && profile.skills.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {profile.skills.map((skill) => (
            <span
              key={skill}
              className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {/* Experience */}
      {profile.experiences && profile.experiences.length > 0 && (
        <div className="text-gray-600 text-xs space-y-1">
          {profile.experiences.map((exp, idx) => (
            <div key={idx}>
              <div className="font-semibold">{exp.role}</div>
              <div>{exp.company} • {exp.period}</div>
              {exp.location && <div className="text-gray-400">{exp.location}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {profile.education && profile.education.length > 0 && (
        <div className="text-gray-600 text-xs space-y-1">
          {profile.education.map((edu, idx) => (
            <div key={idx}>
              <div className="font-semibold">{edu.degree}</div>
              <div>{edu.school} • {edu.period}</div>
            </div>
          ))}
        </div>
      )}

      {/* Recent Activities */}
      {profile.activity && profile.activity.length > 0 && (
        <div className="text-gray-600 text-xs space-y-1">
          <div className="font-semibold text-gray-700">Recent Activities:</div>
          {profile.activity.slice(0, 3).map((activity, idx) => (
            <div key={activity.id} className="bg-white p-2 rounded border">
              <div className="text-gray-500 text-xs">{activity.interaction}</div>
              <div className="font-medium text-xs mt-1 line-clamp-2">
                {activity.title.length > 80 ? `${activity.title.substring(0, 80)}...` : activity.title}
              </div>
              {activity.link && (
                <a
                  href={activity.link}
                  target="_blank"
                  className="text-blue-600 text-xs underline mt-1 inline-block"
                >
                  View Post
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Social Links */}
      {profile.social && (
        <div className="flex gap-2 mt-1 text-xs">
          {profile.social.linkedin && (
            <a href={profile.social.linkedin} target="_blank" className="text-blue-700 underline">LinkedIn</a>
          )}
          {profile.social.twitter && (
            <a href={profile.social.twitter} target="_blank" className="text-blue-400 underline">Twitter</a>
          )}
          {profile.social.github && (
            <a href={profile.social.github} target="_blank" className="text-gray-800 underline">GitHub</a>
          )}
          {profile.social.website && (
            <a href={profile.social.website} target="_blank" className="text-gray-600 underline">Website</a>
          )}
        </div>
      )}

      {/* LinkedIn ID */}
      <div className="text-gray-400 text-xs">
        ID: {profile.linkedin_id}
      </div>
    </div>
  )
}
