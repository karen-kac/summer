import { useState } from "react";
import { login } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await login(email, password);
      localStorage.setItem("user", res.first_name); // 仮のセッション保存
      window.location.href = "/";
    } catch (err: any) {
      setError(err.response?.data?.detail || "ログインに失敗しました");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>ログイン</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="メールアドレス" required />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="パスワード" required />
      <button type="submit">ログイン</button>
    </form>
  );
}
