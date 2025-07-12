// 学年の型定義
export type Grade =
  | "elementary1"
  | "elementary2"
  | "elementary3"
  | "elementary4"
  | "elementary5"
  | "elementary6"
  | "junior1"
  | "junior2"
  | "junior3";

// 興味分野の型定義
export type Interest =
  | "science"
  | "nature"
  | "technology"
  | "art"
  | "sports"
  | "music"
  | "cooking"
  | "animals"
  | "space"
  | "history"
  | "math";

// 性格特性の型定義
export type Personality =
  | "curious"
  | "patient"
  | "creative"
  | "active"
  | "careful"
  | "social"
  | "independent"
  | "persistent"
  | "analytical";

// 得意分野の型定義
export type Strength =
  | "observation"
  | "writing"
  | "drawing"
  | "calculation"
  | "experiment"
  | "presentation"
  | "research"
  | "craft"
  | "crafting"
  | "calculating"
  | "reading";

// 研究期間の型定義
export type Duration =
  | "1week"
  | "2weeks"
  | "3weeks"
  | "4weeks"
  | "longer"
  | "1month"
  | "2months"
  | "flexible";

// ジャンルの型定義
export type Genre =
  | "experiment"
  | "observation"
  | "research";

export interface UserProfile {
  grade: Grade;
  interests: Interest[];
  personality: Personality[];
  strengths: Strength[];
  duration: Duration;
}

// フォーム用の部分的なUserProfile型
export interface PartialUserProfile {
  grade?: Grade;
  interests: Interest[];
  personality: Personality[];
  strengths: Strength[];
  duration?: Duration;
}

export interface ResearchTheme {
  id: string;
  title: string;
  description: string;
  genre: Genre;
  materials: string[];
  steps: string[];
  estimatedDays: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

// AIが生成する研究計画のステップ
export interface AIResearchStep {
  title: string;
  description: string;
  tips: string[];
  duration: string;
  order: number;
}

// AIが生成する研究計画
export interface AIResearchPlan {
  theme_id: string;
  theme_title: string;
  steps: AIResearchStep[];
  total_estimated_days: number;
  difficulty: 'easy' | 'medium' | 'hard';
  genre: Genre;
}

// 研究計画生成API関連の型
export interface GeneratePlanRequest {
  theme_id: string;
}

export interface GeneratePlanResponse {
  success: boolean;
  message: string;
  plan?: AIResearchPlan;
}

export interface GetSavedThemeResponse {
  success: boolean;
  message: string;
  theme?: ResearchTheme;
  user_profile?: UserProfile;
}

export interface GetResearchPlanResponse {
  success: boolean;
  message: string;
  plan?: AIResearchPlan;
  is_cached: boolean;
}

export interface ResearchProject {
  id: string;
  userId: string;
  themeId: string;
  title: string;
  description: string;
  genre?: Genre;
  status: 'planning' | 'in_progress' | 'completed' | 'paused';
  startDate: string;
  targetEndDate: string;
  actualEndDate?: string;
  customMaterials: string[];
  customSteps: string[];
  progressPercentage: number;
  currentStepIndex: number;
  createdAt: string;
  updatedAt: string;
}

export interface ResearchStep {
  id: string;
  projectId: string;
  stepNumber: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  plannedDate?: string;
  completedDate?: string;
  notes: { [key: string]: any };
  createdAt: string;
  updatedAt: string;
}

export interface Record {
  id: string;
  projectId: string;
  stepId?: string;
  recordType: 'observation' | 'experiment' | 'photo' | 'note' | 'data';
  title: string;
  content: string;
  data: { [key: string]: any };
  recordDate: string;
  weatherInfo?: { [key: string]: any };
  locationInfo?: { [key: string]: any };
  createdAt: string;
  updatedAt: string;
}

export interface Media {
  id: string;
  recordId: string;
  mediaType: 'image' | 'video' | 'audio';
  filePath: string;
  originalFilename: string;
  fileSize: number;
  metadata: { [key: string]: any };
  aiAnalysis?: string;
  analysisData?: { [key: string]: any };
  createdAt: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  requirements: { [key: string]: any };
  points: number;
  isActive: boolean;
  createdAt: string;
}

export interface UserAchievement {
  userId: string;
  achievementId: string;
  earnedAt: string;
  earnedData: { [key: string]: any };
}

export interface UserStats {
  totalPoints: number;
  level: number;
  completedProjects: number;
  currentStreak: number;
  totalRecords: number;
  totalPhotos: number;
  totalExperiments: number;
}

export interface AIConversation {
  id: string;
  userId: string;
  projectId?: string;
  contextType: 'general' | 'project_help' | 'tutor' | 'analysis';
  messages: AIMessage[];
  aiModelInfo: { [key: string]: any };
  createdAt: string;
  updatedAt: string;
}

export interface AIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: { [key: string]: any };
}

export interface Schedule {
  id: string;
  projectId: string;
  stepId?: string;
  eventType: 'task' | 'reminder' | 'deadline' | 'observation';
  title: string;
  description: string;
  scheduledAt: string;
  isCompleted: boolean;
  reminderSent: boolean;
  reminderSettings: { [key: string]: any };
  createdAt: string;
  updatedAt: string;
}

export interface Report {
  id: string;
  projectId: string;
  title: string;
  abstract: string;
  introduction: string;
  methodology: string;
  results: string;
  discussion: string;
  conclusion: string;
  structure: { [key: string]: any };
  status: 'draft' | 'in_review' | 'completed';
  completionPercentage: number;
  createdAt: string;
  updatedAt: string;
}

export interface Notification {
  id: string;
  userId: string;
  parentId?: string;
  type: 'reminder' | 'achievement' | 'progress' | 'system';
  title: string;
  content: string;
  data: { [key: string]: any };
  isRead: boolean;
  scheduledAt?: string;
  sentAt?: string;
  createdAt: string;
}

// 認証関連の型定義
export interface User {
  id: string;
  email: string;
  name: string;
  profile?: UserProfile;
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
}

// API レスポンス用の型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// フォーム用の型
export interface CreateProjectRequest {
  themeId: string;
  title?: string;
  description?: string;
  customMaterials?: string[];
  customSteps?: string[];
  targetEndDate?: string;
}

export interface UpdateProjectRequest {
  title?: string;
  description?: string;
  status?: ResearchProject['status'];
  progressPercentage?: number;
  targetEndDate?: string;
  customMaterials?: string[];
  customSteps?: string[];
}

export interface CreateRecordRequest {
  projectId: string;
  stepId?: string;
  recordType: Record['recordType'];
  title: string;
  content: string;
  data?: { [key: string]: any };
  recordDate?: string;
  recordTime?: string;
  tags?: string[];
  weatherInfo?: { [key: string]: any };
  locationInfo?: { [key: string]: any };
}

// ダッシュボード用の集約データ型
export interface DashboardData {
  user: UserProfile;
  stats: UserStats;
  activeProjects: ResearchProject[];
  recentAchievements: Achievement[];
  todaysTasks: Schedule[];
  recentRecords: Record[];
  notifications: Notification[];
}
