import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, ResearchTheme, ResearchProject, AuthState, LoginRequest, SignupRequest, User, Grade, Interest, Personality, Strength, Duration, Record, Schedule } from '../types';
import { generateMockThemes } from '../utils/mockThemeGenerator';
import { mockActiveProjects, mockUserStats, mockRecentAchievements, mockPastProjects, mockRecords, mockSchedules } from '../utils/mockData';

// ヘルパー関数: 研究ジャンルに応じたステップ数を返す
const getStepCount = (genre: string): number => {
  switch (genre) {
    case 'experiment': return 7;
    case 'observation': return 6;
    case 'research': return 6;
    default: return 7;
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
  records: Record[];
  schedules: Schedule[];

  // テーマ関連
  generatedThemes: ResearchTheme[];
  selectedTheme: ResearchTheme | null;

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
  addRecord: (record: Partial<Record>) => void;
  updateRecord: (recordId: string, updates: Partial<Record>) => void;
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

  // プロジェクト状態の管理を追加
  const [activeProjects, setActiveProjects] = useState<ResearchProject[]>(mockActiveProjects);
  const [pastProjects, setPastProjects] = useState<ResearchProject[]>(mockPastProjects);
  const [records, setRecords] = useState<Record[]>(mockRecords);
  const [schedules, setSchedules] = useState<Schedule[]>(mockSchedules);
  const [todaysTasks, setTodaysTasks] = useState([
    { icon: '🌱', task: '植物の成長を測定しよう', urgent: true },
    { icon: '📷', task: '実験結果の写真を撮ろう', urgent: false }
  ]);

  // 研究タイプとステップに応じたタスク生成
  const generateTasksForProject = (project: ResearchProject, stepIndex: number) => {
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
  };

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

  // 認証関連のハンドラー
  const handleLogin = async (credentials: LoginRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      console.log('Logging in with:', credentials);

      // モックレスポンス（実際の実装では、APIからのレスポンスを使用）
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockUser: User = {
        id: 'user-123',
        email: credentials.email,
        name: 'テストユーザー',
        profile: {
          grade: 'elementary4',
          interests: ['science', 'nature'],
          personality: ['curious', 'patient'],
          strengths: ['observation', 'writing'],
          duration: '2weeks'
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      setAuthState({
        isAuthenticated: true,
        user: mockUser,
        token: 'mock-token-123',
        isLoading: false
      });
      setUserProfile(mockUser.profile || null);
    } catch (error) {
      setAuthError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleSignup = async (credentials: SignupRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      console.log('Signing up with:', credentials);

      // モックレスポンス
      await new Promise(resolve => setTimeout(resolve, 1500));

      const mockProfile: UserProfile = {
        grade: 'elementary4' as Grade,
        interests: ['science', 'nature'] as Interest[],
        personality: ['curious', 'patient'] as Personality[],
        strengths: ['observation', 'writing'] as Strength[],
        duration: '2weeks' as Duration
      };

      const mockUser: User = {
        id: 'user-' + Date.now(),
        email: credentials.email,
        name: credentials.name,
        profile: mockProfile,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      setAuthState({
        isAuthenticated: true,
        user: mockUser,
        token: 'mock-token-' + Date.now(),
        isLoading: false
      });
      setUserProfile(mockProfile);
    } catch (error) {
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

  const handleUpdateProjectProgress = (projectId: string, stepIndex: number) => {
    const project = activeProjects.find(p => p.id === projectId);
    if (!project) return;

    const totalSteps = getStepCount(project.genre || 'experiment');
    const progressPercentage = Math.round(((stepIndex + 1) / totalSteps) * 100);

    setActiveProjects(prev =>
      prev.map(p =>
        p.id === projectId
          ? { ...p, progressPercentage, updatedAt: new Date().toISOString() }
          : p
      )
    );

    if (selectedProject && selectedProject.id === projectId) {
      setSelectedProject(prev =>
        prev ? { ...prev, progressPercentage, updatedAt: new Date().toISOString() } : null
      );
    }

    const newTasks = generateTasksForProject(project, stepIndex);
    setTodaysTasks(newTasks);
  };

  const handleThemeDecision = (theme: ResearchTheme) => {
    // 既存のアクティブプロジェクトを過去のプロジェクトに移動
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
    }

    // 新しいプロジェクトを作成
    const newProject: ResearchProject = {
      id: `project-${Date.now()}`,
      userId: authState.user?.id || 'user-1',
      themeId: theme.id,
      title: theme.title,
      description: theme.description,
      genre: theme.genre,
      status: 'in_progress',
      startDate: new Date().toISOString().split('T')[0],
      targetEndDate: new Date(Date.now() + theme.estimatedDays * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      customMaterials: theme.materials,
      customSteps: theme.steps,
      progressPercentage: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    setActiveProjects([newProject]);

    // 新しいタスクを生成
    const newTasks = generateTasksForProject(newProject, 0);
    setTodaysTasks(newTasks);

    setGeneratedThemes([]);
    setSelectedTheme(null);
  };

  // 記録関連のメソッド
  const addRecord = (record: Partial<Record>) => {
    const newRecord: Record = {
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

  const updateRecord = (recordId: string, updates: Partial<Record>) => {
    setRecords(prev =>
      prev.map(record =>
        record.id === recordId
          ? { ...record, ...updates, updatedAt: new Date().toISOString() }
          : record
      )
    );
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
    updateRecord
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
