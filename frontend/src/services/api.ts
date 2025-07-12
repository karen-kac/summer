import { UserProfile, ResearchTheme, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse, SignupRequest, LoginRequest, User, CreateRecordRequest, Record } from '../types';

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

export interface DashboardDataResponse {
  active_projects: any[];
  past_projects: any[];
  user_stats: {
    totalPoints: number;
    level: number;
    completedProjects: number;
    currentStreak: number;
    totalRecords: number;
    totalPhotos: number;
    totalExperiments: number;
  };
  recent_achievements: Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    category: string;
    points: number;
    earnedAt?: string;
  }>;
}

export interface CreateProjectRequest {
  theme_id: string;
  title: string;
  description: string;
  genre: string;
  estimated_days: number;
  materials: string[];
  steps: string[];
  target_end_date: string;
}

export interface CreateProjectResponse {
  success: boolean;
  project: any;
  message: string;
  previous_projects_saved?: number;
}

// プロジェクト進捗更新用の型定義
export interface UpdateProjectProgressRequest {
  current_step_index: number;
  progress_percentage: number;
  status?: string;
}

export interface UpdateProjectProgressResponse {
  success: boolean;
  message: string;
  current_step_index: number;
  progress_percentage: number;
}

// 記録関連レスポンス型
export interface CreateRecordResponse {
  record: {
    recordId: string;
    projectId: string;
    userId: string;
    stepId?: string;
    recordType: string;
    title: string;
    content: string;
    recordDate: string;
    recordTime: string;
    data: { [key: string]: any };
    tags: string[];
    weatherInfo?: { [key: string]: any };
    locationInfo?: { [key: string]: any };
    mediaIds: string[];
    aiAnalysis?: { [key: string]: any };
    isPublic: boolean;
    parentVisible: boolean;
    createdAt: string;
    updatedAt: string;
  };
  media: any[];
  aiAnalysis?: any;
}

