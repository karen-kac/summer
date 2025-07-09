import { useState } from 'react';
import { LoginRequest } from '../types';
import '../styles/Auth.css';

interface LoginPageProps {
  onLogin: (credentials: LoginRequest) => Promise<void>;
  onSwitchToSignup: () => void;
  isLoading?: boolean;
  error?: string;
}

function LoginPage({ onLogin, onSwitchToSignup, isLoading = false, error }: LoginPageProps) {
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: ''
  });
  const [formErrors, setFormErrors] = useState<Partial<LoginRequest>>({});

  const validateForm = (): boolean => {
    const errors: Partial<LoginRequest> = {};

    // メールアドレスの検証
    if (!formData.email) {
      errors.email = 'メールアドレスを入力してください';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = '有効なメールアドレスを入力してください';
    }

    // パスワードの検証
    if (!formData.password) {
      errors.password = 'パスワードを入力してください';
    } else if (formData.password.length < 8) {
      errors.password = 'パスワードは8文字以上で入力してください';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (field: keyof LoginRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // エラーをクリア
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await onLogin(formData);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>ログイン</h1>
          <p>夏休み自由研究AIにログインして、あなたの研究を始めましょう！</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className={formErrors.email ? 'error' : ''}
              placeholder="例: tanaka@example.com"
              disabled={isLoading}
            />
            {formErrors.email && (
              <span className="field-error">{formErrors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className={formErrors.password ? 'error' : ''}
              placeholder="8文字以上で入力してください"
              disabled={isLoading}
            />
            {formErrors.password && (
              <span className="field-error">{formErrors.password}</span>
            )}
          </div>

          <button
            type="submit"
            className="auth-button primary"
            disabled={isLoading}
          >
            {isLoading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            アカウントをお持ちでない方は
            <button
              type="button"
              className="link-button"
              onClick={onSwitchToSignup}
              disabled={isLoading}
            >
              新規登録
            </button>
          </p>
          <button type="button" className="link-button">
            パスワードを忘れた方はこちら
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
