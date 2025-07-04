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

export interface ResearchProject {
  id: string;
  userId: string;
  themeId: string;
  title: string;
  description: string;
  status: 'planning' | 'in_progress' | 'completed' | 'paused';
  startDate: string;
  targetEndDate: string;
  actualEndDate?: string;
  customMaterials: string[];
  customSteps: string[];
  progressPercentage: number;
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