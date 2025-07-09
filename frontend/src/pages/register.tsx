import { useState } from "react";
import { register } from "../api/auth";

export default function Register() {
  const [form, setForm] = useState({ last_name: "", first_name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password.length < 8) {
      setError("パスワードは8文字以上にしてください。");
      return;
    }
    try {
      await register(form);
      window.location.href = "/login";
    } catch (err: any) {
      setError(err.response?.data?.detail || "登録に失敗しました");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>会員登録</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input name="last_name" value={form.last_name} onChange={handleChange} placeholder="名字" required />
      <input name="first_name" value={form.first_name} onChange={handleChange} placeholder="名前" required />
      <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="メールアドレス" required />
      <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="パスワード" required />
      <button type="submit">登録</button>
    </form>
  );
}
