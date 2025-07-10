import { UserProfile, ResearchTheme } from '../types';

const themeTemplates = {
  science: [
    {
      title: 'pH指示薬を使った酸性・アルカリ性の研究',
      description: '身近な食材を使って天然のpH指示薬を作り、様々な液体の酸性・アルカリ性を調べる実験です。',
      genre: 'experiment' as const,
      materials: ['紫キャベツ', 'レモン汁', '重曹', 'お酢', '石鹸水', 'コップ', 'スポイト'],
      steps: ['紫キャベツを煮出して指示薬を作る', '様々な液体のpHを測定', '色の変化を記録', '結果をグラフにまとめる', '考察を書く'],
      estimatedDays: 5,
      difficulty: 'medium' as const
    },
    {
      title: '磁石の性質と電磁誘導の実験',
      description: '永久磁石と電磁石の違いを調べ、電磁誘導の原理を理解する物理実験です。',
      genre: 'experiment' as const,
      materials: ['磁石', '電池', '銅線', '鉄釘', 'クリップ', 'LED', '方位磁針'],
      steps: ['永久磁石の磁力を測定', '電磁石を作製', '磁力の強さを比較', '電磁誘導実験', '結果の分析と考察'],
      estimatedDays: 7,
      difficulty: 'hard' as const
    }
  ],
  nature: [
    {
      title: '植物の光合成と環境要因の関係',
      description: '光の強さや温度などの環境要因が植物の成長にどのような影響を与えるかを調べる生物学的研究です。',
      genre: 'experiment' as const,
      materials: ['豆の種', '植木鉢', '土', '照明器具', '温度計', '定規', 'カメラ'],
      steps: ['異なる条件で種を植える', '毎日の成長を記録', '光合成量を測定', 'データをグラフ化', '環境要因の影響を分析'],
      estimatedDays: 21,
      difficulty: 'medium' as const
    },
    {
      title: '生態系における昆虫の役割調査',
      description: '地域の昆虫を観察し、食物連鎖や生態系における役割を調べる環境科学研究です。',
      genre: 'observation' as const,
      materials: ['虫眼鏡', 'カメラ', '採集網', '観察ケース', '図鑑', '記録ノート'],
      steps: ['昆虫の種類を調査', '食性と行動を観察', '生息環境を記録', '食物連鎖図を作成', '生態系の役割を考察'],
      estimatedDays: 14,
      difficulty: 'hard' as const
    }
  ],
  cooking: [
    {
      title: '発酵のメカニズムとパン作りの科学',
      description: 'パン作りを通して発酵の仕組みを学び、温度や時間が発酵に与える影響を調べます。',
      genre: 'experiment' as const,
      materials: ['強力粉', 'ドライイースト', '砂糖', '塩', '水', 'オーブン', '温度計'],
      steps: ['異なる条件でパン生地を作る', '発酵過程を観察・記録', '温度の影響を測定', 'パンの出来上がりを比較', '発酵メカニズムを考察'],
      estimatedDays: 3,
      difficulty: 'medium' as const
    }
  ],
  art: [
    {
      title: '自然素材を使った持続可能なアート制作',
      description: '環境に配慮した自然素材のみを使用してアート作品を制作し、持続可能性について考察します。',
      genre: 'research' as const,
      materials: ['枯れ葉', '木の枝', '石', '土', '天然色素', 'キャンバス'],
      steps: ['自然素材を収集', '色素の抽出実験', 'アート作品の設計', '制作過程の記録', '環境への影響を考察'],
      estimatedDays: 10,
      difficulty: 'medium' as const
    }
  ],
  technology: [
    {
      title: 'Scratchを使ったゲーム制作とプログラミング学習',
      description: 'プログラミング言語Scratchを使ってオリジナルゲームを制作し、プログラミングの基本概念を学びます。',
      genre: 'research' as const,
      materials: ['パソコン', 'Scratchソフト', '設計用紙', 'ペン'],
      steps: ['ゲームの企画・設計', 'Scratchの基本操作を習得', 'プログラム作成', 'テストとデバッグ', '改良と完成'],
      estimatedDays: 14,
      difficulty: 'medium' as const
    },
    {
      title: 'センサーを使った環境モニタリングシステム',
      description: 'Arduino等を使って温度や湿度を測定するシステムを作り、環境データを収集・分析します。',
      genre: 'experiment' as const,
      materials: ['Arduino', '温湿度センサー', 'LED', '抵抗', 'ブレッドボード', 'ジャンパーワイヤー'],
      steps: ['回路設計', 'プログラミング', 'センサーの校正', 'データ収集', '結果の分析と考察'],
      estimatedDays: 10,
      difficulty: 'hard' as const
    }
  ],
  math: [
    {
      title: '黄金比と自然界の数学的パターン',
      description: '植物や建築物に見られる黄金比や フィボナッチ数列のパターンを調べ、数学と自然の関係を探ります。',
      genre: 'research' as const,
      materials: ['定規', 'コンパス', 'カメラ', '計算機', 'グラフ用紙'],
      steps: ['身近な物の比率を測定', '黄金比の計算', 'フィボナッチ数列の確認', 'パターンの分析', '数学的関係の考察'],
      estimatedDays: 7,
      difficulty: 'medium' as const
    }
  ],
  history: [
    {
      title: '地域の歴史と文化遺産の調査研究',
      description: '自分の住む地域の歴史を調べ、文化遺産や伝統について記録・保存する社会科学研究です。',
      genre: 'research' as const,
      materials: ['カメラ', 'ICレコーダー', 'ノート', '地図', '図書館資料'],
      steps: ['文献調査', '地域住民へのインタビュー', '史跡の見学と記録', '歴史年表の作成', '地域の特色をまとめる'],
      estimatedDays: 21,
      difficulty: 'medium' as const
    }
  ]
};

