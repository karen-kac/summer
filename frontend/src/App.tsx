import React, { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import { UserProfile, ResearchTheme, ResearchProject, Achievement, UserStats } from './types';
import { generateMockThemes } from './utils/mockThemeGenerator';
import './App.css';
import './styles/Common.css';

type AppState = 'dashboard' | 'selector' | 'results' | 'selected';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('dashboard');
  const [userProfile, setUserProfile] = useState<UserProfile | null>({
    grade: 'elementary4',
    interests: ['science', 'nature'],
    personality: ['curious', 'patient'],
    strengths: ['observation', 'writing'],
    duration: '2weeks'
  });
  const [generatedThemes, setGeneratedThemes] = useState<ResearchTheme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<ResearchTheme | null>(null);

  // モックデータ
  const mockActiveProjects: ResearchProject[] = [
    {
      id: 'project-1',
      userId: 'user-1',
      themeId: 'theme-1',
      title: '植物の成長観察',
      description: '豆の成長を毎日記録する実験',
      status: 'in_progress',
      startDate: '2025-07-01',
      targetEndDate: '2025-07-21',
      customMaterials: [],
      customSteps: [],
      progressPercentage: 65,
      createdAt: '2025-07-01',
      updatedAt: '2025-07-04'
    }
  ];

  const mockUserStats: UserStats = {
    totalPoints: 1250,
    level: 5,
    completedProjects: 2,
    currentStreak: 7,
    totalRecords: 23,
    totalPhotos: 15,
    totalExperiments: 8
  };

  const mockRecentAchievements: Achievement[] = [
    {
      id: 'achievement-1',
      name: '初回観察完了',
      description: '初めての観察記録を作成しました',
      icon: '🔬',
      category: 'observation',
      requirements: {},
      points: 100,
      isActive: true,
      createdAt: '2025-07-01'
    },
    {
      id: 'achievement-2',
      name: '7日連続記録',
      description: '7日間連続で記録を作成しました',
      icon: '🔥',
      category: 'consistency',
      requirements: {},
      points: 200,
      isActive: true,
      createdAt: '2025-07-02'
    }
  ];

  const mockPastProjects: ResearchProject[] = [
    {
      id: 'past-project-1',
      userId: 'user-1',
      themeId: 'theme-past-1',
      title: '水の表面張力実験',
      description: '水の表面張力について調べる実験',
      status: 'completed',
      startDate: '2024-08-01',
      targetEndDate: '2024-08-15',
      actualEndDate: '2024-08-14',
      customMaterials: ['水', 'コップ', 'クリップ'],
      customSteps: [],
      progressPercentage: 100,
      createdAt: '2024-08-01',
      updatedAt: '2024-08-14'
    },
    {
      id: 'past-project-2',
      userId: 'user-1',
      themeId: 'theme-past-2',
      title: '植物の光合成実験',
      description: '光の強さと植物の成長の関係を調べる',
      status: 'completed',
      startDate: '2024-07-15',
      targetEndDate: '2024-08-05',
      actualEndDate: '2024-08-03',
      customMaterials: ['豆', '植木鉢', 'LEDライト'],
      customSteps: [],
      progressPercentage: 100,
      createdAt: '2024-07-15',
      updatedAt: '2024-08-03'
    }
  ];

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

  return (
    <div className="app">
      <header className="header">
        <h1>夏休み自由研究AI</h1>
        <p>AIがあなたにぴったりの自由研究テーマを提案します！（小学生〜中学生対象）</p>
      </header>

      {currentState === 'dashboard' && (
        <DashboardPage
          userProfile={userProfile}
          activeProjects={mockActiveProjects}
          pastProjects={mockPastProjects}
          userStats={mockUserStats}
          recentAchievements={mockRecentAchievements}
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
        />
      )}

      {/* フローティングダッシュボードボタン（ダッシュボード以外の画面で表示） */}
      {currentState !== 'dashboard' && (
        <button 
          className="floating-dashboard-btn"
          onClick={handleBackToDashboard}
          title="ダッシュボードに戻る"
        >
          🏠
        </button>
      )}
    </div>
  );
}

export default App;