export interface RecordListResponse {
  records: CreateRecordResponse[];
  total: number;
  hasMore: boolean;
  nextToken?: string;
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

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
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
  async saveTheme(theme: ResearchTheme, userProfile?: UserProfile, userId?: string): Promise<SaveThemeResponse> {
    const request: SaveThemeRequest = {
      theme,
      user_profile: userProfile
    };

    // ユーザーIDがある場合はクエリパラメータとして追加
    const endpoint = userId ? `/theme/save?user_id=${userId}` : '/theme/save';

    return this.client.post<SaveThemeResponse>(endpoint, request);
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

// 記録API
class RecordApi {
  constructor(private client: ApiClient) {}

  /**
   * 新しい記録を作成する
   */
  async createRecord(userId: string, request: CreateRecordRequest): Promise<CreateRecordResponse> {
    // リクエストデータのサイズを計算
    const requestString = JSON.stringify(request);
    const requestSizeKB = Math.round(requestString.length / 1024);

    console.log('🌐 API記録作成リクエスト:', {
      userId: userId,
      endpoint: `/record/create?user_id=${userId}`,
      requestSizeKB: requestSizeKB,
      requestSizeMB: Math.round(requestSizeKB / 1024 * 100) / 100,
      requestData: {
        ...request,
        data: {
          ...request.data,
          images: request.data?.images?.map((img: any, i: number) => ({
            index: i,
            filename: img.filename,
            contentType: img.contentType,
            size: img.size,
            hasBase64: !!img.base64Data,
            base64Length: img.base64Data?.length || 0,
            base64SizeKB: Math.round((img.base64Data?.length || 0) / 1024)
          })) || []
        }
      }
    });

    // 大きすぎる場合は警告
    if (requestSizeKB > 5000) { // 5MB以上
      console.warn('⚠️ リクエストサイズが大きすぎます:', {
        sizeKB: requestSizeKB,
        sizeMB: Math.round(requestSizeKB / 1024 * 100) / 100,
        recommendation: '画像サイズを小さくしてください'
      });
    }

        try {
      const response = await this.client.post<CreateRecordResponse>(`/record/create?user_id=${userId}`, request);

      console.log('🌐 API記録作成レスポンス:', {
        success: !!response,
        recordId: response.record?.recordId,
        mediaCount: response.media?.length || 0,
        hasMedia: !!response.media && response.media.length > 0,
        response: response
      });

      return response;
    } catch (error) {
      console.error('❌ API記録作成エラー:', {
        error: error,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
        errorType: typeof error,
        isApiError: error instanceof ApiError,
        apiErrorStatus: error instanceof ApiError ? error.status : undefined,
        apiErrorData: error instanceof ApiError ? error.data : undefined
      });

      // エラーを再投げ
      throw error;
    }
  }

  /**
   * プロジェクトの記録一覧を取得する
   */
  async getRecordsByProject(projectId: string, limit?: number, nextToken?: string): Promise<RecordListResponse> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (nextToken) params.append('last_evaluated_key', nextToken);

    const queryString = params.toString();
    const endpoint = `/record/project/${projectId}${queryString ? `?${queryString}` : ''}`;

    return this.client.get<RecordListResponse>(endpoint);
  }

  /**
   * ユーザーの記録一覧を取得する
   */
  async getRecordsByUser(userId: string, limit?: number, nextToken?: string): Promise<RecordListResponse> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (nextToken) params.append('last_evaluated_key', nextToken);

    const queryString = params.toString();
    const endpoint = `/record/user/${userId}${queryString ? `?${queryString}` : ''}`;

    console.log('🌐 API記録取得リクエスト:', {
      userId: userId,
      endpoint: endpoint,
      limit: limit,
      nextToken: nextToken
    });

    const response = await this.client.get<RecordListResponse>(endpoint);

    console.log('🌐 API記録取得レスポンス:', {
      recordsCount: response.records?.length || 0,
      hasMore: response.hasMore,
      total: response.total,
      recordsWithMedia: response.records?.filter((r: any) => r.media && r.media.length > 0).length || 0,
      mediaDetails: response.records?.map((record: any, i: number) => ({
        index: i,
        recordId: record.record?.recordId,
        title: record.record?.title,
        recordType: record.record?.recordType,
        hasMedia: !!record.media && record.media.length > 0,
        mediaCount: record.media?.length || 0
      })) || []
    });

    return response;
  }

  /**
   * 日付の記録一覧を取得する
   */
  async getRecordsByDate(recordDate: string, limit?: number, nextToken?: string): Promise<RecordListResponse> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (nextToken) params.append('last_evaluated_key', nextToken);

    const queryString = params.toString();
    const endpoint = `/record/date/${recordDate}${queryString ? `?${queryString}` : ''}`;

    return this.client.get<RecordListResponse>(endpoint);
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

  /**
   * ユーザーダッシュボードデータを取得する
   */
  async getDashboardData(userId: string): Promise<DashboardDataResponse> {
    return this.client.get<DashboardDataResponse>(`/user/dashboard/${userId}`);
  }

  /**
   * テーマからプロジェクトを作成する
   */
  async createProjectFromTheme(userId: string, request: CreateProjectRequest): Promise<CreateProjectResponse> {
    return this.client.post<CreateProjectResponse>(`/user/projects?user_id=${userId}`, request);
  }

  /**
   * プロジェクトの進捗を更新する
   */
  async updateProjectProgress(projectId: string, request: UpdateProjectProgressRequest): Promise<UpdateProjectProgressResponse> {
    return this.client.put<UpdateProjectProgressResponse>(`/user/projects/${projectId}/progress`, request);
  }
}

// API インスタンス
const apiClient = new ApiClient();
export const themeApi = new ThemeApi(apiClient);
export const userApi = new UserApi(apiClient);
export const recordApi = new RecordApi(apiClient);

// デフォルトエクスポート
export default {
  theme: themeApi,
  user: userApi,
  record: recordApi,
};
