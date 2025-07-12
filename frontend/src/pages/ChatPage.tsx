import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatBot } from '../components/ChatBot';
import { useApp } from '../context/AppContext';

export const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeProjects, selectedProject } = useApp();
  
  // 現在のアクティブプロジェクトを取得
  const currentProject = selectedProject || activeProjects[0];
  const userId = "user123";
  const projectId = currentProject?.id || "default_project";

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleBackToProject = () => {
    if (currentProject) {
      navigate(`/project/${currentProject.id}`);
    } else {
      navigate('/dashboard');
    }
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
      
      {currentProject && (
        <div style={{ 
          padding: '10px 15px', 
          backgroundColor: '#e3f2fd', 
          borderRadius: '8px', 
          marginBottom: '20px',
          border: '1px solid #bbdefb'
        }}>
          <strong>現在の研究:</strong> {currentProject.title} 
          <span style={{ marginLeft: '10px', fontSize: '0.9em', color: '#666' }}>
            (進捗: {currentProject.progressPercentage}%)
          </span>
        </div>
      )}
      
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