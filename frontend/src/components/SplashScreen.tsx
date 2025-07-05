import React, { useEffect, useState } from 'react';
import './SplashScreen.css';

interface SplashScreenProps {
  onComplete: () => void;
  fadeDelay?: number; // フェードアウト開始までの時間（ミリ秒）
  completeDelay?: number; // スプラッシュスクリーン終了までの時間（ミリ秒）
}

// デフォルトの時間設定を定数として定義
const DEFAULT_FADE_DELAY = 2500; // 2.5秒後にフェードアウト開始
const DEFAULT_COMPLETE_DELAY = 3000; // 3秒後にスプラッシュスクリーン終了

const SplashScreen: React.FC<SplashScreenProps> = ({
  onComplete,
  fadeDelay = DEFAULT_FADE_DELAY,
  completeDelay = DEFAULT_COMPLETE_DELAY
}) => {
  const [fadeOut, setFadeOut] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // フェードアウト開始
    const fadeTimer = setTimeout(() => {
      setFadeOut(true);
    }, fadeDelay);

    // スプラッシュスクリーン終了
    const completeTimer = setTimeout(() => {
      setIsVisible(false);
      onComplete();
    }, completeDelay);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete, fadeDelay, completeDelay]);

  // コンポーネントが非表示になったらDOMから削除
  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`splash-screen ${fadeOut ? 'fade-out' : ''}`}
      aria-hidden={!isVisible}
      role="presentation"
    >
      <div className="splash-content">
        <div className="main-container">
          <div className="image-section">
            <img
              src="/summer-removebg-preview.png"
              alt="自由研究アイコン"
              className="main-image"
            />
          </div>

          <div className="content-section">
            <h1 className="splash-title">
              <span className="title-line">夏休み</span>
              <span className="title-line">自由研究AI</span>
            </h1>
            <div className="splash-subtitle">
              AIがあなたにぴったりの自由研究テーマを提案
            </div>
          </div>
        </div>
      </div>

      <div className="splash-background">
      </div>
    </div>
  );
};

export default SplashScreen;
