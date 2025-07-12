import { UserProfile, ResearchTheme, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse, SignupRequest, LoginRequest, User } from '../types';

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

// ユーザー関連レスポンス型
export interface SignupResponse {
  profile: any;
  settings: any;
  stats: any;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: SignupResponse;
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
   * Bedrock AIを使用してテーマを生成する
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

// ユーザーAPI
class UserApi {
  constructor(private client: ApiClient) {}

  /**
   * 新規会員登録
   */
  async signup(credentials: SignupRequest): Promise<SignupResponse> {
    // バックエンドの期待するフォーマットに変換
    const requestData = {
      email: credentials.email,
      displayName: credentials.name,
      // デフォルト値を設定（実際の実装では適切な値を設定する）
      grade: 'elementary4',
      interests: ['science', 'nature'],
      personality: ['curious', 'patient'],
      strengths: ['observation', 'writing'],
      preferredDuration: '2weeks',
      parentEmail: null
    };

    return this.client.post<SignupResponse>('/user/signup', requestData);
  }

    /**
   * ログイン
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return this.client.post<LoginResponse>('/user/login', credentials);
  }

  /**
   * ユーザープロフィール取得
   */
  async getUserProfile(userId: string): Promise<SignupResponse> {
    return this.client.get<SignupResponse>(`/user/profile/${userId}`);
  }
}

// API インスタンス
const apiClient = new ApiClient();
export const themeApi = new ThemeApi(apiClient);
export const userApi = new UserApi(apiClient);

// デフォルトエクスポート
export default {
  theme: themeApi,
  user: userApi,
};
