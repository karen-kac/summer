import { UserProfile, ResearchTheme, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse, ResearchProject, Achievement } from '../types';

// APIの基本設定
const API_BASE_URL = 'http://127.0.0.1:8000';

// レスポンス型定義
export interface ThemeListResponse {
  themes: ResearchTheme[];
}

export interface SaveThemeResponse {
  success: boolean;
  message: string;
  saved_theme_id: string;
}

export interface SaveThemeRequest {
  theme: ResearchTheme;
  user_profile?: UserProfile;
}

export interface DashboardResponse {
  activeProjects: ResearchProject[];
  pastProjects: ResearchProject[];
  recentAchievements: Achievement[];
}

// APIエラー型
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// API基本クラス
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new ApiError(
          `HTTP Error: ${response.status}`,
          response.status,
          errorData
        );
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('ネットワークエラーが発生しました', 0, error);
    }
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
    });
  }
}

// テーマAPI
class ThemeApi {
  constructor(private client: ApiClient) {}

  /**
   * Gemini AIを使用してテーマを生成する
   */
  async generateThemes(profile: UserProfile): Promise<ThemeListResponse> {
    return this.client.post<ThemeListResponse>('/theme/generate', profile);
  }

  /**
   * 選択されたテーマを保存する
   */
  async saveTheme(theme: ResearchTheme, userProfile?: UserProfile): Promise<SaveThemeResponse> {
    const request: SaveThemeRequest = {
      theme,
      user_profile: userProfile
    };
    return this.client.post<SaveThemeResponse>('/theme/save', request);
  }

  /**
   * 保存されたテーマを取得する
   */
  async getSavedTheme(themeId: string): Promise<GetSavedThemeResponse> {
    return this.client.get<GetSavedThemeResponse>(`/theme/saved/${themeId}`);
  }

  /**
   * 保存された研究計画を取得する
   */
  async getResearchPlan(themeId: string): Promise<GetResearchPlanResponse> {
    return this.client.get<GetResearchPlanResponse>(`/theme/plan/${themeId}`);
  }

  /**
   * 保存されたテーマを基に研究計画を生成する（初回のみ）
   */
  async generateResearchPlan(themeId: string): Promise<GeneratePlanResponse> {
    const request: GeneratePlanRequest = {
      theme_id: themeId
    };
    return this.client.post<GeneratePlanResponse>('/theme/generate-plan', request);
  }
}

// API インスタンス
const apiClient = new ApiClient();
export const themeApi = new ThemeApi(apiClient);

// ダッシュボードAPI
class DashboardApi {
  constructor(private client: ApiClient) {}

  async getDashboardData(): Promise<DashboardResponse> {
    return this.client.get<DashboardResponse>('/dashboard/get');
  }
}

export const dashboardApi = new DashboardApi(apiClient);

// デフォルトエクスポート
export default {
  theme: themeApi,
  dashboard: dashboardApi,
};