export const generateMockThemes = (profile: UserProfile): ResearchTheme[] => {
  const themes: ResearchTheme[] = [];

  profile.interests.forEach((interest, index) => {
    if (themeTemplates[interest as keyof typeof themeTemplates]) {
      const templates = themeTemplates[interest as keyof typeof themeTemplates];
      if (templates.length > 0) {
        const template = templates[index % templates.length];
        themes.push({
          id: `theme-${interest}-${index}`,
          ...template
        });
      }
    }
  });

  if (themes.length < 3) {
    const defaultThemes = [
      {
        id: 'default-1',
        title: '表面張力の研究と実用性の検証',
        description: '水の表面張力の性質を調べ、日常生活での応用例を探る物理実験です。',
        genre: 'experiment' as const,
        materials: ['水', 'コップ', 'クリップ', '洗剤', 'コイン', '針'],
        steps: ['表面張力の基本実験', '様々な液体での比較', '温度による変化を測定', '実用例の調査', '結果の考察'],
        estimatedDays: 5,
        difficulty: 'medium' as const
      },
      {
        id: 'default-2',
        title: '家族史から見る地域社会の変遷',
        description: '家族の歴史を通して地域社会の変化を調べ、社会史的な視点で分析します。',
        genre: 'research' as const,
        materials: ['ノート', '録音機器', 'カメラ', '古い写真', '地図'],
        steps: ['家族へのインタビュー', '写真・資料の収集', '年表の作成', '地域史との比較', '社会変化の分析'],
        estimatedDays: 14,
        difficulty: 'medium' as const
      },
      {
        id: 'default-3',
        title: '気候変動が生物に与える影響の長期観察',
        description: '季節の変化と生物の行動や形態変化の関係を長期間観察し、気候変動の影響を考察します。',
        genre: 'observation' as const,
        materials: ['カメラ', '温度計', '湿度計', '記録ノート', '定規'],
        steps: ['観察地点の設定', '定期的な観察と記録', '気象データの収集', 'データの分析', '気候変動との関連を考察'],
        estimatedDays: 35,
        difficulty: 'hard' as const
      }
    ];

    while (themes.length < 3) {
      themes.push(defaultThemes[themes.length]);
    }
  }

  return themes.slice(0, 3);
};
