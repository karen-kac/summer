import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatBot } from '../components/ChatBot';
import { useApp } from '../context/AppContext';
import { themeApi } from '../services/api';
import { AIResearchStep } from '../types';

interface StepTemplate {
  title: string;
  description: string;
  tips: string[];
  duration: string;
}

export const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeProjects, selectedProject } = useApp();
  const [projectSteps, setProjectSteps] = useState<StepTemplate[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // 現在のアクティブプロジェクトを取得
  const currentProject = selectedProject || activeProjects[0];
  
  // currentProjectがない場合はダッシュボードにリダイレクト
  if (!currentProject) {
    navigate('/dashboard');
    return null;
  }
  
  const userId = "user123";
  const projectId = currentProject.id;
  
  // AIが生成したステップをStepTemplateに変換
  const convertAIStepsToTemplate = (aiSteps: AIResearchStep[]): StepTemplate[] => {
    return aiSteps.map(step => ({
      title: step.title,
      description: step.description,
      tips: step.tips,
      duration: step.duration
    }));
  };
  
  // 研究計画を読み込み
  useEffect(() => {
    const loadResearchPlan = async () => {
      if (currentProject.themeId) {
        try {
          const response = await themeApi.generateResearchPlan(currentProject.themeId);
          if (response.success && response.plan) {
            const aiSteps = convertAIStepsToTemplate(response.plan.steps);
            setProjectSteps(aiSteps);
          }
        } catch (error) {
          console.error('研究計画の取得エラー:', error);
        }
      }
    };
    
    loadResearchPlan();
  }, [currentProject.themeId]);
  
  // 現在のステップインデックスを設定
  useEffect(() => {
    if (projectSteps.length > 0) {
      if (currentProject.currentStepIndex !== undefined && currentProject.currentStepIndex >= 0) {
        const newStepIndex = Math.min(currentProject.currentStepIndex, projectSteps.length - 1);
        setCurrentStepIndex(newStepIndex);
      } else {
        const progressIndex = Math.floor((currentProject.progressPercentage / 100) * projectSteps.length);
        const newStepIndex = Math.min(progressIndex, projectSteps.length - 1);
        setCurrentStepIndex(newStepIndex);
      }
    }
  }, [currentProject.currentStepIndex, currentProject.progressPercentage, projectSteps]);
  
  // 進捗率を計算
  const progressPercentage = projectSteps.length > 0 
    ? ((currentStepIndex + 1) / projectSteps.length) * 100
    : currentProject.progressPercentage;

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleBackToProject = () => {
    navigate(`/project/${currentProject.id}`);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>🤖 AI先生とチャット</h1>
        <div className="navigation-buttons">
          <button className="back-button" onClick={handleBackToDashboard}>
            ダッシュボードに戻る
          </button>
          {currentProject && (
            <button className="back-button" onClick={handleBackToProject}>
              進行中の研究に戻る
            </button>
          )}
        </div>
      </div>
      
      <div style={{ 
        padding: '10px 15px', 
        backgroundColor: '#e3f2fd', 
        borderRadius: '8px', 
        marginBottom: '20px',
        border: '1px solid #bbdefb'
      }}>
        <strong>現在の研究:</strong> {currentProject.title} 
        <span style={{ marginLeft: '10px', fontSize: '0.9em', color: '#666' }}>
          (進捗: {Math.round(progressPercentage)}% - ステップ {currentStepIndex + 1}/{projectSteps.length || 1})
        </span>
      </div>
      
      <p>研究について何でも質問してください。写真や音声も送れます！</p>
      
      <ChatBot userId={userId} projectId={projectId} />
      
      <div className="chat-tips">
        <h3>💡 使い方のヒント</h3>
        <ul>
          <li>研究で困ったことがあれば何でも聞いてください</li>
          <li>観察した写真を送ると、AI先生が解析してくれます</li>
          <li>実験のやり方や安全な方法を教えてもらえます</li>
          <li>レポートの書き方もサポートします</li>
        </ul>
      </div>
    </div>
  );
};