import React from 'react';
import { ResearchTheme } from '../types';
import '../styles/Common.css';
import '../styles/ThemeResults.css';

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

  // テーマがない場合の表示
  if (themes.length === 0) {
    return (
      <div className="theme-results">
        <div className="results-header">
          <h1>😔 テーマが見つかりませんでした</h1>
          <p>サーバーとの接続に問題があったようです</p>
        </div>

        <div className="no-themes-message" style={{
          textAlign: 'center',
          padding: '40px 20px',
          backgroundColor: '#f5f5f5',
          borderRadius: '12px',
          margin: '20px 0'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>🚫</div>
          <h3 style={{ color: '#666', marginBottom: '15px' }}>テーマを生成できませんでした</h3>
          <p style={{ color: '#888', lineHeight: '1.6' }}>
            以下をお試しください：<br/>
            • ページを再読み込みしてください<br/>
            • サーバーが起動していることを確認してください<br/>
            • しばらく時間をおいて再度お試しください
          </p>
        </div>

        <div className="back-section">
          <button className="back-btn" onClick={onBackToSelector}>
            <span className="emoji">🔄</span>
            <span className="label">再度テーマを探す</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-results">
      <div className="results-header">
        <h1>🎯 あなたにおすすめの自由研究テーマ！</h1>
        <p>{themes.length}つのテーマから選んでください</p>
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
              <span className="label">詳しくみてみる</span>
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
