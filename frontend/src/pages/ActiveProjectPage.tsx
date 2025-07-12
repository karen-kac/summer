import React, { useState, useEffect } from 'react';
import { ResearchProject, ResearchStep, Genre, AIResearchStep } from '../types';
import { themeApi } from '../services/api';
import '../styles/Common.css';
import '../styles/Components.css';
import '../styles/ActiveProject.css';

interface ActiveProjectPageProps {
  project: ResearchProject;
  onBack: () => void;
  onUpdateProgress: (projectId: string, stepIndex: number) => void;
  onOpenChat?: () => void;
}

interface StepTemplate {
  title: string;
  description: string;
  tips: string[];
  duration: string;
}

const ActiveProjectPage: React.FC<ActiveProjectPageProps> = ({
  project,
  onBack,
  onUpdateProgress,
  onOpenChat
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [projectSteps, setProjectSteps] = useState<StepTemplate[]>([]);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [isUsingAIPlan, setIsUsingAIPlan] = useState(false);
  const [planStatus, setPlanStatus] = useState<'cached' | 'generated' | 'default' | null>(null);

  // AIが生成したステップをStepTemplateに変換
  const convertAIStepsToTemplate = (aiSteps: AIResearchStep[]): StepTemplate[] => {
    return aiSteps.map(step => ({
      title: step.title,
      description: step.description,
      tips: step.tips,
      duration: step.duration
    }));
  };

  // 研究タイプに応じたステップテンプレートを定義（フォールバック用）
  const getDefaultStepTemplates = (genre: Genre): StepTemplate[] => {
    switch (genre) {
      case 'experiment':
        return [
          {
            title: '準備',
            description: '実験に必要な材料や道具を揃え、安全に実験を行うための環境を整えます。',
            tips: [
              '必要な材料をすべて揃えましょう',
              '実験を行う場所を確保しましょう',
              '安全対策を確認しましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '仮説設定',
            description: '実験の結果を予想し、なぜそうなると思うかの理由を考えます。',
            tips: [
              '「もし〜なら、〜になるだろう」の形で仮説を立てましょう',
              '仮説の理由も一緒に考えましょう',
              '複数の仮説を立てても良いです'
            ],
            duration: '1日'
          },
          {
            title: '実験設計',
            description: '仮説を確かめるための具体的な実験方法を計画します。',
            tips: [
              '実験の手順を詳しく書きましょう',
              '測定方法を決めましょう',
              '何回実験するか決めましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '実験実施',
            description: '計画に従って実験を行い、結果を観察・測定します。',
            tips: [
              '手順通りに実験を行いましょう',
              '結果をその場で記録しましょう',
              '写真や動画も撮りましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '結果記録',
            description: '実験で得られたデータや観察結果を整理します。',
            tips: [
              'データを表やグラフにまとめましょう',
              '写真や図も整理しましょう',
              '気づいたことをメモしましょう'
            ],
            duration: '1-2日'
          },
          {
            title: 'データ分析',
            description: '実験結果から傾向やパターンを見つけ出します。',
            tips: [
              'データの変化や傾向を見つけましょう',
              'グラフを作って視覚的に分析しましょう',
              '予想と違った部分があるか確認しましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '考察・結論',
            description: '結果から分かったことをまとめ、仮説が正しかったかを判断します。',
            tips: [
              '仮説が正しかったか検証しましょう',
              'なぜそうなったかを考えましょう',
              '新しい疑問があれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      case 'observation':
        return [
          {
            title: '準備',
            description: '観察に必要な道具を揃え、観察場所や対象を決めます。',
            tips: [
              '観察道具（虫眼鏡、定規、カメラなど）を準備しましょう',
              '観察する対象を決めましょう',
              '観察記録の方法を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '観察計画',
            description: 'いつ、どこで、何を、どのように観察するかを計画します。',
            tips: [
              '観察の時間帯を決めましょう',
              '観察の頻度を決めましょう',
              '記録する項目を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '継続観察',
            description: '計画に従って継続的に観察を行います。',
            tips: [
              '毎回同じ時間に観察しましょう',
              '変化を見逃さないよう注意深く観察しましょう',
              '写真やスケッチも活用しましょう'
            ],
            duration: '7-14日'
          },
          {
            title: '記録蓄積',
            description: '観察した内容を詳しく記録し、データを蓄積します。',
            tips: [
              '日付、時間、天気も記録しましょう',
              '変化を具体的に記録しましょう',
              '疑問に思ったことも書き留めましょう'
            ],
            duration: '継続'
          },
          {
            title: 'パターン発見',
            description: '蓄積したデータから規則性や変化のパターンを見つけます。',
            tips: [
              'グラフや表を作って変化を可視化しましょう',
              '繰り返し起こることがないか探しましょう',
              '環境の変化と観察対象の変化を比較しましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '考察・結論',
            description: '観察結果から分かったことをまとめ、結論を導きます。',
            tips: [
              '発見したパターンの理由を考えましょう',
              '他の要因との関係を考えましょう',
              'さらに詳しく調べたいことがあれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      case 'research':
        return [
          {
            title: '準備',
            description: '調査に必要な道具や方法を準備し、調査対象を明確にします。',
            tips: [
              '調査テーマを明確にしましょう',
              '調査方法を決めましょう',
              '必要な道具や資料を準備しましょう'
            ],
            duration: '1日'
          },
          {
            title: '問題設定',
            description: '調査で明らかにしたい問題や疑問を具体的に設定します。',
            tips: [
              '調べたい疑問を具体的に書きましょう',
              '調査の目的を明確にしましょう',
              '調査範囲を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '情報収集',
            description: '本、インターネット、アンケート、インタビューなどで情報を集めます。',
            tips: [
              '複数の情報源から情報を集めましょう',
              '情報の出典を記録しましょう',
              '信頼できる情報か確認しましょう'
            ],
            duration: '3-5日'
          },
          {
            title: 'データ整理',
            description: '集めた情報を分類し、整理します。',
            tips: [
              '情報をテーマ別に分類しましょう',
              '表やグラフを使って整理しましょう',
              '重要な情報を見つけやすくしましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '分析・比較',
            description: '整理した情報を分析し、比較検討します。',
            tips: [
              '異なる情報を比較しましょう',
              '共通点や相違点を見つけましょう',
              '傾向やパターンを探しましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '考察・結論',
            description: '分析結果から結論を導き、自分の考えをまとめます。',
            tips: [
              '調査結果から分かったことをまとめましょう',
              '自分の考えや意見を書きましょう',
              '新しい疑問があれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      default:
        return [];
    }
  };

  // 研究計画を取得または生成
  const loadResearchPlan = async (themeId: string) => {
    setIsLoadingPlan(true);
    setPlanError(null);

    try {
      // まず既存の研究計画を取得を試行
      const existingPlanResponse = await themeApi.getResearchPlan(themeId);

      if (existingPlanResponse.success && existingPlanResponse.plan) {
        const aiSteps = convertAIStepsToTemplate(existingPlanResponse.plan.steps);
        setProjectSteps(aiSteps);
        setIsUsingAIPlan(true);
        setPlanStatus('cached');
        return;
      }

      // 既存の研究計画がない場合、新しく生成
      const generateResponse = await themeApi.generateResearchPlan(themeId);

      if (generateResponse.success && generateResponse.plan) {
        const aiSteps = convertAIStepsToTemplate(generateResponse.plan.steps);
        setProjectSteps(aiSteps);
        setIsUsingAIPlan(true);
        setPlanStatus('generated');
      } else {
        const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
        setProjectSteps(defaultSteps);
        setIsUsingAIPlan(false);
        setPlanStatus('default');
      }
    } catch (error) {
      setPlanError('研究計画の取得に失敗しました。デフォルトプランを使用します。');
      const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
      setProjectSteps(defaultSteps);
      setIsUsingAIPlan(false);
      setPlanStatus('default');
    } finally {
      setIsLoadingPlan(false);
    }
  };

  useEffect(() => {
    // プロジェクトにthemeIdがある場合、研究計画を取得
    if (project.themeId) {
      loadResearchPlan(project.themeId);
    } else {
      const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
      setProjectSteps(defaultSteps);
      setIsUsingAIPlan(false);
      setPlanStatus('default');
    }
  }, [project]);

  useEffect(() => {
    if (projectSteps.length > 0) {
      // プロジェクトの進捗から現在のステップを計算
      const progressIndex = Math.floor((project.progressPercentage / 100) * projectSteps.length);
      setCurrentStepIndex(Math.min(progressIndex, projectSteps.length - 1));
    }
  }, [project.progressPercentage, projectSteps]);

  const handleStepComplete = () => {
    if (currentStepIndex < projectSteps.length - 1) {
      const newStepIndex = currentStepIndex + 1;
      setCurrentStepIndex(newStepIndex);
      onUpdateProgress(project.id, newStepIndex);
    }
  };

  const handleStepSelect = (stepIndex: number) => {
    setCurrentStepIndex(stepIndex);
  };

  const getGenreDisplayName = (genre: Genre) => {
    const genreMap = {
      'experiment': '実験型',
      'observation': '観察型',
      'research': '調査型'
    };
    return genreMap[genre] || '実験型';
  };

  const getGenreIcon = (genre: Genre) => {
    const iconMap = {
      'experiment': '🧪',
      'observation': '👀',
      'research': '📚'
    };
    return iconMap[genre] || '🧪';
  };

  const getPlanStatusMessage = () => {
    switch (planStatus) {
      case 'cached':
        return '保存された研究計画を使用しています';
      case 'generated':
        return '新しい研究計画を生成・保存しました';
      case 'default':
        return 'デフォルトの研究計画を使用しています';
      default:
        return '';
    }
  };

  // ローディング中の表示
  if (isLoadingPlan) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>研究計画を準備中...</h2>
          <p>あなたのテーマに最適な研究計画を取得しています。</p>
        </div>
      </div>
    );
  }

  // ステップがない場合の表示
  if (projectSteps.length === 0) {
    return (
      <div className="page-container">
        <div className="error-container">
          <h2>研究計画の読み込みに失敗しました</h2>
          <p>しばらく待ってから再度お試しください。</p>
          <button onClick={onBack}>ダッシュボードに戻る</button>
        </div>
      </div>
    );
  }

  const currentStep = projectSteps[currentStepIndex];
  const progressPercentage = ((currentStepIndex + 1) / projectSteps.length) * 100;

  return (
    <div className="page-container">
      <div className="header-section">
        <button className="back-button" onClick={onBack}>
          ← ダッシュボードに戻る
        </button>
        <div className="project-header">
          <div className="project-title-section">
            <h1>{project.title}</h1>
            <div className="project-meta">
              <span className="genre-badge">
                {getGenreIcon(project.genre || 'experiment')} {getGenreDisplayName(project.genre || 'experiment')}
              </span>
              {isUsingAIPlan && (
                <span className="ai-badge">
                  🤖 AI研究計画
                </span>
              )}
            </div>
          </div>
          <div className="overall-progress">
            <div className="progress-header">
              <span>全体の進捗</span>
              <span>{Math.round(progressPercentage)}%</span>
            </div>
            <div className="progress-bar-outer">
              <div className="progress-bar-inner" style={{ width: `${progressPercentage}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {planError && (
        <div className="error-notice">
          <span>⚠️ {planError}</span>
        </div>
      )}

      {planStatus && (
        <div className="plan-status-notice">
          <span>ℹ️ {getPlanStatusMessage()}</span>
        </div>
      )}

      <div className="active-project-content">
        <div className="steps-timeline">
          <h2>研究の流れ</h2>
          <div className="timeline">
            {projectSteps.map((step, index) => (
              <div
                key={index}
                className={`timeline-item ${index === currentStepIndex ? 'current' : ''} ${
                  index < currentStepIndex ? 'completed' : ''
                }`}
                onClick={() => handleStepSelect(index)}
              >
                <div className="timeline-marker">
                  {index < currentStepIndex ? '✅' : index === currentStepIndex ? '❗️' : '🔸'}
                </div>
                <div className="timeline-content">
                  <div className="step-title">{step.title}</div>
                  <div className="step-duration">{step.duration}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="current-step-detail">
          <div className="step-card">
            <div className="step-header">
              <h2>
                ステップ {currentStepIndex + 1}: {currentStep.title}
              </h2>
              <div className="step-status">
                {currentStepIndex < projectSteps.length - 1 ? '進行中' : '最終ステップ'}
              </div>
            </div>

            <div className="step-description">
              <h3>このステップでやること</h3>
              <p>{currentStep.description}</p>
            </div>

            <div className="step-tips">
              <h3>💡 ポイント</h3>
              <ul>
                {currentStep.tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>

            <div className="step-duration-info">
              <strong>目安時間:</strong> {currentStep.duration}
            </div>

            <div className="step-actions">
              {currentStepIndex < projectSteps.length - 1 ? (
                <button className="step-complete-btn" onClick={handleStepComplete}>
                  このステップを完了して次へ
                </button>
              ) : (
                <button className="step-complete-btn" onClick={handleStepComplete}>
                  研究を完了する
                </button>
              )}

              <div className="secondary-actions">
                <button className="secondary-btn">
                  📝 メモを記録
                </button>
                <button className="secondary-btn">
                  📷 写真を追加
                </button>
                <button className="secondary-btn" onClick={onOpenChat}>
                  🤖 AI先生に質問
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveProjectPage;
