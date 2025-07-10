import { UserProfile, ResearchTheme } from '../types';

// APIの基本設定
const API_BASE_URL = 'http://127.0.0.1:8000';

// レスポンス型定義
export interface ThemeListResponse {
  themes: ResearchTheme[];
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
   * モックデータを使用してテーマを生成する
   */
  async generateThemes(profile: UserProfile): Promise<ThemeListResponse> {
    return this.client.post<ThemeListResponse>('/theme/generate', profile);
  }

  /**
   * 実際のGemini APIを使用してテーマを生成する（テスト用）
   */
  async generateThemesWithAI(profile: UserProfile): Promise<ThemeListResponse> {
    return this.client.post<ThemeListResponse>('/theme/test-prompt', profile);
  }
}

// API インスタンス
const apiClient = new ApiClient();
export const themeApi = new ThemeApi(apiClient);

// デフォルトエクスポート
export default {
  theme: themeApi,
};
