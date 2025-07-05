import React, { useState } from 'react';
import { UserProfile, PartialUserProfile, Grade, Interest, Personality, Strength, Duration } from '../types';
import {gradeOptions, interestOptions, personalityOptions, strengthOptions, durationOptions} from '../constants/themeOptions';
import '../styles/Common.css';
import '../styles/ThemeSelector.css';

interface ThemeSelectorPageProps {
  onProfileComplete: (profile: UserProfile) => void;
  onBack: () => void;
}

const ThemeSelectorPage: React.FC<ThemeSelectorPageProps> = ({ onProfileComplete, onBack }) => {
  const [profile, setProfile] = useState<PartialUserProfile>({
    grade: undefined,
    interests: [],
    personality: [],
    strengths: [],
    duration: undefined
  });

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

      <div className="submit-section horizontal">
        <button
          className="submit-btn secondary"
          onClick={onBack}
        >
          <span className="label">戻る</span>
        </button>
        <button
          className={`submit-btn ${isComplete ? 'ready' : 'disabled'}`}
          onClick={handleSubmit}
          disabled={!isComplete}
        >
          <span className="emoji">🎉</span>
          <span className="label">自由研究のテーマを探す！</span>
        </button>
      </div>
    </div>
  );
};

export default ThemeSelectorPage;
