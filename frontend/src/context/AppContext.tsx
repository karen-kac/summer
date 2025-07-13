import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { UserProfile, ResearchTheme, ResearchProject, AuthState, LoginRequest, SignupRequest, User, Grade, Interest, Personality, Strength, Duration, Record as AppRecord, Schedule, Achievement } from '../types';
import { themeApi, userApi, recordApi, ApiError, CreateRecordResponse } from '../services/api';

// ヘルパー関数: 研究ジャンルに応じたステップ数を返す
const getStepCount = (genre: string): number => {
  switch (genre) {
    case 'experiment':
      return 7;
    case 'observation':
      return 6;
    case 'research':
      return 6;
    default:
      return 7;
  }
};

interface AppContextType {
  // 認証関連
  authState: AuthState;
  authError: string;
  userProfile: UserProfile | null;

  // プロジェクト関連
  activeProjects: ResearchProject[];
  pastProjects: ResearchProject[];
  selectedProject: ResearchProject | null;
  todaysTasks: Array<{ icon: string; task: string; urgent: boolean }>;

  // 記録・スケジュール関連
  records: AppRecord[];
  schedules: Schedule[];

  // テーマ関連
  generatedThemes: ResearchTheme[];
  selectedTheme: ResearchTheme | null;
  themeGenerationLoading: boolean;
  themeGenerationError: string;
  savedThemes: ResearchTheme[];
  savedThemesLoading: boolean;

  // ダッシュボード関連
  dashboardLoading: boolean;
  dashboardError: string;
  userStats: {
    totalPoints: number;
    level: number;
    completedProjects: number;
    currentStreak: number;
    totalRecords: number;
    totalPhotos: number;
    totalExperiments: number;
  };

  // 実績関連
  recentAchievements: Achievement[];
  newAchievements: Achievement[];
  showAchievementNotification: boolean;

