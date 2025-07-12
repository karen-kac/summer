import {
  UserProfile,
  ResearchTheme,
  GeneratePlanRequest,
  GeneratePlanResponse,
  GetSavedThemeResponse,
  GetResearchPlanResponse,
  LineConnectionStatus,
  LineConnectRequest,
  ProgressNotificationRequest
} from '../types';

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

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
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

// LINE API
class LineApi {
  constructor(private client: ApiClient) {}

  /**
   * ユーザーのLINE連携状態を取得
   */
  async getConnectionStatus(userId: string): Promise<LineConnectionStatus> {
    return this.client.get<LineConnectionStatus>(`/line/status/${userId}`);
  }

  /**
   * LINEアカウントを連携
   */
  async connectAccount(request: LineConnectRequest): Promise<{ status: string; connection: any }> {
    return this.client.post('/line/connect', request);
  }

  /**
   * LINEアカウント連携を解除
   */
  async disconnectAccount(userId: string): Promise<{ status: string; message: string }> {
    return this.client.delete(`/line/disconnect/${userId}`);
  }

  /**
   * 研究進捗通知を送信
   */
  async sendProgressNotification(request: ProgressNotificationRequest): Promise<{ status: string; message: string }> {
    return this.client.post('/line/send-progress-notification', request);
  }

  /**
   * 日次リマインダーを送信
   */
  async sendDailyReminder(userId: string, researchTitle: string): Promise<{ status: string; message: string }> {
    return this.client.post('/line/send-daily-reminder', {
      user_id: userId,
      research_title: researchTitle
    });
  }

  /**
   * LINE API の健康状態をチェック
   */
  async healthCheck(): Promise<{ status: string; line_api_configured: boolean; message: string }> {
    return this.client.get('/line/health');
  }
}

// API インスタンス
const apiClient = new ApiClient();
export const themeApi = new ThemeApi(apiClient);
export const lineApi = new LineApi(apiClient);

// デフォルトエクスポート
export default {
  theme: themeApi,
  line: lineApi,
};
