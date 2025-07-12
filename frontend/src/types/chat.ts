export interface ChatMessage {
  id: string;
  message: string;
  isAiResponse: boolean;
  timestamp: Date;
  mediaUrl?: string;
  mediaAnalysis?: string;
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  media_analysis?: string;
}

export type MessageType = 'text' | 'image' | 'audio';