import React from 'react';
import { UserProfile, ResearchProject, Achievement } from '../types';
import '../styles/Dashboard.css';
import '../styles/Common.css';
import '../styles/Components.css';

interface TaskItem {
  icon: string;
  task: string;
  urgent: boolean;
}

interface DashboardPageProps {
  userProfile: UserProfile | null;
  activeProjects: ResearchProject[];
  pastProjects: ResearchProject[];
  userStats: {
    totalPoints: number;
    level: number;
    completedProjects: number;
    currentStreak: number;
  };
  recentAchievements: Achievement[];
  todaysTasks: TaskItem[];
  onStartNewResearch: () => void;
  onContinueProject: (project: ResearchProject) => void;
  onViewAllProjects: () => void;
  onOpenAITutor: () => void;
  onViewRecords: () => void;
  onViewLearning: () => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({
  userProfile,
  activeProjects,
  pastProjects,
  userStats,
  recentAchievements,
  todaysTasks,
  onStartNewResearch,
  onContinueProject,
  onViewAllProjects,
  onOpenAITutor,
  onViewRecords,
  onViewLearning
}) => {
  const getGradeDisplayName = (grade: string) => {
    const gradeMap: { [key: string]: string } = {
      'elementary1': '小学1年生',
      'elementary2': '小学2年生',
      'elementary3': '小学3年生',
      'elementary4': '小学4年生',
      'elementary5': '小学5年生',
      'elementary6': '小学6年生',
      'junior1': '中学1年生',
      'junior2': '中学2年生',
      'junior3': '中学3年生'
    };
    return gradeMap[grade] || grade;
  };

  const getInterestEmoji = (interest: string) => {
    const emojiMap: { [key: string]: string } = {
      'science': '🔬',
      'nature': '🌱',
      'animals': '🐾',
      'cooking': '🍳',
      'art': '🎨',
      'sports': '⚽',
      'music': '🎵',
      'history': '🏛️',
      'technology': '💻',
      'math': '📊'
    };
    return emojiMap[interest] || '✨';
  };

  const getLevelEmoji = (level: number) => {
    if (level >= 10) return '🏆';
    if (level >= 7) return '🥇';
    if (level >= 4) return '🥈';
    if (level >= 2) return '🥉';
    return '🌟';
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'おはよう！';
    if (hour < 18) return 'こんにちは！';
    return 'こんばんは！';
  };

  return (
    <div className="dashboard-grid">
      {/* 上段：3つ横並び */}
      <div className="dashboard-row">
        <div className="card main-action-card">
          <div className="card-title">🚀 テーマ決め</div>
		  <div>AIと一緒に自由研究のテーマを考えよう！</div>
		  <div style={{ height: '10px' }}></div>
          <button className="select-theme-btn" onClick={onStartNewResearch}>
            <span className="main-action-text">自由研究のテーマを決めよう！</span>
          </button>
        </div>
        <div className="card projects-card">
          <div className="card-title">🔬 進行中の研究</div>
          {activeProjects.length === 0 ? (
            <div>進行中の研究はありません</div>
          ) : (
            activeProjects.slice(0, 2).map((project) => (
              <div key={project.id} className="project-card-inner">
                <div className="project-title">{project.title}</div>
                <div className="progress-bar-outer">
                  <div className="progress-bar-inner" style={{ width: `${project.progressPercentage}%` }}></div>
                </div>
                <button className="continue-btn" onClick={() => onContinueProject(project)}>
                  <span className="emoji">▶️</span> 続きを見る
                </button>
              </div>
            ))
          )}
        </div>
        <div className="card tasks-card">
          <div className="card-title">📅 今日のタスク</div>
          {todaysTasks.map((task, i) => (
            <div key={i} className={`task-item${task.urgent ? " urgent" : ""}`}>
              <span className="task-icon">{task.icon}</span>
              <span className="task-text">{task.task}</span>
              {task.urgent && <span className="urgent-badge">急ぎ</span>}
            </div>
          ))}
        </div>
      </div>
      {/* 下段：2つ横並び */}
      <div className="dashboard-row">
        <div className="card achievements-card">
          <div className="card-title">🏆 最近の実績</div>
          {recentAchievements.length === 0 ? (
            <div>まだ実績はありません</div>
          ) : (
            recentAchievements.slice(0, 3).map((ach) => (
              <div key={ach.id} className="achievement-item">
                <span className="achievement-icon">{ach.icon}</span>
                <span className="achievement-name">{ach.name}</span>
                <span className="achievement-points">+{ach.points}</span>
              </div>
            ))
          )}
        </div>
        <div className="card past-projects-card">
          <div className="card-title">📚 過去の研究</div>
          {pastProjects.length === 0 ? (
            <div>過去の研究はありません</div>
          ) : (
            pastProjects.slice(0, 2).map((project) => (
              <div key={project.id} className="past-project-item">
                <div className="past-project-title">{project.title}</div>
                <div className="past-project-date">
                  {new Date(project.actualEndDate || project.targetEndDate).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      {/* クイックアクション */}
      <div className="quick-actions-row">
        <button className="quick-action-btn" onClick={onOpenAITutor}>
          <span className="qa-icon">🤖</span>
          <span className="qa-label">AI先生</span>
        </button>
        <button className="quick-action-btn" onClick={onViewRecords}>
          <span className="qa-icon">📝</span>
          <span className="qa-label">記録</span>
        </button>
        <button className="quick-action-btn" onClick={onViewLearning}>
          <span className="qa-icon">⚙️</span>
          <span className="qa-label">設定</span>
        </button>
      </div>
    </div>
  );
};

export default DashboardPage;
