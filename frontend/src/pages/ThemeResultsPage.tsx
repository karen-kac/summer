import React from 'react';
import { ResearchTheme } from '../types';

interface ThemeResultsPageProps {
  themes: ResearchTheme[];
  onThemeSelect: (theme: ResearchTheme) => void;
  onBackToSelector: () => void;
}

const ThemeResultsPage: React.FC<ThemeResultsPageProps> = ({ themes, onThemeSelect, onBackToSelector }) => {
  const getDifficultyEmoji = (difficulty: ResearchTheme['difficulty']) => {
    switch (difficulty) {
      case 'easy': return '🌟';
      case 'medium': return '⭐⭐';
      case 'hard': return '⭐⭐⭐';
      default: return '🌟';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '初級';
      case 'medium': return '中級';
      case 'hard': return '上級';
      default: return '初級';
    }
  };

  return (
    <div className="theme-results">
      <div className="results-header">
        <h1>🎯 あなたにおすすめの自由研究テーマ！</h1>
        <p>3つのテーマから選んでください</p>
      </div>

      <div className="themes-grid">
        {themes.map((theme, index) => (
          <div key={theme.id} className="theme-card">
            <div className="theme-header">
              <span className="theme-number">{index + 1}</span>
              <div className="difficulty-badge">
                <span className="emoji">{getDifficultyEmoji(theme.difficulty)}</span>
                <span className="label">{getDifficultyLabel(theme.difficulty)}</span>
              </div>
            </div>

            <h3 className="theme-title">{theme.title}</h3>
            <p className="theme-description">{theme.description}</p>

            <div className="theme-details">
              <div className="detail-item">
                <span className="emoji">📅</span>
                <span className="label">期間: {theme.estimatedDays}日</span>
              </div>

              <div className="detail-item">
                <span className="emoji">🛠️</span>
                <span className="label">必要な材料：</span>
                <ul className="materials-list">
                  {theme.materials.slice(0, 3).map((material, idx) => (
                    <li key={idx}>{material}</li>
                  ))}
                  {theme.materials.length > 3 && <li>...など</li>}
                </ul>
              </div>
            </div>

            <button
              className="select-theme-btn"
              onClick={() => onThemeSelect(theme)}
            >
              <span className="emoji">✨</span>
              <span className="label">このテーマに決める！</span>
            </button>
          </div>
        ))}
      </div>

      <div className="back-section">
        <button className="back-btn" onClick={onBackToSelector}>
          <span className="emoji">🔄</span>
          <span className="label">別のテーマを探す</span>
        </button>
      </div>
    </div>
  );
};

export default ThemeResultsPage;
