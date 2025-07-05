import React, { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import { UserProfile, ResearchTheme, ResearchProject, Achievement, UserStats } from './types';
import { generateMockThemes } from './utils/mockThemeGenerator';
import { mockActiveProjects, mockUserStats, mockRecentAchievements, mockPastProjects } from './utils/mockData';
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
