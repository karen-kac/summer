import { ResearchProject, UserStats, Achievement } from '../types';

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
