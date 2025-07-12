import React, { useState } from 'react';
import { ResearchTheme } from '../types';
import { themeApi } from '../services/api';
import { useApp } from '../context/AppContext';
import '../styles/Common.css';
import '../styles/SelectedTheme.css';

interface SelectedThemePageProps {
  theme: ResearchTheme;
  onBackToResults: () => void;
  onBackToSelector: () => void;
  onThemeDecision: (theme: ResearchTheme) => void;
}

const SelectedThemePage: React.FC<SelectedThemePageProps> = ({
  theme,
  onBackToResults,
  onBackToSelector,
  onThemeDecision
}) => {
  const { activeProjects } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<'success' | 'error' | null>(null);

  const hasActiveProject = activeProjects.length > 0;

  const handleThemeDecision = async () => {
    setIsLoading(true);
    setMessage(null);
    setMessageType(null);

    console.log('🎯 テーマ決定処理開始:', {
      themeId: theme.id,
      themeTitle: theme.title,
      hasActiveProject
    });

    try {
      console.log('💾 テーマを保存中...', theme);
      const response = await themeApi.saveTheme(theme);
      console.log('📊 テーマ保存結果:', response);

      if (response.success) {
        if (hasActiveProject) {
          setMessage('既存の研究を過去の研究として保存し、新しいテーマでプロジェクトを作成しています...');
        } else {
          setMessage('テーマが正常に保存されました！新しいプロジェクトを作成しています...');
        }
        setMessageType('success');

        console.log('✅ テーマ保存成功、テーマID:', response.saved_theme_id);

        // 保存されたテーマIDでテーマオブジェクトを更新
        const updatedTheme: ResearchTheme = {
          ...theme,
          id: response.saved_theme_id
        };

        console.log('🔄 テーマIDを更新しました:', {
          oldId: theme.id,
          newId: response.saved_theme_id
        });

        // 少し遅延してから次の画面に進む
        setTimeout(() => {
          onThemeDecision(updatedTheme);
        }, 1500);
      } else {
        console.error('❌ テーマ保存失敗:', response.message);
        setMessage(`保存に失敗しました: ${response.message}`);
        setMessageType('error');
      }
    } catch (error) {
      console.error('❌ テーマ保存エラー:', error);
      setMessage('ネットワークエラーが発生しました。もう一度お試しください。');
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="theme-selected">
      <div className="selected-header">
        <h1>選択した自由研究テーマ</h1>
        <h2>{theme.title}</h2>
        <p>このテーマで自由研究を進めましょう！</p>
      </div>

      {/* 既存のアクティブプロジェクトがある場合の警告 */}
      {/* {hasActiveProject && (
        <div className="warning-notice">
          <h3>⚠️ 注意</h3>
          <p>
            現在進行中の研究「{activeProjects[0].title}」があります。<br/>
            新しいテーマを選択すると、この研究は<strong>過去の研究として自動保存</strong>され、<br/>
            新しいテーマで研究を開始します。
          </p>
        </div>
      )} */}

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

      {/* メッセージ表示エリア */}
      {message && (
        <div className={`message ${messageType}`}>
          <p>{message}</p>
        </div>
      )}

      <div className="selected-actions">
        <button className="back-btn" onClick={onBackToResults} disabled={isLoading}>
          <span className="emoji">🔙</span>
          <span className="label">テーマ一覧に戻る</span>
        </button>
        <button
          className="select-theme-btn"
          onClick={handleThemeDecision}
          disabled={isLoading}
        >
          <span className="emoji">{isLoading ? '⏳' : '🎯'}</span>
          <span className="label">
            {isLoading
              ? '保存中...'
              : hasActiveProject
                ? '既存の研究を保存して新しいテーマに決定する！'
                : 'このテーマに決定する！'
            }
          </span>
        </button>
        <button className="back-btn" onClick={onBackToSelector} disabled={isLoading}>
          <span className="emoji">🔄</span>
          <span className="label">最初から選び直す</span>
        </button>
      </div>
    </div>
  );
};

export default SelectedThemePage;
