export interface CandidateProfile {
  id: string;
  name: string;
  email: string;
  skills: string[];
  experience_years: number;
  location: string;
  seniority: string;
  resume_text?: string;
  created_at: string;
}

export interface MatchJob {
  id: string;
  candidate_id: string;
  job_description: string;
  source_url?: string;
  status: "pending" | "processing" | "completed" | "failed" | "dead";
  
  overall_score?: number;
  skill_score?: number;
  experience_score?: number;
  location_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  recommendation?: string;
  
  error_message?: string;
  retry_count: number;
  created_at: string;
  updated_at: string;
}

export interface MatchBatchResponse {
  jobs: MatchJob[];
  total: number;
}

export interface MatchListResponse {
  data: MatchJob[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  }
}
