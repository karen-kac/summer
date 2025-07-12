import React from 'react';
import '../styles/Help.css';
import '../styles/Common.css';

interface HelpPageProps {
  onBack: () => void;
}

interface HelpSection {
  id: string;
  title: string;
  content: string;
  icon: string;
}

const HelpPage: React.FC<HelpPageProps> = ({ onBack }) => {
  const helpSections: HelpSection[] = [
    {
      id: 'getting-started',
      title: '🚀 はじめに',
      icon: '🌟',
      content: 'この夏の自由研究アプリは、AIと一緒に楽しく研究テーマを考えて、研究を進めていくことができるアプリです。あなたの興味や学年に合わせて、ぴったりのテーマを提案します！'
    },
    {
      id: 'theme-selection',
      title: '🎯 テーマの決め方',
      icon: '🔍',
      content: '①「自由研究のテーマを決めよう！」ボタンをクリック\n②あなたの学年や興味のあることを選択\n③AIがあなたにぴったりのテーマを3つ提案\n④気に入ったテーマを選んで研究スタート！'
    },
    {
      id: 'project-progress',
      title: '📚 研究の進め方',
      icon: '✅',
      content: '研究は複数のステップに分かれています。\n①テーマについて調べる\n②実験や観察をする\n③結果をまとめる\n④発表資料を作る\n\n各ステップで写真を撮ったり、メモを残したりして記録を残しましょう！'
    },
    {
      id: 'record-keeping',
      title: '📝 記録カレンダー',
      icon: '📅',
      content: '記録カレンダーでは、研究の進捗を日々記録できます。\n・実験の結果を写真付きで記録\n・観察したことをメモとして保存\n・研究の予定を立てる\n\n記録をつけることで、研究がより深くなります！'
    },
    {
      id: 'dashboard',
      title: '🏠 ダッシュボード',
      icon: '📊',
      content: 'ダッシュボードでは以下のことができます：\n・進行中の研究を確認\n・今日のタスクをチェック\n・過去の研究を振り返り\n・実績やレベルを確認\n\n研究の全体の状況を把握できる場所です！'
    },
    {
      id: 'tips',
      title: '💡 研究のコツ',
      icon: '🎓',
      content: '・毎日少しずつでも記録をつけよう\n・わからないことは大人に聞いてみよう\n・実験は安全に気をつけて行おう\n・失敗も大切な発見！記録に残そう\n・写真をたくさん撮って記録を残そう'
    }
  ];

  const faqItems = [
    {
      question: 'テーマを変更したい場合はどうすればいいですか？',
      answer: 'ダッシュボードから「自由研究のテーマを決めよう！」ボタンを押して、新しいテーマを作成できます。'
    },
    {
      question: '写真はどこに保存されますか？',
      answer: '撮影した写真は安全にクラウドに保存され、あなたの研究記録として使用できます。'
    },
    {
      question: '研究が終わったらどうすればいいですか？',
      answer: '全てのステップを完了すると、自動的に「完了済み」になり、過去の研究として保存されます。'
    },
    {
      question: 'アプリの使い方がわからない時は？',
      answer: 'この画面をいつでも見返すことができます。ダッシュボードの「使い方」ボタンからアクセスできます。'
    }
  ];

  return (
    <div className="help-page">
      <div className="help-header">
        <div className="help-header-content">
          <h1>📖 アプリの使い方</h1>
          <p>夏の自由研究を楽しく進めるためのガイドです</p>
        </div>
        <button className="back-btn" onClick={onBack}>
          ← ダッシュボードに戻る
        </button>
      </div>

      <div className="help-content">
        {/* 基本的な使い方セクション */}
        <section className="help-section">
          <h2>📚 基本的な使い方</h2>
          <div className="help-cards-grid">
            {helpSections.map((section) => (
              <div key={section.id} className="help-card">
                <div className="help-card-header">
                  <span className="help-card-icon">{section.icon}</span>
                  <h3>{section.title}</h3>
                </div>
                <div className="help-card-content">
                  {section.content.split('\n').map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* よくある質問セクション */}
        <section className="help-section">
          <h2>❓ よくある質問</h2>
          <div className="faq-list">
            {faqItems.map((item, index) => (
              <div key={index} className="faq-item">
                <div className="faq-question">
                  <span className="faq-icon">Q.</span>
                  <span className="faq-text">{item.question}</span>
                </div>
                <div className="faq-answer">
                  <span className="faq-icon">A.</span>
                  <span className="faq-text">{item.answer}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* お困りの時セクション */}
        <section className="help-section">
          <h2>🆘 お困りの時は</h2>
          <div className="support-card">
            <div className="support-content">
              <h3>📞 サポートについて</h3>
              <p>アプリの使い方でわからないことがあれば、以下の方法でサポートを受けることができます：</p>
              <ul>
                <li>📧 保護者の方にヘルプをお願いする</li>
                <li>📖 この使い方ページを見返す</li>
                <li>🔄 アプリを再起動してみる</li>
              </ul>
              <div className="support-note">
                <span className="support-note-icon">💡</span>
                <span>困った時は無理をせず、大人の人に相談しましょう！</span>
              </div>
            </div>
          </div>
        </section>

        {/* アプリの特徴セクション */}
        <section className="help-section">
          <h2>✨ このアプリの特徴</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h4>AI powered</h4>
              <p>最新のAI技術があなたの研究をサポート</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h4>簡単操作</h4>
              <p>直感的でわかりやすいインターフェース</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h4>進捗管理</h4>
              <p>研究の進み具合をビジュアルで確認</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏆</div>
              <h4>やる気UP</h4>
              <p>実績やレベルシステムで楽しく継続</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HelpPage;
