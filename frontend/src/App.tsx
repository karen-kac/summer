import { useState } from 'react';
import SplashScreen from './pages/SplashScreen';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import { UserProfile, ResearchTheme, ResearchProject, AuthState, LoginRequest, SignupRequest, User } from './types';
import { generateMockThemes } from './utils/mockThemeGenerator';
import { mockActiveProjects, mockUserStats, mockRecentAchievements, mockPastProjects } from './utils/mockData';
import './styles/Common.css';

type AppState = 'splash' | 'login' | 'signup' | 'dashboard' | 'selector' | 'results' | 'selected';

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

  // プロジェクト状態の管理を追加
  const [activeProjects, setActiveProjects] = useState<ResearchProject[]>(mockActiveProjects);
  const [pastProjects, setPastProjects] = useState<ResearchProject[]>(mockPastProjects);
  const [todaysTasks, setTodaysTasks] = useState([
    { icon: '🌱', task: '植物の成長を測定しよう', urgent: true },
    { icon: '📷', task: '実験結果の写真を撮ろう', urgent: false }
  ]);

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

  const handleContinueProject = (project: ResearchProject) => {
    // 既存のプロジェクトを継続する処理
    console.log('Continue project:', project);
    // TODO: プロジェクト詳細画面に遷移
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
    const newTasks = [
      { icon: '📋', task: `${theme.title}の準備を始めよう`, urgent: true },
      { icon: '🛠️', task: '必要な材料を揃えよう', urgent: false },
      { icon: '📖', task: '研究計画を立てよう', urgent: false }
    ];

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
