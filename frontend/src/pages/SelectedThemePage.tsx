import React from 'react';
import { ResearchTheme } from '../types';
import '../styles/Common.css';
import '../styles/SelectedTheme.css';

interface SelectedThemePageProps {
  theme: ResearchTheme;
  onBackToResults: () => void;
  onBackToSelector: () => void;
}

const SelectedThemePage: React.FC<SelectedThemePageProps> = ({
  theme,
  onBackToResults,
  onBackToSelector
}) => {
  return (
    <div className="theme-selected">
      <div className="selected-header">
        <h1>選択した自由研究テーマ</h1>
        <h2>{theme.title}</h2>
        <p>このテーマで自由研究を進めましょう！</p>
      </div>

      <div className="selected-content">
        <div className="description-card">
          <h3>研究テーマの概要</h3>
          <p>{theme.description}</p>
        </div>

        <div className="materials-card">
          <h3>必要な材料・道具</h3>
          <ul>
            {theme.materials.map((material, index) => (
              <li key={index}>{material}</li>
            ))}
          </ul>
        </div>

        <div className="steps-card">
          <h3>研究の進め方</h3>
          <ol>
            {theme.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </div>
      </div>

      <div className="selected-actions">
        <button className="back-btn" onClick={onBackToResults}>
          <span className="emoji">🔙</span>
          <span className="label">テーマ一覧に戻る</span>
        </button>
        <button className="back-btn" onClick={onBackToSelector}>
          <span className="emoji">🔄</span>
          <span className="label">最初から選び直す</span>
        </button>
      </div>
    </div>
  );
};

export default SelectedThemePage;
