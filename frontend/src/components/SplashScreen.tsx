import React, { useEffect, useState } from 'react';
import './SplashScreen.css';

interface SplashScreenProps {
  onComplete: () => void;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ onComplete }) => {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // 2.5秒後にフェードアウト開始
    const fadeTimer = setTimeout(() => {
      setFadeOut(true);
    }, 2500);

    // 3秒後にスプラッシュスクリーン終了
    const completeTimer = setTimeout(() => {
      onComplete();
    }, 3000);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  return (
    <div className={`splash-screen ${fadeOut ? 'fade-out' : ''}`}>
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