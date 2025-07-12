import React, { useEffect } from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
  useNavigate,
  useParams,
  useLocation
} from 'react-router-dom';
import { AppProvider, useApp } from './context/AppContext';
import PrivateRoute from './components/PrivateRoute';
import AppLayout from './components/AppLayout';

// Pages
import SplashScreen from './pages/SplashScreen';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import ActiveProjectPage from './pages/ActiveProjectPage';
import RecordCalendarPage from './pages/RecordCalendarPage';
import { ChatPage } from './pages/ChatPage';

import type { Record, UserProfile, ResearchProject, ResearchTheme, UserStats, Achievement } from './types';
import './styles/Common.css';

// デフォルトデータ
const defaultUserStats: UserStats = {
  totalPoints: 0,
  level: 1,
  completedProjects: 0,
  currentStreak: 0,
  totalRecords: 0,
  totalPhotos: 0,
  totalExperiments: 0
};

const defaultRecentAchievements: Achievement[] = [];

// ページコンポーネントをラップしてReact Router対応にする
const SplashScreenWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { authState } = useApp();

  const handleSplashComplete = () => {
    if (authState.isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return <SplashScreen onComplete={handleSplashComplete} />;
};

const LoginPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { handleLogin, authState, authError } = useApp();

  const handleLoginSubmit = async (credentials: any) => {
    await handleLogin(credentials);
    // 認証成功時は元のページまたはダッシュボードにリダイレクト
    const from = location.state?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  };

  const handleSwitchToSignup = () => {
    navigate('/signup');
  };

  return (
    <LoginPage
      onLogin={handleLoginSubmit}
      onSwitchToSignup={handleSwitchToSignup}
      isLoading={authState.isLoading}
      error={authError}
    />
  );
};

const SignupPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { handleSignup, authState, authError } = useApp();

  const handleSignupSubmit = async (credentials: any) => {
    await handleSignup(credentials);
    navigate('/dashboard');
  };

  const handleSwitchToLogin = () => {
    navigate('/login');
  };

  return (
    <SignupPage
      onSignup={handleSignupSubmit}
      onSwitchToLogin={handleSwitchToLogin}
      isLoading={authState.isLoading}
      error={authError}
    />
  );
};

const DashboardPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const {
    userProfile,
    activeProjects,
    pastProjects,
    todaysTasks,
    savedThemes,
    savedThemesLoading,
    setSelectedProject,
    setSelectedTheme
  } = useApp();

  const handleStartNewResearch = () => {
    navigate('/selector');
  };

  const handleContinueProject = (project: any) => {
    setSelectedProject(project);
    navigate(`/project/${project.id}`);
  };

  const handleViewAllProjects = () => {
    console.log('View all projects');
    // TODO: プロジェクト一覧画面に遷移
  };

  const handleOpenAITutor = () => {
    navigate('/chat');
  };

  const handleViewRecords = () => {
    navigate('/records');
  };

  const handleViewLearning = () => {
    console.log('View learning content');
    // TODO: 学習コンテンツ画面に遷移
  };

  const handleSelectSavedTheme = (theme: ResearchTheme) => {
    // 保存済みテーマを選択して、ActiveProjectPageに遷移
    setSelectedTheme(theme);
    navigate(`/theme/${theme.id}`);
  };

  return (
    <DashboardPage
      userProfile={userProfile}
      activeProjects={activeProjects}
      pastProjects={pastProjects}
      userStats={defaultUserStats}
      recentAchievements={defaultRecentAchievements}
      todaysTasks={todaysTasks}
      savedThemes={savedThemes}
      savedThemesLoading={savedThemesLoading}
      onStartNewResearch={handleStartNewResearch}
      onContinueProject={handleContinueProject}
      onViewAllProjects={handleViewAllProjects}
      onOpenAITutor={handleOpenAITutor}
      onViewRecords={handleViewRecords}
      onViewLearning={handleViewLearning}
      onSelectSavedTheme={handleSelectSavedTheme}
    />
  );
};

const ThemeSelectorPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { setUserProfile, generateThemesFromAPI, themeGenerationLoading, themeGenerationError } = useApp();

  const handleProfileComplete = async (profile: any) => {
    setUserProfile(profile);

    try {
      await generateThemesFromAPI(profile); // Gemini AIを使用

      // APIが成功し、エラーがない場合は結果ページに遷移
      if (!themeGenerationError) {
        navigate('/results');
      }
    } catch (error) {
      console.error('テーマ生成エラー:', error);
      // エラーの場合は遷移しない（ThemeSelectorPageでエラーメッセージを表示）
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <ThemeSelectorPage
      onProfileComplete={handleProfileComplete}
      onBack={handleBack}
      isLoading={themeGenerationLoading}
      error={themeGenerationError}
    />
  );
};

const ThemeResultsPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { generatedThemes, setSelectedTheme } = useApp();

  const handleThemeSelect = (theme: any) => {
    setSelectedTheme(theme);
    navigate(`/theme/${theme.id}`);
  };

  const handleBackToSelector = () => {
    navigate('/selector');
  };

  return (
    <ThemeResultsPage
      themes={generatedThemes}
      onThemeSelect={handleThemeSelect}
      onBackToSelector={handleBackToSelector}
    />
  );
};

const SelectedThemePageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const params = useParams<{ id: string }>();
  const { selectedTheme, generatedThemes, setSelectedTheme, handleThemeDecision } = useApp();

  // URLからテーマIDを取得してテーマを設定
  useEffect(() => {
    if (params.id && !selectedTheme) {
      const theme = generatedThemes.find(t => t.id === params.id);
      if (theme) {
        setSelectedTheme(theme);
      }
    }
  }, [params.id, selectedTheme, generatedThemes, setSelectedTheme]);

  const handleBackToResults = () => {
    navigate('/results');
  };

  const handleBackToSelector = () => {
    navigate('/selector');
  };

  const handleThemeDecisionClick = (theme: any) => {
    handleThemeDecision(theme);
    navigate('/dashboard');
  };

  if (!selectedTheme) {
    return <div>テーマが見つかりません</div>;
  }

  return (
    <SelectedThemePage
      theme={selectedTheme}
      onBackToResults={handleBackToResults}
      onBackToSelector={handleBackToSelector}
      onThemeDecision={handleThemeDecisionClick}
    />
  );
};

const ActiveProjectPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const params = useParams<{ id: string }>();
  const {
    selectedProject,
    activeProjects,
    setSelectedProject,
    handleUpdateProjectProgress
  } = useApp();

  // URLからプロジェクトIDを取得してプロジェクトを設定
  useEffect(() => {
    if (params.id && !selectedProject) {
      const project = activeProjects.find(p => p.id === params.id);
      if (project) {
        setSelectedProject(project);
      }
    }
  }, [params.id, selectedProject, activeProjects, setSelectedProject]);

  const handleBack = () => {
    setSelectedProject(null);
    navigate('/dashboard');
  };

  const handleOpenChat = () => {
    navigate('/chat');
  };

  if (!selectedProject) {
    return <div>プロジェクトが見つかりません</div>;
  }

  return (
    <ActiveProjectPage
      project={selectedProject}
      onBack={handleBack}
      onUpdateProgress={handleUpdateProjectProgress}
      onOpenChat={handleOpenChat}
    />
  );
};

const ChatPageWrapper: React.FC = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/dashboard');
  };

  return <ChatPage />;
};

const RecordCalendarPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { activeProjects, records, schedules, addRecord } = useApp();

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleAddRecord = (record: Partial<Record>) => {
    // AppContextの addRecord メソッドを使用して記録を追加
    addRecord(record);

    // 成功メッセージを表示（将来的にはtoast通知などで置き換え）
    console.log('記録が正常に追加されました:', {
      title: record.title,
      type: record.recordType,
      date: new Date(record.recordDate || '').toLocaleDateString('ja-JP')
    });
  };

  const handleViewRecord = (record: Record) => {
    // 記録詳細を表示（将来的にはモーダルや詳細ページで表示）
    const recordDetails = {
      id: record.id,
      title: record.title,
      type: record.recordType,
      content: record.content,
      date: new Date(record.recordDate).toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      }),
      time: new Date(record.recordDate).toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
      }),
      projectId: record.projectId,
      data: record.data
    };

    console.log('記録詳細:', recordDetails);

    // 将来的にはここで詳細表示モーダルを開く
    // 例: setSelectedRecord(record); setShowRecordDetailModal(true);
  };

  return (
    <RecordCalendarPage
      activeProjects={activeProjects}
      records={records || []}
      schedules={schedules || []}
      onBack={handleBack}
      onAddRecord={handleAddRecord}
      onViewRecord={handleViewRecord}
    />
  );
};

// ルーターの設定
const router = createBrowserRouter([
  {
    path: '/',
    element: <SplashScreenWrapper />,
  },
  {
    path: '/login',
    element: <LoginPageWrapper />,
  },
  {
    path: '/signup',
    element: <SignupPageWrapper />,
  },
  {
    path: '/',
    element: (
      <PrivateRoute>
        <AppLayout />
      </PrivateRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <DashboardPageWrapper />,
      },
      {
        path: 'selector',
        element: <ThemeSelectorPageWrapper />,
      },
      {
        path: 'results',
        element: <ThemeResultsPageWrapper />,
      },
      {
        path: 'theme/:id',
        element: <SelectedThemePageWrapper />,
      },
      {
        path: 'project/:id',
        element: <ActiveProjectPageWrapper />,
      },
      {
        path: 'records',
        element: <RecordCalendarPageWrapper />,
      },
      {
        path: 'chat',
        element: <ChatPageWrapper />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

function App() {
  return (
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  );
}

export default App;
