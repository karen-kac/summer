import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const register = async (data: {
  last_name: string;
  first_name: string;
  email: string;
  password: string;
}) => {
  return axios.post(`${API_URL}/register`, data);
};

export const login = async (email: string, password: string) => {
  const response = await axios.post(`${API_URL}/login`, { email, password });
  return response.data;
};
