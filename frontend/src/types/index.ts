export interface UserProfile {
  grade: string;
  interests: string[];
  personality: string[];
  strengths: string[];
  duration: string;
}

export interface ResearchTheme {
  id: string;
  title: string;
  description: string;
  materials: string[];
  steps: string[];
  estimatedDays: number;
  difficulty: 'easy' | 'medium' | 'hard';
}
