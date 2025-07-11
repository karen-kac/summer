import React from 'react';
import '../styles/Usage.css';
import '../styles/Common.css';

interface UsagePageProps {
  onBackToDashboard: () => void;
}

const UsagePage: React.FC<UsagePageProps> = ({ onBackToDashboard }) => {
  return (
    <div className="usage-container">
      <div className="usage-header">
        <button className="back-btn" onClick={onBackToDashboard}>
          ← もどる
        </button>
        <h1 className="page-title">🔍 使い方</h1>
      </div>

      <div className="usage-content">
        <div className="usage-section">
          <div className="section-header">
            <span className="section-icon">🚀</span>
            <h2>自由研究のテーマを決めよう</h2>
          </div>
          <div className="step-list">
            <div className="step-item">
              <span className="step-number">1</span>
              <div className="step-content">
                <h3>「自由研究のテーマを決めよう！」ボタンを押そう</h3>
                <p>ダッシュボードの一番上にある大きなボタンをクリックします。</p>
              </div>
            </div>
            <div className="step-item">
              <span className="step-number">2</span>
              <div className="step-content">
                <h3>あなたのことも教えてね</h3>
                <p>学年や好きなこと、性格などを選んでください。</p>
              </div>
            </div>
            <div className="step-item">
              <span className="step-number">3</span>
              <div className="step-content">
                <h3>AIがテーマを提案してくれます</h3>
                <p>あなたにぴったりの研究テーマをAIが考えてくれます。</p>
              </div>
            </div>
          </div>
        </div>

        <div className="usage-section">
          <div className="section-header">
            <span className="section-icon">🔬</span>
            <h2>研究を進めよう</h2>
          </div>
          <div className="step-list">
            <div className="step-item">
              <span className="step-number">1</span>
              <div className="step-content">
                <h3>研究プランを見よう</h3>
                <p>どんな順番で研究するかが書いてあります。</p>
              </div>
            </div>
            <div className="step-item">
              <span className="step-number">2</span>
              <div className="step-content">
                <h3>毎日少しずつやろう</h3>
                <p>「続きを見る」ボタンで研究を続けましょう。</p>
              </div>
            </div>
            <div className="step-item">
              <span className="step-number">3</span>
              <div className="step-content">
                <h3>記録を残そう</h3>
                <p>分かったことや感じたことを書きとめておきましょう。</p>
              </div>
            </div>
          </div>
        </div>

        <div className="usage-section">
          <div className="section-header">
            <span className="section-icon">📝</span>
            <h2>記録カレンダーを使おう</h2>
          </div>
          <div className="feature-explanation">
            <p>毎日の研究の様子をカレンダーで確認できます。</p>
            <ul className="feature-list">
              <li>✅ 今日何をしたか記録</li>
              <li>📸 写真も保存できる</li>
              <li>📊 研究の進捗が分かる</li>
              <li>🏆 ポイントがもらえる</li>
            </ul>
          </div>
        </div>

        <div className="tips-section">
          <div className="section-header">
            <span className="section-icon">💡</span>
            <h2>上手く使うコツ</h2>
          </div>
          <div className="tips-grid">
            <div className="tip-card">
              <span className="tip-icon">⏰</span>
              <h3>毎日ちょっとずつ</h3>
              <p>10分でもいいから、毎日続けることが大切です。</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">📋</span>
              <h3>記録を忘れずに</h3>
              <p>面白いことがあったら、すぐにメモしましょう。</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">👨‍👩‍👧‍👦</span>
              <h3>お家の人とやろう</h3>
              <p>分からないことがあったら、お家の人に聞いてみましょう。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UsagePage;
