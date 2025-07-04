import React, { useState } from 'react';
import ThemeSelectorPage from './pages/ThemeSelectorPage';
import ThemeResultsPage from './pages/ThemeResultsPage';
import SelectedThemePage from './pages/SelectedThemePage';
import { UserProfile, ResearchTheme } from './types';
import { generateMockThemes } from './utils/mockThemeGenerator';
import './App.css';

type AppState = 'selector' | 'results' | 'selected';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('selector');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [generatedThemes, setGeneratedThemes] = useState<ResearchTheme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<ResearchTheme | null>(null);

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

  const handleBackToSelector = () => {
    setCurrentState('selector');
    setUserProfile(null);
    setGeneratedThemes([]);
    setSelectedTheme(null);
  };

  const handleBackToResults = () => {
    setCurrentState('results');
    setSelectedTheme(null);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>夏休み自由研究AI</h1>
        <p>AIがあなたにぴったりの自由研究テーマを提案します！（小学生〜中学生対象）</p>
      </header>

      {currentState === 'selector' && (
        <ThemeSelectorPage onProfileComplete={handleProfileComplete} />
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
    </div>
  );
}

export default App;
