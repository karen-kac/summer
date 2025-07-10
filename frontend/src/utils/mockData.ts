import { ResearchProject, UserStats, Achievement, Record, Schedule } from '../types';

// モックアクティブプロジェクト
export const mockActiveProjects: ResearchProject[] = [
  {
    id: 'project-1',
    userId: 'user-1',
    themeId: 'theme-1',
    title: '植物の成長観察',
    description: '豆の成長を毎日記録する実験',
    genre: 'observation',
    status: 'in_progress',
    startDate: '2025-07-01',
    targetEndDate: '2025-07-21',
    customMaterials: [],
    customSteps: [],
    progressPercentage: 65,
    createdAt: '2025-07-01',
    updatedAt: '2025-07-04'
  }
];

// モックユーザー統計
export const mockUserStats: UserStats = {
  totalPoints: 1250,
  level: 5,
  completedProjects: 2,
  currentStreak: 7,
  totalRecords: 23,
  totalPhotos: 15,
  totalExperiments: 8
};

// モック最近の実績
export const mockRecentAchievements: Achievement[] = [
  {
    id: 'achievement-1',
    name: '初回観察完了',
    description: '初めての観察記録を作成しました',
    icon: '🔬',
    category: 'observation',
    requirements: {},
    points: 100,
    isActive: true,
    createdAt: '2025-07-01'
  },
  {
    id: 'achievement-2',
    name: '7日連続記録',
    description: '7日間連続で記録を作成しました',
    icon: '🔥',
    category: 'consistency',
    requirements: {},
    points: 200,
    isActive: true,
    createdAt: '2025-07-02'
  }
];

// モック過去のプロジェクト
export const mockPastProjects: ResearchProject[] = [
  {
    id: 'past-project-1',
    userId: 'user-1',
    themeId: 'theme-past-1',
    title: '水の表面張力実験',
    description: '水の表面張力について調べる実験',
    genre: 'experiment',
    status: 'completed',
    startDate: '2024-08-01',
    targetEndDate: '2024-08-15',
    actualEndDate: '2024-08-14',
    customMaterials: ['水', 'コップ', 'クリップ'],
    customSteps: [],
    progressPercentage: 100,
    createdAt: '2024-08-01',
    updatedAt: '2024-08-14'
  },
  {
    id: 'past-project-2',
    userId: 'user-1',
    themeId: 'theme-past-2',
    title: '植物の光合成実験',
    description: '光の強さと植物の成長の関係を調べる',
    genre: 'experiment',
    status: 'completed',
    startDate: '2024-07-15',
    targetEndDate: '2024-08-05',
    actualEndDate: '2024-08-03',
    customMaterials: ['豆', '植木鉢', 'LEDライト'],
    customSteps: [],
    progressPercentage: 100,
    createdAt: '2024-07-15',
    updatedAt: '2024-08-03'
  }
];

// 記録のモックデータ
export const mockRecords: Record[] = [
  {
    id: 'record-1',
    projectId: 'project-1',
    recordType: 'observation',
    title: '植物の成長観察',
    content: '今日はアサガオの芽が1cm伸びていました。葉っぱも少し大きくなったように見えます。',
    data: { height: 5.2, leafCount: 4 },
    recordDate: '2024-12-10T14:30:00Z',
    weatherInfo: { condition: '晴れ', temperature: 22 },
    createdAt: '2024-12-10T14:30:00Z',
    updatedAt: '2024-12-10T14:30:00Z'
  },
  {
    id: 'record-2',
    projectId: 'project-1',
    recordType: 'observation',
    title: '植物の成長観察',
    content: 'アサガオの高さが6.5cmになりました。新しい葉っぱが出てきそうです。',
    data: { height: 6.5, leafCount: 4 },
    recordDate: '2024-12-11T15:00:00Z',
    weatherInfo: { condition: '曇り', temperature: 18 },
    createdAt: '2024-12-11T15:00:00Z',
    updatedAt: '2024-12-11T15:00:00Z'
  },
  {
    id: 'record-3',
    projectId: 'past-project-1',
    recordType: 'experiment',
    title: '実験結果の記録',
    content: '氷が完全に溶けるまでに35分かかりました。室温は24度でした。',
    data: { meltingTime: 35, roomTemperature: 24 },
    recordDate: '2024-12-09T13:20:00Z',
    createdAt: '2024-12-09T13:20:00Z',
    updatedAt: '2024-12-09T13:20:00Z'
  },
  {
    id: 'record-4',
    projectId: 'project-1',
    recordType: 'note',
    title: 'メモ',
    content: '明日は雨の予報なので、植物を室内に入れるかどうか検討する必要がある。',
    data: {},
    recordDate: '2024-12-12T19:00:00Z',
    createdAt: '2024-12-12T19:00:00Z',
    updatedAt: '2024-12-12T19:00:00Z'
  }
];

// スケジュールのモックデータ
export const mockSchedules: Schedule[] = [
  {
    id: 'schedule-1',
    projectId: 'project-1',
    eventType: 'task',
    title: '植物の水やり',
    description: 'アサガオに水をあげましょう',
    scheduledAt: '2024-12-10T08:00:00Z',
    isCompleted: true,
    reminderSent: true,
    reminderSettings: {},
    createdAt: '2024-12-10T07:00:00Z',
    updatedAt: '2024-12-10T08:15:00Z'
  },
  {
    id: 'schedule-2',
    projectId: 'project-1',
    eventType: 'observation',
    title: '成長測定',
    description: '植物の高さと葉っぱの数を測定する',
    scheduledAt: '2024-12-11T15:00:00Z',
    isCompleted: true,
    reminderSent: true,
    reminderSettings: {},
    createdAt: '2024-12-10T15:00:00Z',
    updatedAt: '2024-12-11T15:30:00Z'
  },
  {
    id: 'schedule-3',
    projectId: 'past-project-2',
    eventType: 'task',
    title: '実験器具の準備',
    description: '明日の実験のために器具を準備する',
    scheduledAt: '2024-12-12T16:00:00Z',
    isCompleted: false,
    reminderSent: false,
    reminderSettings: {},
    createdAt: '2024-12-12T10:00:00Z',
    updatedAt: '2024-12-12T10:00:00Z'
  },
  {
    id: 'schedule-4',
    projectId: 'project-1',
    eventType: 'reminder',
    title: '観察の時間',
    description: '今日の植物観察を忘れずに',
    scheduledAt: '2024-12-13T14:00:00Z',
    isCompleted: false,
    reminderSent: false,
    reminderSettings: {},
    createdAt: '2024-12-12T20:00:00Z',
    updatedAt: '2024-12-12T20:00:00Z'
  }
];
