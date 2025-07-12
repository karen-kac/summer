import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import '../styles/Settings.css';
import '../styles/Common.css';

interface SettingsPageProps {
  onBackToDashboard: () => void;
}

interface ParentContact {
  name: string;
  relationship: string;
  lineConnected: boolean;
  lineUserId?: string;
  notificationSettings: {
    dailyProgress: boolean;
    completedTasks: boolean;
    achievements: boolean;
    weeklyReport: boolean;
  };
}

const SettingsPage: React.FC<SettingsPageProps> = ({ onBackToDashboard }) => {
  const {
    authState,
    lineConnectionStatus,
    lineConnectionLoading,
    lineConnectionError,
    loadLineConnectionStatus,
    connectToLine,
    disconnectFromLine
  } = useApp();

  const [activeTab, setActiveTab] = useState<string>('profile');
  const [parentContacts, setParentContacts] = useState<ParentContact[]>([
    {
      name: '',
      relationship: 'parent',
      lineConnected: false,
      notificationSettings: {
        dailyProgress: true,
        completedTasks: true,
        achievements: true,
        weeklyReport: true,
      }
    }
  ]);

  // ユーザーログイン時にLINE連携状態を取得
  useEffect(() => {
    if (authState.user?.id) {
      loadLineConnectionStatus(authState.user.id);
    }
  }, [authState.user?.id, loadLineConnectionStatus]);

  const [appSettings, setAppSettings] = useState({
    notifications: {
      dailyReminder: true,
      taskDeadline: true,
      achievements: true,
    },
    privacy: {
      shareProgress: false,
      analyticsOptIn: true,
    },
    accessibility: {
      fontSize: 'medium',
      colorContrast: 'normal',
    }
  });

  const handleLINEConnect = async () => {
    if (!authState.user?.id) {
      alert('ユーザー情報が見つかりません。もう一度ログインしてください。');
      return;
    }

    try {
      // 実際のLINE連携では、LINE Login APIを使用してユーザーIDを取得
      // ここではデモ用にランダムなLINE User IDを生成
      const demoLineUserId = `U${Math.random().toString(36).substr(2, 32)}`;

      // LINE Bot友達追加URLを生成（実際の実装では環境変数から取得）
      const lineConnectUrl = `https://line.me/R/ti/p/@your_bot_id`;

      // LINE友達追加ページを開く
      window.open(lineConnectUrl, '_blank');

      // 実際の連携処理
      const success = await connectToLine(authState.user.id, demoLineUserId);

      if (success) {
        alert('LINE連携が完了しました！これからLINEで進捗通知をお届けします。');
      } else {
        alert('LINE連携に失敗しました。もう一度お試しください。');
      }
    } catch (error) {
      console.error('LINE連携エラー:', error);
      alert('LINE連携中にエラーが発生しました。もう一度お試しください。');
    }
  };

  const handleLINEDisconnect = async () => {
    if (!authState.user?.id) {
      alert('ユーザー情報が見つかりません。');
      return;
    }

    try {
      const success = await disconnectFromLine(authState.user.id);

      if (success) {
        alert('LINE連携を解除しました。');
      } else {
        alert('LINE連携解除に失敗しました。もう一度お試しください。');
      }
    } catch (error) {
      console.error('LINE連携解除エラー:', error);
      alert('LINE連携解除中にエラーが発生しました。');
    }
  };

  const addParentContact = () => {
    setParentContacts([...parentContacts, {
      name: '',
      relationship: 'parent',
      lineConnected: false,
      notificationSettings: {
        dailyProgress: true,
        completedTasks: true,
        achievements: true,
        weeklyReport: true,
      }
    }]);
  };

  const removeParentContact = (index: number) => {
    if (parentContacts.length > 1) {
      const newContacts = parentContacts.filter((_, i) => i !== index);
      setParentContacts(newContacts);
    }
  };

  const handleParentContactChange = (index: number, field: string, value: any) => {
    const newContacts = [...parentContacts];
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      newContacts[index] = {
        ...newContacts[index],
        [parent]: {
          ...(newContacts[index] as any)[parent],
          [child]: value
        }
      };
    } else {
      newContacts[index] = {
        ...newContacts[index],
        [field]: value
      };
    }
    setParentContacts(newContacts);
  };

  const handleAppSettingChange = (category: string, setting: string, value: any) => {
    setAppSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [setting]: value
      }
    }));
  };

  const exportData = () => {
    // ユーザーデータをJSONファイルとしてエクスポート
    const data = {
      exportDate: new Date().toISOString(),
      userProfile: {}, // 実際の実装では現在のユーザープロフィールを含める
      projects: [], // プロジェクトデータ
      records: [], // 記録データ
      settings: appSettings
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summer_research_data_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const deleteAllData = () => {
    if (window.confirm('本当にすべてのデータを削除しますか？この操作は取り消せません。')) {
      if (window.confirm('最終確認です。すべての研究データ、記録、設定が削除されます。続行しますか？')) {
        // 実際の実装では、すべてのユーザーデータを削除
        alert('データ削除機能は現在開発中です。');
      }
    }
  };

  const renderProfileTab = () => (
    <div className="settings-section">
      <h3>👤 プロフィール設定</h3>
      <div className="setting-item">
        <label>名前</label>
        <input type="text" placeholder="あなたの名前" />
      </div>
      <div className="setting-item">
        <label>学年</label>
        <select>
          <option value="elementary1">小学1年生</option>
          <option value="elementary2">小学2年生</option>
          <option value="elementary3">小学3年生</option>
          <option value="elementary4">小学4年生</option>
          <option value="elementary5">小学5年生</option>
          <option value="elementary6">小学6年生</option>
          <option value="junior1">中学1年生</option>
          <option value="junior2">中学2年生</option>
          <option value="junior3">中学3年生</option>
        </select>
      </div>
      <div className="setting-item">
        <label>興味のある分野</label>
        <div className="interest-tags">
          {['science', 'nature', 'animals', 'cooking', 'art', 'sports', 'music', 'history', 'technology', 'math'].map(interest => (
            <label key={interest} className="interest-tag">
              <input type="checkbox" />
              <span>{interest}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  const renderParentTab = () => (
    <div className="settings-section">
      <h3>👨‍👩‍👧‍👦 LINE連携</h3>
      <p className="section-description">
        お子様の研究進捗をLINEで受け取ることができます
      </p>

      {lineConnectionError && (
        <div className="error-message">
          {lineConnectionError}
        </div>
      )}

      <div className="line-connection-card">
        <div className="line-status">
          <h5>📱 LINE連携状態</h5>
          {lineConnectionLoading ? (
            <div className="loading-status">
              <span className="status-indicator loading">⏳ 読み込み中...</span>
            </div>
          ) : lineConnectionStatus?.is_connected ? (
            <div className="connected-status">
              <span className="status-indicator connected">✅ 連携済み</span>
              {lineConnectionStatus.connection?.display_name && (
                <p className="connected-info">
                  連携アカウント: {lineConnectionStatus.connection.display_name}
                </p>
              )}
              <button
                className="disconnect-btn"
                onClick={handleLINEDisconnect}
                disabled={lineConnectionLoading}
              >
                連携解除
              </button>
            </div>
          ) : (
            <div className="disconnected-status">
              <span className="status-indicator disconnected">❌ 未連携</span>
              <p className="connection-info">
                LINE連携すると、研究の進捗や応援メッセージを受け取ることができます
              </p>
              <button
                className="connect-btn"
                onClick={handleLINEConnect}
                disabled={lineConnectionLoading}
              >
                {lineConnectionLoading ? '連携中...' : 'LINE連携する'}
              </button>
            </div>
          )}
        </div>

        {lineConnectionStatus?.is_connected && (
          <div className="notification-settings">
            <h6>📬 受け取る通知</h6>
            <div className="notification-info">
              <div className="notification-item">
                <span className="notification-icon">📊</span>
                <div className="notification-details">
                  <strong>研究進捗レポート</strong>
                  <p>研究が進んだときに進捗状況をお知らせします</p>
                </div>
              </div>
              <div className="notification-item">
                <span className="notification-icon">🎉</span>
                <div className="notification-details">
                  <strong>応援メッセージ</strong>
                  <p>タスクを完了したときに励ましのメッセージを送ります</p>
                </div>
              </div>
              <div className="notification-item">
                <span className="notification-icon">🌅</span>
                <div className="notification-details">
                  <strong>日次リマインダー</strong>
                  <p>毎朝、今日の研究予定をお知らせします</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {!lineConnectionStatus?.is_connected && (
          <div className="line-setup-guide">
            <h6>💡 LINE連携の手順</h6>
            <ol className="setup-steps">
              <li>上の「LINE連携する」ボタンをクリック</li>
              <li>開かれたページで「夏休み自由研究AI」を友達追加</li>
              <li>LINEで「連携完了」のメッセージが届いたら設定完了！</li>
            </ol>
          </div>
        )}
      </div>

      {/* 既存の保護者連絡先機能は残しておく（将来的な拡張用） */}
      <div className="legacy-contacts" style={{display: 'none'}}>
        {parentContacts.map((contact, index) => (
          <div key={index} className="parent-contact-card">
            <div className="contact-header">
              <h4>保護者 {index + 1}</h4>
              {parentContacts.length > 1 && (
                <button
                  className="remove-contact-btn"
                  onClick={() => removeParentContact(index)}
                >
                  削除
                </button>
              )}
            </div>

            <div className="contact-info">
              <div className="setting-item">
                <label>お名前</label>
                <input
                  type="text"
                  placeholder="保護者の方のお名前"
                  value={contact.name}
                  onChange={(e) => handleParentContactChange(index, 'name', e.target.value)}
                />
              </div>

              <div className="setting-item">
                <label>続柄</label>
                <select
                  value={contact.relationship}
                  onChange={(e) => handleParentContactChange(index, 'relationship', e.target.value)}
                >
                  <option value="parent">両親</option>
                  <option value="father">父親</option>
                  <option value="mother">母親</option>
                  <option value="grandparent">祖父母</option>
                  <option value="guardian">保護者</option>
                </select>
              </div>
            </div>

            {contact.lineConnected && (
              <div className="notification-settings">
                <h6>通知設定</h6>
                <div className="notification-options">
                  <label className="notification-option">
                    <input
                      type="checkbox"
                      checked={contact.notificationSettings.dailyProgress}
                      onChange={(e) => handleParentContactChange(index, 'notificationSettings.dailyProgress', e.target.checked)}
                    />
                    <span>日次進捗レポート</span>
                  </label>
                  <label className="notification-option">
                    <input
                      type="checkbox"
                      checked={contact.notificationSettings.completedTasks}
                      onChange={(e) => handleParentContactChange(index, 'notificationSettings.completedTasks', e.target.checked)}
                    />
                    <span>タスク完了通知</span>
                  </label>
                  <label className="notification-option">
                    <input
                      type="checkbox"
                      checked={contact.notificationSettings.achievements}
                      onChange={(e) => handleParentContactChange(index, 'notificationSettings.achievements', e.target.checked)}
                    />
                    <span>実績達成通知</span>
                  </label>
                  <label className="notification-option">
                    <input
                      type="checkbox"
                      checked={contact.notificationSettings.weeklyReport}
                      onChange={(e) => handleParentContactChange(index, 'notificationSettings.weeklyReport', e.target.checked)}
                    />
                    <span>週間レポート</span>
                  </label>
                </div>
              </div>
            )}
          </div>
        ))}

        <button className="add-contact-btn" onClick={addParentContact}>
          ➕ 保護者を追加
        </button>
      </div>
    </div>
  );

  const renderNotificationTab = () => (
    <div className="settings-section">
      <h3>🔔 通知設定</h3>
      <div className="notification-group">
        <h4>アプリ通知</h4>
        <label className="notification-option">
          <input
            type="checkbox"
            checked={appSettings.notifications.dailyReminder}
            onChange={(e) => handleAppSettingChange('notifications', 'dailyReminder', e.target.checked)}
          />
          <span>毎日のリマインダー</span>
        </label>
        <label className="notification-option">
          <input
            type="checkbox"
            checked={appSettings.notifications.taskDeadline}
            onChange={(e) => handleAppSettingChange('notifications', 'taskDeadline', e.target.checked)}
          />
          <span>タスク期限のお知らせ</span>
        </label>
        <label className="notification-option">
          <input
            type="checkbox"
            checked={appSettings.notifications.achievements}
            onChange={(e) => handleAppSettingChange('notifications', 'achievements', e.target.checked)}
          />
          <span>実績達成のお祝い</span>
        </label>
      </div>
    </div>
  );

  const renderPrivacyTab = () => (
    <div className="settings-section">
      <h3>🔒 プライバシー設定</h3>
      <div className="privacy-group">
        <label className="notification-option">
          <input
            type="checkbox"
            checked={appSettings.privacy.shareProgress}
            onChange={(e) => handleAppSettingChange('privacy', 'shareProgress', e.target.checked)}
          />
          <span>進捗情報の共有を許可</span>
        </label>
        <label className="notification-option">
          <input
            type="checkbox"
            checked={appSettings.privacy.analyticsOptIn}
            onChange={(e) => handleAppSettingChange('privacy', 'analyticsOptIn', e.target.checked)}
          />
          <span>サービス改善のためのデータ分析に協力</span>
        </label>
      </div>
    </div>
  );

  const renderDataTab = () => (
    <div className="settings-section">
      <h3>💾 データ管理</h3>
      <div className="data-actions">
        <div className="data-action-card">
          <h4>📤 データエクスポート</h4>
          <p>研究データや記録をバックアップファイルとしてダウンロードできます</p>
          <button className="export-btn" onClick={exportData}>
            データをエクスポート
          </button>
        </div>

        <div className="data-action-card danger">
          <h4>🗑️ データ削除</h4>
          <p>すべての研究データ、記録、設定を完全に削除します（復元不可）</p>
          <button className="delete-btn" onClick={deleteAllData}>
            すべてのデータを削除
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="settings-container">
      <div className="settings-header">
        <button className="back-btn" onClick={onBackToDashboard}>
          ← もどる
        </button>
        <h1 className="page-title">⚙️ 設定</h1>
      </div>

      <div className="settings-content">
        <div className="settings-tabs">
          <button
            className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            👤 プロフィール
          </button>
          <button
            className={`tab-btn ${activeTab === 'parent' ? 'active' : ''}`}
            onClick={() => setActiveTab('parent')}
          >
            👨‍👩‍👧‍👦 保護者連携
          </button>
          <button
            className={`tab-btn ${activeTab === 'notification' ? 'active' : ''}`}
            onClick={() => setActiveTab('notification')}
          >
            🔔 通知
          </button>
          <button
            className={`tab-btn ${activeTab === 'privacy' ? 'active' : ''}`}
            onClick={() => setActiveTab('privacy')}
          >
            🔒 プライバシー
          </button>
          <button
            className={`tab-btn ${activeTab === 'data' ? 'active' : ''}`}
            onClick={() => setActiveTab('data')}
          >
            💾 データ管理
          </button>
        </div>

        <div className="settings-tab-content">
          {activeTab === 'profile' && renderProfileTab()}
          {activeTab === 'parent' && renderParentTab()}
          {activeTab === 'notification' && renderNotificationTab()}
          {activeTab === 'privacy' && renderPrivacyTab()}
          {activeTab === 'data' && renderDataTab()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
