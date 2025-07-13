import { ChatResponse, MessageType } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const chatService = {
  async sendMessage(
    userId: string,
    projectId: string,
    message: string,
    messageType: MessageType = 'text',
    mediaUrl?: string
  ): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        project_id: projectId,
        message,
        message_type: messageType,
        media_url: mediaUrl
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  },

  async uploadMedia(
    userId: string,
    projectId: string,
    message: string,
    file: File
  ): Promise<ChatResponse> {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('project_id', projectId);
    formData.append('message', message);
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/chat/upload-media`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
};
