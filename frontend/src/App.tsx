import { useState, useEffect } from 'react';
import SplashScreen from './pages/SplashScreen';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import ActiveProjectPage from './pages/ActiveProjectPage';
import { UserProfile, ResearchTheme, ResearchProject, AuthState, LoginRequest, SignupRequest, User } from './types';
import { generateMockThemes } from './utils/mockThemeGenerator';
import { mockActiveProjects, mockUserStats, mockRecentAchievements, mockPastProjects } from './utils/mockData';
import './styles/Common.css';

type AppState = 'splash' | 'login' | 'signup' | 'dashboard' | 'selector' | 'results' | 'selected' | 'active-project';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('splash');
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
      const getStepCount = (genre: string) => {
        switch (genre) {
          case 'experiment': return 7;
          case 'observation': return 6;
          case 'research': return 6;
          default: return 7;
        }
      };

      const totalSteps = getStepCount(currentProject.genre || 'experiment');
      const currentStepIndex = Math.floor((currentProject.progressPercentage / 100) * totalSteps);
      const stepIndex = Math.min(currentStepIndex, totalSteps - 1);

      const tasks = generateTasksForProject(currentProject, stepIndex);
      setTodaysTasks(tasks);
    }
  }, []);  // 空の依存配列で初回のみ実行

  const handleSplashComplete = () => {
    // 認証状態をチェック（実際の実装では、保存されたトークンなどをチェック）
    if (authState.isAuthenticated) {
      setCurrentState('dashboard');
    } else {
      setCurrentState('login');
    }
  };

  // 認証関連のハンドラー
  const handleLogin = async (credentials: LoginRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      console.log('Logging in with:', credentials);

      // モックレスポンス（実際の実装では、APIからのレスポンスを使用）
      await new Promise(resolve => setTimeout(resolve, 1000)); // シミュレート

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
      setCurrentState('dashboard');
    } catch (error) {
      setAuthError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleSignup = async (credentials: SignupRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    setAuthError('');

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      console.log('Signing up with:', credentials);

      // モックレスポンス（実際の実装では、APIからのレスポンスを使用）
      await new Promise(resolve => setTimeout(resolve, 1500)); // シミュレート

      const mockUser: User = {
        id: 'user-' + Date.now(),
        email: credentials.email,
        name: credentials.name,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      setAuthState({
        isAuthenticated: true,
        user: mockUser,
        token: 'mock-token-' + Date.now(),
        isLoading: false
      });
      setCurrentState('dashboard');
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
    setCurrentState('login');
  };

  const handleSwitchToSignup = () => {
    setAuthError('');
    setCurrentState('signup');
  };

  const handleSwitchToLogin = () => {
    setAuthError('');
    setCurrentState('login');
  };

  const handleStartNewResearch = () => {
    setCurrentState('selector');
  };

  const handleProfileComplete = (profile: UserProfile) => {
    setUserProfile(profile);
    const themes = generateMockThemes(profile);
    setGeneratedThemes(themes);
    setCurrentState('results');
  };

  const handleThemeSelect = (theme: ResearchTheme) => {
    setSelectedTheme(theme);
    setCurrentState('selected');
  };

  const handleBackToDashboard = () => {
    setCurrentState('dashboard');
    setGeneratedThemes([]);
    setSelectedTheme(null);
  };

  const handleBackToSelector = () => {
    setCurrentState('selector');
    setSelectedTheme(null);
  };

  const handleBackToResults = () => {
    setCurrentState('results');
    setSelectedTheme(null);
  };

  const handleBackToActiveProject = () => {
    setCurrentState('dashboard');
    setSelectedProject(null);
  };

  const handleUpdateProjectProgress = (projectId: string, stepIndex: number) => {
    // プロジェクトを取得
    const project = activeProjects.find(p => p.id === projectId);
    if (!project) return;

    // ステップ数を取得（研究タイプによって異なる）
    const getStepCount = (genre: string) => {
      switch (genre) {
        case 'experiment': return 7;
        case 'observation': return 6;
        case 'research': return 6;
        default: return 7;
      }
    };

    const totalSteps = getStepCount(project.genre || 'experiment');
    const progressPercentage = Math.round(((stepIndex + 1) / totalSteps) * 100);

    setActiveProjects(prev =>
      prev.map(p =>
        p.id === projectId
          ? { ...p, progressPercentage, updatedAt: new Date().toISOString() }
          : p
      )
    );

    // selectedProjectも更新
    if (selectedProject && selectedProject.id === projectId) {
      setSelectedProject(prev =>
        prev ? { ...prev, progressPercentage, updatedAt: new Date().toISOString() } : null
      );
    }

    // 今日のタスクを更新
    const newTasks = generateTasksForProject(project, stepIndex);
    setTodaysTasks(newTasks);
  };

  const handleContinueProject = (project: ResearchProject) => {
    setSelectedProject(project);
    setCurrentState('active-project');
  };

  const handleViewAllProjects = () => {
    // すべてのプロジェクトを表示する処理
    console.log('View all projects');
    // TODO: プロジェクト一覧画面に遷移
  };

  const handleOpenAITutor = () => {
    // AIチューターを開く処理
    console.log('Open AI tutor');
    // TODO: AIチューター画面に遷移
  };

  const handleViewRecords = () => {
    // 記録一覧を表示する処理
    console.log('View records');
    // TODO: 記録一覧画面に遷移
  };

  const handleViewLearning = () => {
    // 学習コンテンツを表示する処理
    console.log('View learning content');
    // TODO: 学習コンテンツ画面に遷移
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

    // 新しいタスクを生成（ステップ0の準備段階）
    const newTasks = generateTasksForProject(newProject, 0);
    setTodaysTasks(newTasks);

    // ダッシュボードに遷移
    setCurrentState('dashboard');
    setGeneratedThemes([]);
    setSelectedTheme(null);
  };

  return (
    <div className="app">
      {currentState === 'splash' && (
        <SplashScreen onComplete={handleSplashComplete} />
      )}

            {currentState === 'login' && (
        <LoginPage
          onLogin={handleLogin}
          onSwitchToSignup={handleSwitchToSignup}
          isLoading={authState.isLoading}
          error={authError}
        />
      )}

      {currentState === 'signup' && (
        <SignupPage
          onSignup={handleSignup}
          onSwitchToLogin={handleSwitchToLogin}
          isLoading={authState.isLoading}
          error={authError}
        />
      )}

      {currentState !== 'splash' && currentState !== 'login' && currentState !== 'signup' && (
        <>
          <header className="header">
            <div className="header-content">
              <div className="header-text">
                <h1>夏休み自由研究AI</h1>
                <p>AIがあなたにぴったりの自由研究テーマを提案します！（小学生〜中学生対象）</p>
              </div>
              {authState.isAuthenticated && (
                <div className="header-actions">
                  <span className="user-name">
                    {authState.user?.name}さん
                  </span>
                  <button
                    className="logout-button"
                    onClick={handleLogout}
                    title="ログアウト"
                  >
                    ログアウト
                  </button>
                </div>
              )}
            </div>
          </header>

          {currentState === 'dashboard' && (
        <DashboardPage
          userProfile={userProfile}
          activeProjects={activeProjects}
          pastProjects={pastProjects}
          userStats={mockUserStats}
          recentAchievements={mockRecentAchievements}
          todaysTasks={todaysTasks}
          onStartNewResearch={handleStartNewResearch}
          onContinueProject={handleContinueProject}
          onViewAllProjects={handleViewAllProjects}
          onOpenAITutor={handleOpenAITutor}
          onViewRecords={handleViewRecords}
          onViewLearning={handleViewLearning}
        />
      )}

      {currentState === 'selector' && (
        <ThemeSelectorPage onProfileComplete={handleProfileComplete} onBack={handleBackToDashboard} />
      )}

      {currentState === 'results' && (
        <ThemeResultsPage
          themes={generatedThemes}
          onThemeSelect={handleThemeSelect}
          onBackToSelector={handleBackToSelector}
        />
      )}

      {currentState === 'selected' && selectedTheme && (
        <SelectedThemePage
          theme={selectedTheme}
          onBackToResults={handleBackToResults}
          onBackToSelector={handleBackToSelector}
          onThemeDecision={handleThemeDecision}
        />
      )}

      {currentState === 'active-project' && selectedProject && (
        <ActiveProjectPage
          project={selectedProject}
          onBack={handleBackToActiveProject}
          onUpdateProgress={handleUpdateProjectProgress}
        />
      )}

          {/* フローティングダッシュボードボタン（ダッシュボード以外の認証済み画面で表示） */}
          {currentState !== 'dashboard' && authState.isAuthenticated && (
            <button
              className="floating-dashboard-btn"
              onClick={handleBackToDashboard}
              title="ダッシュボードに戻る"
            >
              🏠
            </button>
          )}
        </>
      )}
    </div>
  );
}

export default App;
