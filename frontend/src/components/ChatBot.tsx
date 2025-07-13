import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, ChatResponse } from '../types/chat';
import { chatService } from '../services/chatService';
import '../styles/ChatBot.css';

interface ChatBotProps {
  userId: string;
  projectId: string;
}

export const ChatBot: React.FC<ChatBotProps> = ({ userId, projectId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (message: string, isAiResponse: boolean, mediaUrl?: string, mediaAnalysis?: string) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      message,
      isAiResponse,
      timestamp: new Date(),
      mediaUrl,
      mediaAnalysis
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage;
    setInputMessage('');
    addMessage(userMessage, false);
    setIsLoading(true);

    try {
      const response: ChatResponse = await chatService.sendMessage(
        userId,
        projectId,
        userMessage
      );
      
      addMessage(response.message, true, undefined, response.media_analysis);
      setSuggestions(response.suggestions || []);
    } catch (error) {
      addMessage('申し訳ありません。エラーが発生しました。', true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const message = `${file.name}を送信しました。これについて教えてください。`;
    addMessage(message, false, URL.createObjectURL(file));
    setIsLoading(true);

    try {
      const response: ChatResponse = await chatService.uploadMedia(
        userId,
        projectId,
        message,
        file
      );
      
      addMessage(response.message, true, undefined, response.media_analysis);
      setSuggestions(response.suggestions || []);
    } catch (error) {
      addMessage('ファイルの処理でエラーが発生しました。', true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h3>🤖 AI先生</h3>
        <p>研究のことなら何でも聞いてね！</p>
      </div>
      
      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.isAiResponse ? 'ai-message' : 'user-message'}`}>
            <div className="message-content">
              {msg.mediaUrl && (
                <img src={msg.mediaUrl} alt="アップロード画像" className="message-image" />
              )}
              <p>{msg.message}</p>
              {msg.mediaAnalysis && (
                <div className="media-analysis">
                  <strong>画像解析結果:</strong>
                  <p>{msg.mediaAnalysis}</p>
                </div>
              )}
            </div>
            <span className="message-time">
              {msg.timestamp.toLocaleTimeString()}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="message ai-message">
            <div className="message-content">
              <p>考え中...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {suggestions.length > 0 && (
        <div className="suggestions">
          <p>こんなことも聞いてみよう:</p>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-button"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="質問を入力してください..."
          className="message-input"
        />
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept="image/*,audio/*"
          style={{ display: 'none' }}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="file-button"
          title="画像や音声を送信"
        >
          📎
        </button>
        <button
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
          className="send-button"
        >
          送信
        </button>
      </div>
    </div>
  );
};