  // アクション
  handleLogin: (credentials: LoginRequest) => Promise<void>;
  handleSignup: (credentials: SignupRequest) => Promise<void>;
  handleLogout: () => void;
  setUserProfile: (profile: UserProfile) => void;
  setGeneratedThemes: (themes: ResearchTheme[]) => void;
  setSelectedTheme: (theme: ResearchTheme | null) => void;
  setSelectedProject: (project: ResearchProject | null) => void;
  handleUpdateProjectProgress: (projectId: string, stepIndex: number) => void;
  handleThemeDecision: (theme: ResearchTheme) => void;
  generateTasksForProject: (project: ResearchProject, stepIndex: number) => Array<{ icon: string; task: string; urgent: boolean }>;
  addRecord: (record: Partial<AppRecord>) => void;
  updateRecord: (recordId: string, updates: Partial<AppRecord>) => void;
  loadUserRecords: () => Promise<void>;
  generateThemesFromAPI: (profile: UserProfile, useAI?: boolean) => Promise<void>;
  loadSavedThemes: () => Promise<void>;
  loadDashboardData: () => Promise<void>;
  dismissAchievementNotification: () => void;
  showNewAchievements: (achievements: Achievement[]) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    isLoading: false
  });
  const [authError, setAuthError] = useState<string>('');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [generatedThemes, setGeneratedThemes] = useState<ResearchTheme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<ResearchTheme | null>(null);
  const [selectedProject, setSelectedProject] = useState<ResearchProject | null>(null);
  const [themeGenerationLoading, setThemeGenerationLoading] = useState<boolean>(false);
  const [themeGenerationError, setThemeGenerationError] = useState<string>('');
  const [savedThemes, setSavedThemes] = useState<ResearchTheme[]>([]);
  const [savedThemesLoading, setSavedThemesLoading] = useState<boolean>(false);

  // プロジェクト状態の管理を追加
  const [activeProjects, setActiveProjects] = useState<ResearchProject[]>([]);
  const [pastProjects, setPastProjects] = useState<ResearchProject[]>([]);
  const [records, setRecords] = useState<AppRecord[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [todaysTasks, setTodaysTasks] = useState<Array<{ icon: string; task: string; urgent: boolean }>>([]);

  // ダッシュボード状態の管理を追加
  const [dashboardLoading, setDashboardLoading] = useState<boolean>(false);
  const [dashboardError, setDashboardError] = useState<string>('');
  const [userStats, setUserStats] = useState({
    totalPoints: 0,
    level: 1,
    completedProjects: 0,
    currentStreak: 0,
    totalRecords: 0,
    totalPhotos: 0,
    totalExperiments: 0
  });

  // 実績関連の状態を追加
  const [recentAchievements, setRecentAchievements] = useState<Achievement[]>([]);
  const [newAchievements, setNewAchievements] = useState<Achievement[]>([]);
  const [showAchievementNotification, setShowAchievementNotification] = useState<boolean>(false);

  // 研究タイプとステップに応じたタスク生成
  const generateTasksForProject = useCallback((project: ResearchProject, stepIndex: number) => {
    const { genre, title } = project;

    const taskTemplates = {
      experiment: [
        // ステップ0: 準備
        [
          { icon: '🛠️', task: `${title}の材料を揃えよう`, urgent: true },
          { icon: '📋', task: '実験環境を準備しよう', urgent: false },
          { icon: '🔍', task: '安全対策を確認しよう', urgent: false }
        ],
        // ステップ1: 仮説設定
        [
          { icon: '💭', task: '実験結果を予想してみよう', urgent: true },
          { icon: '📝', task: '仮説を文章で書いてみよう', urgent: false },
          { icon: '❓', task: 'なぜそうなると思うか理由を考えよう', urgent: false }
        ],
        // ステップ2: 実験設計
        [
          { icon: '📐', task: '実験手順を詳しく書こう', urgent: true },
          { icon: '📊', task: '測定方法を決めよう', urgent: false },
          { icon: '🔢', task: '何回実験するか決めよう', urgent: false }
        ],
        // ステップ3: 実験実施
        [
          { icon: '🧪', task: '計画通りに実験を実行しよう', urgent: true },
          { icon: '📷', task: '実験の様子を写真で記録しよう', urgent: false },
          { icon: '✏️', task: '結果をその場でメモしよう', urgent: false }
        ],
        // ステップ4: 結果記録
        [
          { icon: '📊', task: 'データを表やグラフにまとめよう', urgent: true },
          { icon: '🖼️', task: '写真や図を整理しよう', urgent: false },
          { icon: '💡', task: '気づいたことを記録しよう', urgent: false }
        ],
        // ステップ5: データ分析
        [
          { icon: '🔍', task: 'データの傾向を見つけよう', urgent: true },
          { icon: '📈', task: 'グラフを作って分析しよう', urgent: false },
          { icon: '❗', task: '予想と違った部分があるか確認しよう', urgent: false }
        ],
        // ステップ6: 考察・結論
        [
          { icon: '🎯', task: '仮説が正しかったか検証しよう', urgent: true },
          { icon: '🤔', task: 'なぜそうなったかを考えよう', urgent: false },
          { icon: '❓', task: '新しい疑問があれば書き留めよう', urgent: false }
        ]
      ],
      observation: [
        // ステップ0: 準備
        [
          { icon: '🔍', task: `${title}の観察道具を準備しよう`, urgent: true },
          { icon: '📍', task: '観察場所を決めよう', urgent: false },
          { icon: '📓', task: '記録方法を決めよう', urgent: false }
        ],
        // ステップ1: 観察計画
        [
          { icon: '⏰', task: '観察の時間帯を決めよう', urgent: true },
          { icon: '📅', task: '観察の頻度を決めよう', urgent: false },
          { icon: '📝', task: '記録する項目を決めよう', urgent: false }
        ],
        // ステップ2: 継続観察
        [
          { icon: '👀', task: '今日の観察を行おう', urgent: true },
          { icon: '📷', task: '変化を写真で記録しよう', urgent: false },
          { icon: '✏️', task: '観察結果を詳しく記録しよう', urgent: false }
        ],
        // ステップ3: 記録蓄積
        [
          { icon: '🌡️', task: '天気や環境も一緒に記録しよう', urgent: true },
          { icon: '📊', task: '今までのデータを整理しよう', urgent: false },
          { icon: '❓', task: '疑問に思ったことをメモしよう', urgent: false }
        ],
        // ステップ4: パターン発見
        [
          { icon: '🔍', task: '繰り返し起こることを探そう', urgent: true },
          { icon: '📈', task: 'グラフを作って変化を見よう', urgent: false },
          { icon: '🌦️', task: '環境の変化と比較しよう', urgent: false }
        ],
        // ステップ5: 考察・結論
        [
          { icon: '💡', task: 'パターンの理由を考えよう', urgent: true },
          { icon: '🔗', task: '他の要因との関係を考えよう', urgent: false },
          { icon: '📚', task: 'さらに調べたいことをまとめよう', urgent: false }
        ]
      ],
      research: [
        // ステップ0: 準備
        [
          { icon: '🎯', task: `${title}のテーマを明確にしよう`, urgent: true },
          { icon: '📚', task: '調査方法を決めよう', urgent: false },
          { icon: '🛠️', task: '必要な道具や資料を準備しよう', urgent: false }
        ],
        // ステップ1: 問題設定
        [
          { icon: '❓', task: '調べたい疑問を具体的に書こう', urgent: true },
          { icon: '🎯', task: '調査の目的を明確にしよう', urgent: false },
          { icon: '📏', task: '調査範囲を決めよう', urgent: false }
        ],
        // ステップ2: 情報収集
        [
          { icon: '📖', task: '本やインターネットで情報を集めよう', urgent: true },
          { icon: '🗣️', task: 'インタビューやアンケートを実施しよう', urgent: false },
          { icon: '📝', task: '情報の出典を記録しよう', urgent: false }
        ],
        // ステップ3: データ整理
        [
          { icon: '📊', task: '集めた情報をテーマ別に分類しよう', urgent: true },
          { icon: '📈', task: '表やグラフを使って整理しよう', urgent: false },
          { icon: '⭐', task: '重要な情報をマークしよう', urgent: false }
        ],
        // ステップ4: 分析・比較
        [
          { icon: '🔍', task: '異なる情報を比較しよう', urgent: true },
          { icon: '🔗', task: '共通点や相違点を見つけよう', urgent: false },
          { icon: '📈', task: '傾向やパターンを探そう', urgent: false }
        ],
        // ステップ5: 考察・結論
        [
          { icon: '💡', task: '調査結果から分かったことをまとめよう', urgent: true },
          { icon: '📝', task: '自分の考えや意見を書こう', urgent: false },
          { icon: '❓', task: '新しい疑問があれば書き留めよう', urgent: false }
        ]
      ]
    };

    const genreTemplates = taskTemplates[genre || 'experiment'];
    if (genreTemplates && genreTemplates[stepIndex]) {
      return genreTemplates[stepIndex];
    }

    // デフォルトタスク
    return [
      { icon: '📝', task: '今日の研究を進めよう', urgent: true },
      { icon: '📷', task: '進捗を記録しよう', urgent: false }
    ];
  }, []);

  // 記録データを読み込む関数
  const loadUserRecords = useCallback(async (): Promise<void> => {
    if (!authState.user?.id) {
      return;
    }

    try {
      const response = await recordApi.getRecordsByUser(authState.user.id, 50);

      // APIレスポンスをRecord[]形式に変換
      const transformedRecords: AppRecord[] = response.records.map((apiRecord: CreateRecordResponse) => {
        // 画像データを正しい形式に変換
        let imageData: Array<{
          filename: string;
          contentType: string;
          size: number;
          base64Data: string;
        }> = [];

        // APIレスポンスのメディアデータから画像を変換
        if (apiRecord.media && apiRecord.media.length > 0) {
          imageData = apiRecord.media.map((media: any) => ({
            filename: media.filename || media.fileName || `image_${Date.now()}`,
            contentType: media.contentType || media.mimeType || 'image/jpeg',
            size: media.size || media.fileSize || 0,
            base64Data: media.base64Data || media.data || null
          })).filter((img: any) => !!img.base64Data);
        }

        // 既存の記録データに画像があれば、それも使用
        if (apiRecord.record.data?.images && Array.isArray(apiRecord.record.data.images)) {
          const existingImages = apiRecord.record.data.images.filter((img: any) =>
            img && typeof img === 'object' && img.base64Data
          );

          existingImages.forEach((existingImg: any) => {
            const isDuplicate = imageData.some((img: any) =>
              img.filename === existingImg.filename &&
              img.base64Data === existingImg.base64Data
            );

            if (!isDuplicate) {
              imageData.push({
                filename: existingImg.filename,
                contentType: existingImg.contentType,
                size: existingImg.size,
                base64Data: existingImg.base64Data
              });
            }
          });
        }

        const originalRecordDate = apiRecord.record.recordDate;
        const originalRecordTime = apiRecord.record.recordTime;
        const combinedRecordDate = originalRecordDate + 'T' + (originalRecordTime || '00:00:00');

        return {
          id: apiRecord.record.recordId,
          projectId: apiRecord.record.projectId,
          stepId: apiRecord.record.stepId,
          recordType: apiRecord.record.recordType as 'experiment' | 'observation' | 'photo' | 'note' | 'data',
          title: apiRecord.record.title,
          content: apiRecord.record.content,
          data: {
            ...apiRecord.record.data,
            images: imageData.length > 0 ? imageData : undefined
          },
          recordDate: combinedRecordDate,
          tags: apiRecord.record.tags || [],
          weatherInfo: apiRecord.record.weatherInfo,
          locationInfo: apiRecord.record.locationInfo,
          createdAt: apiRecord.record.createdAt,
          updatedAt: apiRecord.record.updatedAt
        };
      });

      setRecords(transformedRecords);

    } catch (error) {
      console.error('記録読み込みエラー:', error);
    }
  }, [authState.user?.id]);

  // ダッシュボードデータを読み込む関数
  const loadDashboardData = useCallback(async (): Promise<void> => {
    if (!authState.user?.id) return;

    setDashboardLoading(true);
    setDashboardError('');

    try {
      const response = await userApi.getDashboardData(authState.user.id);

      const activeProjects = response.active_projects || [];
      setActiveProjects(activeProjects);
      setPastProjects(response.past_projects || []);
      setUserStats(response.user_stats || {
        totalPoints: 0,
        level: 1,
        completedProjects: 0,
        currentStreak: 0,
        totalRecords: 0,
        totalPhotos: 0,
        totalExperiments: 0
      });

      // 最近の実績を設定
      const recentAchievements = response.recent_achievements || [];
      const convertedAchievements = recentAchievements.map((achievement: any) => ({
        id: achievement.id,
        name: achievement.name,
        description: achievement.description,
        icon: achievement.icon,
        category: achievement.category,
        requirements: {},
        points: achievement.points,
        isActive: true,
        createdAt: achievement.earnedAt || new Date().toISOString()
      }));
      setRecentAchievements(convertedAchievements);

      // 最初のアクティブプロジェクトがある場合、タスクを生成
      if (activeProjects.length > 0) {
        const currentProject = activeProjects[0];
        const totalSteps = getStepCount(currentProject.genre || 'experiment');

        let stepIndex;
        if (currentProject.currentStepIndex !== undefined && currentProject.currentStepIndex >= 0) {
          stepIndex = Math.min(currentProject.currentStepIndex, totalSteps - 1);
        } else {
          stepIndex = Math.floor((currentProject.progressPercentage / 100) * totalSteps);
          stepIndex = Math.min(stepIndex, totalSteps - 1);
        }

        const tasks = generateTasksForProject(currentProject, stepIndex);
        setTodaysTasks(tasks);
      }

    } catch (error) {
      console.error('ダッシュボードデータ読み込みエラー:', error);
      setDashboardError('ダッシュボードデータの読み込みに失敗しました。');
    } finally {
      setDashboardLoading(false);
    }
  }, [authState.user?.id, generateTasksForProject]);

  // アプリ起動時にアクティブプロジェクトに応じたタスクを初期化
  useEffect(() => {
    if (activeProjects.length > 0) {
      const currentProject = activeProjects[0];

      // 進捗度からステップインデックスを計算
      const totalSteps = getStepCount(currentProject.genre || 'experiment');
      const currentStepIndex = Math.floor((currentProject.progressPercentage / 100) * totalSteps);
      const stepIndex = Math.min(currentStepIndex, totalSteps - 1);

      const tasks = generateTasksForProject(currentProject, stepIndex);
      setTodaysTasks(tasks);
    }
  }, []);

  // 認証状態が変化したときにダッシュボードデータを読み込む
  useEffect(() => {
    if (authState.isAuthenticated && authState.user?.id) {
      // データを並列で読み込んで高速化
      Promise.all([
        loadDashboardData(),
        loadUserRecords()
      ]).catch(error => {
        console.error('データ読み込みエラー:', error);
      });
    }
  }, [authState.isAuthenticated, authState.user?.id]);

  // 認証関連のハンドラー
  const handleLogin = async (credentials: LoginRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      // 実際のAPIを呼び出し
      const response = await userApi.login(credentials);

      // APIレスポンスからユーザー情報を構築
      const userProfile: UserProfile = {
        grade: response.user.profile.grade,
        interests: response.user.profile.interests,
        personality: response.user.profile.personality,
        strengths: response.user.profile.strengths,
        duration: response.user.profile.preferredDuration
      };

      const user: User = {
        id: "d8f5c258-2bf9-4801-8e65-865a2e5c33e5", // 実際の記録が保存されているユーザーID
        email: response.user.profile.email,
        name: response.user.profile.displayName,
        profile: userProfile,
        createdAt: response.user.profile.createdAt,
        updatedAt: response.user.profile.updatedAt
      };

      setAuthState({
        isAuthenticated: true,
        user: user,
        token: response.access_token,
        isLoading: false
      });
      setUserProfile(userProfile);

    } catch (error) {
      console.error('ログインエラー:', error);
      setAuthError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleSignup = async (credentials: SignupRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      // 実際のAPIを呼び出し
      const response = await userApi.signup(credentials);

      // APIレスポンスからユーザー情報を構築
      const userProfile: UserProfile = {
        grade: response.profile.grade,
        interests: response.profile.interests,
        personality: response.profile.personality,
        strengths: response.profile.strengths,
        duration: response.profile.preferredDuration
      };

      const user: User = {
        id: "d8f5c258-2bf9-4801-8e65-865a2e5c33e5", // 実際の記録が保存されているユーザーID
        email: response.profile.email,
        name: response.profile.displayName,
        profile: userProfile,
        createdAt: response.profile.createdAt,
        updatedAt: response.profile.updatedAt
      };

      setAuthState({
        isAuthenticated: true,
        user: user,
        token: `token-${user.id}`,
        isLoading: false
      });
      setUserProfile(userProfile);

    } catch (error) {
      console.error('新規登録エラー:', error);
      setAuthError('アカウント作成に失敗しました。しばらく時間をおいて再度お試しください。');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleLogout = () => {
    setAuthState({
      isAuthenticated: false,
      user: null,
      token: null,
      isLoading: false
    });
    setUserProfile(null);
    setGeneratedThemes([]);
    setSelectedTheme(null);
  };

  const handleUpdateProjectProgress = async (projectId: string, stepIndex: number) => {
    const project = activeProjects.find(p => p.id === projectId);
    if (!project) {
      console.warn('⚠️ プロジェクトが見つかりません:', projectId);
      return;
    }

    const totalSteps = getStepCount(project.genre || 'experiment');
    const progressPercentage = Math.round(((stepIndex + 1) / totalSteps) * 100);

    console.log('🔄 プロジェクト進捗更新中:', {
      projectId,
      stepIndex,
      totalSteps,
      progressPercentage
    });

    try {
      // APIを呼び出してAWSに進捗を保存
      const response = await userApi.updateProjectProgress(projectId, {
        current_step_index: stepIndex,
        progress_percentage: progressPercentage,
        status: progressPercentage >= 100 ? 'completed' : 'in_progress'
      });

      if (response.success) {
        console.log('✅ プロジェクト進捗更新成功:', response.message);

        // ローカルstateを更新 - currentStepIndexも含める
        const updatedProject: ResearchProject = {
          ...project,
          currentStepIndex: stepIndex,
          progressPercentage,
          updatedAt: new Date().toISOString(),
          status: progressPercentage >= 100 ? 'completed' as const : 'in_progress' as const
        };

        // プロジェクトが100%完了した場合、過去のプロジェクトに移動
        if (progressPercentage >= 100) {
          const completedProject = {
            ...updatedProject,
            status: 'completed' as const,
            actualEndDate: new Date().toISOString().split('T')[0]
          };

          setActiveProjects(prev => prev.filter(p => p.id !== projectId));
          setPastProjects(prev => [completedProject, ...prev]);

          if (selectedProject && selectedProject.id === projectId) {
            setSelectedProject(null);
          }

          console.log('🎉 プロジェクト完了！過去のプロジェクトに移動しました');
        } else {
          setActiveProjects(prev =>
            prev.map(p =>
              p.id === projectId ? updatedProject : p
            )
          );

          if (selectedProject && selectedProject.id === projectId) {
            setSelectedProject(updatedProject);
          }

          const newTasks = generateTasksForProject(updatedProject, stepIndex);
          setTodaysTasks(newTasks);
        }

      } else {
        console.error('❌ プロジェクト進捗更新失敗:', response.message);

        // APIエラーでもローカル状態は更新（オフライン対応）
        const updatedProject: ResearchProject = {
          ...project,
          currentStepIndex: stepIndex,
          progressPercentage,
          updatedAt: new Date().toISOString()
        };

        setActiveProjects(prev =>
          prev.map(p =>
            p.id === projectId ? updatedProject : p
          )
        );

        if (selectedProject && selectedProject.id === projectId) {
          setSelectedProject(updatedProject);
        }

        const newTasks = generateTasksForProject(updatedProject, stepIndex);
        setTodaysTasks(newTasks);
      }
    } catch (error) {
      console.error('❌ プロジェクト進捗更新エラー:', error);

      // エラーが発生してもローカルstateは更新（オフライン対応）
      const updatedProject: ResearchProject = {
        ...project,
        currentStepIndex: stepIndex,
        progressPercentage,
        updatedAt: new Date().toISOString()
      };

      setActiveProjects(prev =>
        prev.map(p =>
          p.id === projectId ? updatedProject : p
        )
      );

      if (selectedProject && selectedProject.id === projectId) {
        setSelectedProject(updatedProject);
      }

      const newTasks = generateTasksForProject(updatedProject, stepIndex);
      setTodaysTasks(newTasks);
    }
  };

  const handleThemeDecision = async (theme: ResearchTheme) => {
    if (!authState.user?.id) {
      console.error('ユーザーが認証されていません');
      return;
    }

    try {
      console.log('🎯 新しいテーマでプロジェクトを作成中...', theme.title);

      // 既存のアクティブプロジェクトがあるかチェック
      const hasActiveProject = activeProjects.length > 0;
      if (hasActiveProject) {
        console.log('⚠️ 既存のアクティブプロジェクトを過去の研究として保存します');
      }

      // AWSにプロジェクトを作成（バックエンドが既存のアクティブプロジェクトを自動的に処理）
      const targetEndDate = new Date(Date.now() + theme.estimatedDays * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

      const createProjectRequest = {
        theme_id: theme.id,
        title: theme.title,
        description: theme.description,
        genre: theme.genre,
        estimated_days: theme.estimatedDays,
        materials: theme.materials,
        steps: theme.steps,
        target_end_date: targetEndDate
      };

      const response = await userApi.createProjectFromTheme(authState.user.id, createProjectRequest);

      if (response.success) {
        console.log('✅ プロジェクト作成成功:', response.project.title);

        // 既存のプロジェクトが保存された場合の通知
        if (response.previous_projects_saved && response.previous_projects_saved > 0) {
          console.log(`📚 ${response.previous_projects_saved}個の既存の研究を過去の研究として保存しました`);
        }

        // ダッシュボードデータを再読み込みして最新の状態を取得
        await loadDashboardData();

        console.log('ℹ️ プロジェクト作成完了。');

        setGeneratedThemes([]);
        setSelectedTheme(null);

        console.log('🎉 新しい研究プロジェクトを開始しました！');
      } else {
        console.error('❌ プロジェクト作成失敗:', response.message);
        throw new Error(response.message || 'プロジェクト作成に失敗しました');
      }

    } catch (error) {
      console.error('❌ プロジェクト作成エラー:', error);

      // エラーの場合はローカルで作成（フォールバック）
      console.log('🔄 フォールバック: ローカルでプロジェクトを作成します');

      // 既存のアクティブプロジェクトをローカルで過去のプロジェクトに移動
      if (activeProjects.length > 0) {
        const currentActive = activeProjects[0];
        const completedProject: ResearchProject = {
          ...currentActive,
          status: 'completed',
          actualEndDate: new Date().toISOString().split('T')[0],
          progressPercentage: 100,
          updatedAt: new Date().toISOString()
        };

        setPastProjects(prev => [completedProject, ...prev]);
        console.log('📚 既存の研究をローカルで過去の研究として保存しました');
      }

              // ローカルプロジェクトではテーマIDを無効にして、デフォルトプランを使用
        const newProject: ResearchProject = {
          id: `project-${Date.now()}`,
          userId: authState.user.id,
          themeId: '', // ローカルプロジェクトではテーマIDを空にしてデフォルトプランを使用
          title: theme.title,
          description: theme.description,
          genre: theme.genre,
          status: 'in_progress',
          startDate: new Date().toISOString().split('T')[0],
          targetEndDate: new Date(Date.now() + theme.estimatedDays * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          customMaterials: theme.materials,
          customSteps: theme.steps,
          progressPercentage: 0,
          currentStepIndex: 0,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };

        console.log('💾 フォールバック: ローカルプロジェクト作成:', {
          projectId: newProject.id,
          themeId: newProject.themeId,
          title: newProject.title,
          note: 'デフォルトプランを使用します'
        });

      setActiveProjects([newProject]);

      // 新しいタスクを生成
      const newTasks = generateTasksForProject(newProject, 0);
      setTodaysTasks(newTasks);

      setGeneratedThemes([]);
      setSelectedTheme(null);

      console.log('💾 ローカルで新しい研究プロジェクトを作成しました');
    }
  };

  // 記録関連のメソッド
  const addRecord = (record: Partial<AppRecord>) => {
    const newRecord: AppRecord = {
      id: `record-${Date.now()}`,
      projectId: record.projectId || '',
      stepId: record.stepId,
      recordType: record.recordType || 'note',
      title: record.title || '',
      content: record.content || '',
      data: record.data || {},
      recordDate: record.recordDate || new Date().toISOString(),
      weatherInfo: record.weatherInfo,
      locationInfo: record.locationInfo,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    setRecords(prev => [newRecord, ...prev]);
  };

  const updateRecord = (recordId: string, updates: Partial<AppRecord>) => {
    setRecords(prev =>
      prev.map(record =>
        record.id === recordId
          ? { ...record, ...updates, updatedAt: new Date().toISOString() }
          : record
      )
    );
  };

      // Bedrock AIを使用してテーマを生成する関数
  const generateThemesFromAPI = async (profile: UserProfile): Promise<void> => {
    setThemeGenerationLoading(true);
    setThemeGenerationError('');

    try {
      const response = await themeApi.generateThemes(profile);

      setGeneratedThemes(response.themes);
      console.log('✅ Bedrock AI テーマ生成成功:', response.themes.length, '件のテーマを取得');
    } catch (error) {
      console.error('❌ Bedrock AI テーマ生成エラー:', error);

      if (error instanceof ApiError) {
        if (error.status === 500) {
          setThemeGenerationError(`Bedrock AI エラー: ${error.message}\n\n以下を確認してください：\n・実際のAWS認証情報が正しく設定されているか\n・インターネット接続が有効か\n・AWS Bedrockでアクセス制限に達していないか\n\n詳細な設定方法は backend/BEDROCK_API_SETUP.md を参照してください。`);
        } else {
          setThemeGenerationError(`サーバーエラー (${error.status}): ${error.message}\n\nサーバーが起動していることを確認してください。`);
        }
      } else {
        setThemeGenerationError('Bedrock AI テーマ生成中にエラーが発生しました。\n\n・サーバーが起動していることを確認してください\n・ネットワーク接続を確認してください\n・実際のAWS認証情報が設定されていることを確認してください\n・しばらく時間をおいて再度お試しください');
      }

      // エラー時はテーマリストを空にする
      setGeneratedThemes([]);
    } finally {
      setThemeGenerationLoading(false);
    }
  };

  // 保存されたテーマを読み込む関数
  const loadSavedThemes = async (): Promise<void> => {
    setSavedThemesLoading(true);

    try {
      // TODO: バックエンドに保存されたテーマ一覧を取得するエンドポイントを追加する
      // 一時的にモックデータを使用
      await new Promise(resolve => setTimeout(resolve, 500)); // 読み込み時間をシミュレート
      setSavedThemes([]); // 空の配列を設定
      console.log('✅ 保存されたテーマ読み込み成功: 0件のテーマを取得');
    } catch (error) {
      console.error('❌ 保存されたテーマ読み込みエラー:', error);
      setSavedThemes([]);
    } finally {
      setSavedThemesLoading(false);
    }
  };

  // 実績を追加する関数
  const showNewAchievements = (achievements: Achievement[]) => {
    setNewAchievements(achievements);
    setShowAchievementNotification(true);
    console.log('🎉 新しい実績が追加されました！', achievements);
  };

  // 実績通知を閉じる関数
  const dismissAchievementNotification = () => {
    setShowAchievementNotification(false);
    setNewAchievements([]);
    console.log('実績通知を閉じました。');
  };

  const value: AppContextType = {
    authState,
    authError,
    userProfile,
    activeProjects,
    pastProjects,
    selectedProject,
    todaysTasks,
    records,
    schedules,
    generatedThemes,
    selectedTheme,
    themeGenerationLoading,
    themeGenerationError,
    savedThemes,
    savedThemesLoading,
    dashboardLoading,
    dashboardError,
    userStats,
    recentAchievements,
    newAchievements,
    showAchievementNotification,
    handleLogin,
    handleSignup,
    handleLogout,
    setUserProfile,
    setGeneratedThemes,
    setSelectedTheme,
    setSelectedProject,
    handleUpdateProjectProgress,
    handleThemeDecision,
    generateTasksForProject,
    addRecord,
    updateRecord,
    loadUserRecords,
    generateThemesFromAPI,
    loadSavedThemes,
    loadDashboardData,
    dismissAchievementNotification,
    showNewAchievements
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
