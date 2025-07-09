import { useState } from 'react';
import { SignupRequest } from '../types';
import '../styles/Auth.css';

interface SignupPageProps {
  onSignup: (credentials: SignupRequest) => Promise<void>;
  onSwitchToLogin: () => void;
  isLoading?: boolean;
  error?: string;
}

function SignupPage({ onSignup, onSwitchToLogin, isLoading = false, error }: SignupPageProps) {
  const [formData, setFormData] = useState<SignupRequest & { confirmPassword: string }>({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState<Partial<SignupRequest & { confirmPassword: string }>>({});

  const validateForm = (): boolean => {
    const errors: Partial<SignupRequest & { confirmPassword: string }> = {};

    // 名前の検証
    if (!formData.name) {
      errors.name = 'お名前を入力してください';
    } else if (formData.name.length < 2) {
      errors.name = 'お名前は2文字以上で入力してください';
    }

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
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = 'パスワードは大文字・小文字・数字を含む必要があります';
    }

    // パスワード確認の検証
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'パスワード（確認）を入力してください';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'パスワードが一致しません';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (field: keyof (SignupRequest & { confirmPassword: string }), value: string) => {
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
      const { confirmPassword, ...signupData } = formData;
      await onSignup(signupData);
    } catch (error) {
      console.error('Signup failed:', error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>新規登録</h1>
          <p>夏休み自由研究AIのアカウントを作成して、楽しい研究を始めましょう！</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="name">お名前</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className={formErrors.name ? 'error' : ''}
              placeholder="例: 田中太郎"
              disabled={isLoading}
            />
            {formErrors.name && (
              <span className="field-error">{formErrors.name}</span>
            )}
          </div>

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
              placeholder="8文字以上、大文字・小文字・数字を含む"
              disabled={isLoading}
            />
            {formErrors.password && (
              <span className="field-error">{formErrors.password}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">パスワード（確認）</label>
            <input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              className={formErrors.confirmPassword ? 'error' : ''}
              placeholder="上記と同じパスワードを入力"
              disabled={isLoading}
            />
            {formErrors.confirmPassword && (
              <span className="field-error">{formErrors.confirmPassword}</span>
            )}
          </div>

          <div className="terms-agreement">
            <p className="terms-text">
              新規登録することで、
              <a href="#" className="terms-link">利用規約</a>
              および
              <a href="#" className="terms-link">プライバシーポリシー</a>
              に同意したものとみなします。
            </p>
          </div>

          <button
            type="submit"
            className="auth-button primary"
            disabled={isLoading}
          >
            {isLoading ? '登録中...' : 'アカウントを作成'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            すでにアカウントをお持ちの方は
            <button
              type="button"
              className="link-button"
              onClick={onSwitchToLogin}
              disabled={isLoading}
            >
              ログイン
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;
