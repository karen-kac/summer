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

import { generateMockThemes } from './utils/mockThemeGenerator';
import { mockUserStats, mockRecentAchievements } from './utils/mockData';
import './styles/Common.css';

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
    setSelectedProject
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
    console.log('Open AI tutor');
    // TODO: AIチューター画面に遷移
  };

  const handleViewRecords = () => {
    navigate('/records');
  };

  const handleViewLearning = () => {
    console.log('View learning content');
    // TODO: 学習コンテンツ画面に遷移
  };

  return (
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
  );
};

const ThemeSelectorPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { setUserProfile, setGeneratedThemes } = useApp();

  const handleProfileComplete = (profile: any) => {
    setUserProfile(profile);
    const themes = generateMockThemes(profile);
    setGeneratedThemes(themes);
    navigate('/results');
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <ThemeSelectorPage
      onProfileComplete={handleProfileComplete}
      onBack={handleBack}
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

  if (!selectedProject) {
    return <div>プロジェクトが見つかりません</div>;
  }

  return (
    <ActiveProjectPage
      project={selectedProject}
      onBack={handleBack}
      onUpdateProgress={handleUpdateProjectProgress}
    />
  );
};

const RecordCalendarPageWrapper: React.FC = () => {
  const navigate = useNavigate();
  const { activeProjects, records, schedules } = useApp();

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleAddRecord = (record: any) => {
    // TODO: 記録追加のロジックを実装
    console.log('Add record:', record);
  };

  const handleViewRecord = (record: any) => {
    // TODO: 記録詳細表示のロジックを実装
    console.log('View record:', record);
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
