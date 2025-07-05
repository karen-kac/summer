import { Grade, Interest, Personality, Strength, Duration } from '../types';

export const gradeOptions: { value: Grade; label: string; emoji: string }[] = [
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

export const interestOptions: { value: Interest; label: string; emoji: string }[] = [
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

export const personalityOptions: { value: Personality; label: string; emoji: string }[] = [
    { value: 'curious', label: '好奇心旺盛', emoji: '🤔' },
    { value: 'patient', label: '根気強い', emoji: '😊' },
    { value: 'creative', label: '創造的', emoji: '💡' },
    { value: 'active', label: '活動的', emoji: '🏃' },
    { value: 'careful', label: '丁寧・慎重', emoji: '🔍' },
    { value: 'social', label: '協調性がある', emoji: '👥' },
    { value: 'analytical', label: '分析的・論理的', emoji: '🧠' },
    { value: 'independent', label: '自立している', emoji: '🎯' }
  ];

export const strengthOptions: { value: Strength; label: string; emoji: string }[] = [
    { value: 'observation', label: '観察', emoji: '👁️' },
    { value: 'writing', label: '文章を書く', emoji: '✍️' },
    { value: 'drawing', label: '絵を描く', emoji: '🖍️' },
    { value: 'crafting', label: 'ものづくり', emoji: '🔨' },
    { value: 'calculating', label: '計算・数学', emoji: '🧮' },
    { value: 'reading', label: '読書・調査', emoji: '📚' },
    { value: 'presentation', label: '発表・説明', emoji: '🎤' },
    { value: 'experiment', label: '実験・検証', emoji: '⚗️' }
  ];

export const durationOptions: { value: Duration; label: string; emoji: string }[] = [
    { value: '1week', label: '1週間', emoji: '📅' },
    { value: '2weeks', label: '2週間', emoji: '📆' },
    { value: '1month', label: '1ヶ月', emoji: '🗓️' },
    { value: '2months', label: '2ヶ月以上', emoji: '📋' },
    { value: 'flexible', label: '特に決まっていない', emoji: '🤷‍♀️' }
  ];
