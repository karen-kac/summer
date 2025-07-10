import React, { useState } from 'react';
import { UserProfile, PartialUserProfile, Grade, Interest, Personality, Strength, Duration } from '../types';
import '../styles/Common.css';
import '../styles/ThemeSelector.css';

interface ThemeSelectorPageProps {
  onProfileComplete: (profile: UserProfile) => void;
  onBack: () => void;
  isLoading?: boolean;
  error?: string;
}

const ThemeSelectorPage: React.FC<ThemeSelectorPageProps> = ({ onProfileComplete, onBack, isLoading = false, error }) => {
  const [profile, setProfile] = useState<PartialUserProfile>({
    grade: undefined,
    interests: [],
    personality: [],
    strengths: [],
    duration: undefined
  });

  const gradeOptions: { value: Grade; label: string; emoji: string }[] = [
    { value: 'elementary1', label: '小学1年生', emoji: '🌟' },
    { value: 'elementary2', label: '小学2年生', emoji: '⭐' },
    { value: 'elementary3', label: '小学3年生', emoji: '✨' },
    { value: 'elementary4', label: '小学4年生', emoji: '🔥' },
    { value: 'elementary5', label: '小学5年生', emoji: '💪' },
    { value: 'elementary6', label: '小学6年生', emoji: '🎯' },
    { value: 'junior1', label: '中学1年生', emoji: '🚀' },
    { value: 'junior2', label: '中学2年生', emoji: '⚡' },
    { value: 'junior3', label: '中学3年生', emoji: '🎓' }
  ];

  const interestOptions: { value: Interest; label: string; emoji: string }[] = [
    { value: 'science', label: '理科・科学', emoji: '🔬' },
    { value: 'nature', label: '自然・環境', emoji: '🌱' },
    { value: 'animals', label: '動物・生物', emoji: '🐾' },
    { value: 'cooking', label: '料理・食べ物', emoji: '🍳' },
    { value: 'art', label: '美術・工作', emoji: '🎨' },
    { value: 'sports', label: 'スポーツ・運動', emoji: '⚽' },
    { value: 'music', label: '音楽・楽器', emoji: '🎵' },
    { value: 'history', label: '歴史・社会', emoji: '🏛️' },
    { value: 'technology', label: 'プログラミング・技術', emoji: '💻' },
    { value: 'math', label: '数学・計算', emoji: '📊' }
  ];

  const personalityOptions: { value: Personality; label: string; emoji: string }[] = [
    { value: 'curious', label: '好奇心旺盛', emoji: '🤔' },
    { value: 'patient', label: '根気強い', emoji: '😊' },
    { value: 'creative', label: '創造的', emoji: '💡' },
    { value: 'active', label: '活動的', emoji: '🏃' },
    { value: 'careful', label: '丁寧・慎重', emoji: '🔍' },
    { value: 'social', label: '協調性がある', emoji: '👥' },
    { value: 'analytical', label: '分析的・論理的', emoji: '🧠' },
    { value: 'independent', label: '自立している', emoji: '🎯' }
  ];

  const strengthOptions: { value: Strength; label: string; emoji: string }[] = [
    { value: 'observation', label: '観察', emoji: '👁️' },
    { value: 'writing', label: '文章を書く', emoji: '✍️' },
    { value: 'drawing', label: '絵を描く', emoji: '🖍️' },
    { value: 'crafting', label: 'ものづくり', emoji: '🔨' },
    { value: 'calculating', label: '計算・数学', emoji: '🧮' },
    { value: 'reading', label: '読書・調査', emoji: '📚' },
    { value: 'presentation', label: '発表・説明', emoji: '🎤' },
    { value: 'experiment', label: '実験・検証', emoji: '⚗️' }
  ];

  const durationOptions: { value: Duration; label: string; emoji: string }[] = [
    { value: '1week', label: '1週間', emoji: '📅' },
    { value: '2weeks', label: '2週間', emoji: '📆' },
    { value: '1month', label: '1ヶ月', emoji: '🗓️' },
    { value: '2months', label: '2ヶ月以上', emoji: '📋' },
    { value: 'flexible', label: '特に決まっていない', emoji: '🤷‍♀️' }
  ];

  // 型マッピング用のtype helper
  type FieldValueMap = {
    interests: Interest;
    personality: Personality;
    strengths: Strength;
  };

  const handleMultiSelect = <T extends keyof FieldValueMap>(
    field: T,
    value: FieldValueMap[T]
  ) => {
    setProfile(prev => {
      const currentArray = prev[field] as FieldValueMap[T][];
      const newArray = currentArray.includes(value)
        ? currentArray.filter(item => item !== value)
        : [...currentArray, value];

      return {
        ...prev,
        [field]: newArray
      };
    });
  };

  const handleSubmit = () => {
    if (profile.grade && profile.interests.length > 0) {
      const completeProfile: UserProfile = {
        grade: profile.grade,
        interests: profile.interests,
        personality: profile.personality,
        strengths: profile.strengths,
        duration: profile.duration || '2weeks' // デフォルト値を設定
      };
      onProfileComplete(completeProfile);
    }
  };

  const isComplete = profile.grade && profile.interests.length > 0;

  return (
    <div className="theme-selector">
      <div className="section">
        <h2>🎓 学年を選んでください（必須）</h2>
        <div className="options-grid">
          {gradeOptions.map(option => (
            <button
              key={option.value}
              className={`option-btn ${profile.grade === option.value ? 'selected' : ''}`}
              onClick={() => setProfile(prev => ({ ...prev, grade: option.value }))}
            >
              <span className="emoji">{option.emoji}</span>
              <span className="label">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <h2>❤️ 興味のある分野を選んでください（必須・複数選択可）</h2>
        <div className="options-grid">
          {interestOptions.map(option => (
            <button
              key={option.value}
              className={`option-btn ${profile.interests.includes(option.value) ? 'selected' : ''}`}
              onClick={() => handleMultiSelect('interests', option.value)}
            >
              <span className="emoji">{option.emoji}</span>
              <span className="label">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <h2>😊 あなたの性格は？（任意）</h2>
        <div className="options-grid">
          {personalityOptions.map(option => (
            <button
              key={option.value}
              className={`option-btn ${profile.personality.includes(option.value) ? 'selected' : ''}`}
              onClick={() => handleMultiSelect('personality', option.value)}
            >
              <span className="emoji">{option.emoji}</span>
              <span className="label">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <h2>💪 得意なことは？（任意）</h2>
        <div className="options-grid">
          {strengthOptions.map(option => (
            <button
              key={option.value}
              className={`option-btn ${profile.strengths.includes(option.value) ? 'selected' : ''}`}
              onClick={() => handleMultiSelect('strengths', option.value)}
            >
              <span className="emoji">{option.emoji}</span>
              <span className="label">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <h2>⏰ 研究にかけられる期間は？（任意）</h2>
        <div className="options-grid">
          {durationOptions.map(option => (
            <button
              key={option.value}
              className={`option-btn ${profile.duration === option.value ? 'selected' : ''}`}
              onClick={() => setProfile(prev => ({ ...prev, duration: option.value }))}
            >
              <span className="emoji">{option.emoji}</span>
              <span className="label">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-message" style={{
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '8px',
          textAlign: 'center',
          whiteSpace: 'pre-line'  // 改行文字を正しく表示
        }}>
          <span className="emoji">⚠️</span>
          <div className="label" style={{ marginLeft: '8px' }}>{error}</div>
        </div>
      )}

      <div className="submit-section horizontal">
        <button
          className="submit-btn secondary"
          onClick={onBack}
          disabled={isLoading}
        >
          <span className="label">戻る</span>
        </button>
        <button
          className={`submit-btn ${(isComplete && !isLoading) ? 'ready' : 'disabled'}`}
          onClick={handleSubmit}
          disabled={!isComplete || isLoading}
        >
          {isLoading ? (
            <>
              <span className="emoji">⏳</span>
              <span className="label">テーマを生成中...</span>
            </>
          ) : (
            <>
              <span className="emoji">🎉</span>
              <span className="label">自由研究のテーマを探す！</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default ThemeSelectorPage;
