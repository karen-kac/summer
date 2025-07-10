import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const AppLayout: React.FC = () => {
  const { authState, handleLogout } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogoutClick = () => {
    handleLogout();
    navigate('/login');
  };

  const isDashboard = location.pathname === '/dashboard';

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-text">
            <h1>夏休み自由研究AI</h1>
            <p>AIがあなたにぴったりの自由研究テーマを提案します！（小学生〜中学生対象）</p>
          </div>
          {authState.isAuthenticated && (
            <div className="header-actions">
              <span className="user-name">
                {authState.user?.name}さん
              </span>
              <button
                className="logout-button"
                onClick={handleLogoutClick}
                title="ログアウト"
              >
                ログアウト
              </button>
            </div>
          )}
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      {/* フローティングダッシュボードボタン（ダッシュボード以外で表示） */}
      {!isDashboard && (
        <button
          className="floating-dashboard-btn"
          onClick={() => navigate('/dashboard')}
          title="ダッシュボードに戻る"
        >
          🏠
        </button>
      )}
    </div>
  );
};

export default AppLayout;
