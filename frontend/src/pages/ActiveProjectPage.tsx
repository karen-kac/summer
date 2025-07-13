import React, { useState, useEffect } from 'react';
import { ResearchProject, ResearchStep, Genre, AIResearchStep, CreateRecordRequest } from '../types';
import { themeApi, recordApi } from '../services/api';
import { useApp } from '../context/AppContext';
import '../styles/Common.css';
import '../styles/Components.css';
import '../styles/ActiveProject.css';
import { useNavigate } from 'react-router-dom';

interface ActiveProjectPageProps {
  project: ResearchProject;
  onBack: () => void;
  onUpdateProgress: (projectId: string, stepIndex: number) => void;
}

interface StepTemplate {
  title: string;
  description: string;
  tips: string[];
  duration: string;
}

const ActiveProjectPage: React.FC<ActiveProjectPageProps> = ({
  project,
  onBack,
  onUpdateProgress
}) => {
  const navigate = useNavigate();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [projectSteps, setProjectSteps] = useState<StepTemplate[]>([]);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [isUsingAIPlan, setIsUsingAIPlan] = useState(false);
  const [planStatus, setPlanStatus] = useState<'cached' | 'generated' | 'default' | null>(null);

  // 記録フォーム関連の状態
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [isCreatingRecord, setIsCreatingRecord] = useState(false);
  const [recordFormData, setRecordFormData] = useState({
    title: '',
    content: '',
    recordType: 'note' as const,
    tags: [] as string[],
    weatherInfo: null as any,
    locationInfo: null as any
  });

  // 写真アップロード関連の状態
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [showPhotoModal, setShowPhotoModal] = useState(false);

  // 研究完了メッセージ関連の状態
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);

  // AppContextからユーザー情報を取得
  const { authState, loadUserRecords, loadDashboardData } = useApp();

  // AIが生成したステップをStepTemplateに変換
  const convertAIStepsToTemplate = (aiSteps: AIResearchStep[]): StepTemplate[] => {
    return aiSteps.map(step => ({
      title: step.title,
      description: step.description,
      tips: step.tips,
      duration: step.duration
    }));
  };

  // 研究タイプに応じたステップテンプレートを定義（フォールバック用）
  const getDefaultStepTemplates = (genre: Genre): StepTemplate[] => {
    switch (genre) {
      case 'experiment':
        return [
          {
            title: '準備',
            description: '実験に必要な材料や道具を揃え、安全に実験を行うための環境を整えます。',
            tips: [
              '必要な材料をすべて揃えましょう',
              '実験を行う場所を確保しましょう',
              '安全対策を確認しましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '仮説設定',
            description: '実験の結果を予想し、なぜそうなると思うかの理由を考えます。',
            tips: [
              '「もし〜なら、〜になるだろう」の形で仮説を立てましょう',
              '仮説の理由も一緒に考えましょう',
              '複数の仮説を立てても良いです'
            ],
            duration: '1日'
          },
          {
            title: '実験設計',
            description: '仮説を確かめるための具体的な実験方法を計画します。',
            tips: [
              '実験の手順を詳しく書きましょう',
              '測定方法を決めましょう',
              '何回実験するか決めましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '実験実施',
            description: '計画に従って実験を行い、結果を観察・測定します。',
            tips: [
              '手順通りに実験を行いましょう',
              '結果をその場で記録しましょう',
              '写真や動画も撮りましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '結果記録',
            description: '実験で得られたデータや観察結果を整理します。',
            tips: [
              'データを表やグラフにまとめましょう',
              '写真や図も整理しましょう',
              '気づいたことをメモしましょう'
            ],
            duration: '1-2日'
          },
          {
            title: 'データ分析',
            description: '実験結果から傾向やパターンを見つけ出します。',
            tips: [
              'データの変化や傾向を見つけましょう',
              'グラフを作って視覚的に分析しましょう',
              '予想と違った部分があるか確認しましょう'
            ],
            duration: '1-2日'
          },
          {
            title: '考察・結論',
            description: '結果から分かったことをまとめ、仮説が正しかったかを判断します。',
            tips: [
              '仮説が正しかったか検証しましょう',
              'なぜそうなったかを考えましょう',
              '新しい疑問があれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      case 'observation':
        return [
          {
            title: '準備',
            description: '観察に必要な道具を揃え、観察場所や対象を決めます。',
            tips: [
              '観察道具（虫眼鏡、定規、カメラなど）を準備しましょう',
              '観察する対象を決めましょう',
              '観察記録の方法を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '観察計画',
            description: 'いつ、どこで、何を、どのように観察するかを計画します。',
            tips: [
              '観察の時間帯を決めましょう',
              '観察の頻度を決めましょう',
              '記録する項目を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '継続観察',
            description: '計画に従って継続的に観察を行います。',
            tips: [
              '毎回同じ時間に観察しましょう',
              '変化を見逃さないよう注意深く観察しましょう',
              '写真やスケッチも活用しましょう'
            ],
            duration: '7-14日'
          },
          {
            title: '記録蓄積',
            description: '観察した内容を詳しく記録し、データを蓄積します。',
            tips: [
              '日付、時間、天気も記録しましょう',
              '変化を具体的に記録しましょう',
              '疑問に思ったことも書き留めましょう'
            ],
            duration: '継続'
          },
          {
            title: 'パターン発見',
            description: '蓄積したデータから規則性や変化のパターンを見つけます。',
            tips: [
              'グラフや表を作って変化を可視化しましょう',
              '繰り返し起こることがないか探しましょう',
              '環境の変化と観察対象の変化を比較しましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '考察・結論',
            description: '観察結果から分かったことをまとめ、結論を導きます。',
            tips: [
              '発見したパターンの理由を考えましょう',
              '他の要因との関係を考えましょう',
              'さらに詳しく調べたいことがあれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      case 'research':
        return [
          {
            title: '準備',
            description: '調査に必要な道具や方法を準備し、調査対象を明確にします。',
            tips: [
              '調査テーマを明確にしましょう',
              '調査方法を決めましょう',
              '必要な道具や資料を準備しましょう'
            ],
            duration: '1日'
          },
          {
            title: '問題設定',
            description: '調査で明らかにしたい問題や疑問を具体的に設定します。',
            tips: [
              '調べたい疑問を具体的に書きましょう',
              '調査の目的を明確にしましょう',
              '調査範囲を決めましょう'
            ],
            duration: '1日'
          },
          {
            title: '情報収集',
            description: '本、インターネット、アンケート、インタビューなどで情報を集めます。',
            tips: [
              '複数の情報源から情報を集めましょう',
              '情報の出典を記録しましょう',
              '信頼できる情報か確認しましょう'
            ],
            duration: '3-5日'
          },
          {
            title: 'データ整理',
            description: '集めた情報を分類し、整理します。',
            tips: [
              '情報をテーマ別に分類しましょう',
              '表やグラフを使って整理しましょう',
              '重要な情報を見つけやすくしましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '分析・比較',
            description: '整理した情報を分析し、比較検討します。',
            tips: [
              '異なる情報を比較しましょう',
              '共通点や相違点を見つけましょう',
              '傾向やパターンを探しましょう'
            ],
            duration: '2-3日'
          },
          {
            title: '考察・結論',
            description: '分析結果から結論を導き、自分の考えをまとめます。',
            tips: [
              '調査結果から分かったことをまとめましょう',
              '自分の考えや意見を書きましょう',
              '新しい疑問があれば書き留めましょう'
            ],
            duration: '2-3日'
          }
        ];

      default:
        return [];
    }
  };

  // 研究計画を取得または生成
  const loadResearchPlan = async (themeId: string) => {
    setIsLoadingPlan(true);
    setPlanError(null);

    console.log('🔄 研究計画を読み込み中...', {
      themeId,
      projectTitle: project.title,
      projectGenre: project.genre
    });

    // テーマIDの有効性を厳密にチェック
    if (!themeId ||
        themeId === '' ||
        themeId === 'undefined' ||
        themeId.startsWith('project-')) {
      console.warn('⚠️ 無効なテーマIDが検出されました。デフォルトプランを使用します:', themeId);
      const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
      setProjectSteps(defaultSteps);
      setIsUsingAIPlan(false);
      setPlanStatus('default');
      setPlanError('無効なテーマIDのため、デフォルトプランを使用しています。');
      setIsLoadingPlan(false);
      return;
    }

    try {
      // generate_research_plan を直接呼び出す
      // このAPIは既存の研究計画があるかチェックして、ない場合は新規生成する
      const response = await themeApi.generateResearchPlan(themeId);

      console.log('📊 研究計画API応答:', response);

      if (response.success && response.plan) {
        const aiSteps = convertAIStepsToTemplate(response.plan.steps);
        setProjectSteps(aiSteps);
        setIsUsingAIPlan(true);

        // メッセージから生成されたか既存だったかを判定
        if (response.message.includes('保存された研究計画')) {
          setPlanStatus('cached');
        } else {
          setPlanStatus('generated');
        }

        console.log(`✅ 研究計画を読み込みました: ${response.plan.theme_title}`);
      } else {
        console.warn('⚠️ AI研究計画の取得に失敗、デフォルトプランを使用します');
        console.warn('エラー詳細:', response.message);

        const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
        setProjectSteps(defaultSteps);
        setIsUsingAIPlan(false);
        setPlanStatus('default');
        setPlanError('テーマが見つからないため、デフォルトプランを使用しています。');
      }
    } catch (error) {
      console.error('❌ 研究計画の取得でエラーが発生しました:', error);
      const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
      setProjectSteps(defaultSteps);
      setIsUsingAIPlan(false);
      setPlanStatus('default');
      setPlanError('ネットワークエラーのため、デフォルトプランを使用しています。');
    } finally {
      setIsLoadingPlan(false);
    }
  };

  useEffect(() => {
    console.log('🔍 ActiveProjectPageにプロジェクトデータが渡されました:', {
      id: project.id,
      title: project.title,
      themeId: project.themeId,
      currentStepIndex: project.currentStepIndex,
      progressPercentage: project.progressPercentage,
      genre: project.genre,
      status: project.status,
      updatedAt: project.updatedAt
    });

    // プロジェクトにthemeIdがある場合、研究計画を取得
    if (project.themeId && project.themeId !== '' && project.themeId !== 'undefined') {
      console.log('✅ 有効なテーマIDが見つかりました:', project.themeId);
      loadResearchPlan(project.themeId);
    } else {
      console.warn('⚠️ 無効なテーマIDです。デフォルトプランを使用します。', {
        themeId: project.themeId,
        projectTitle: project.title
      });
      const defaultSteps = getDefaultStepTemplates(project.genre || 'experiment');
      setProjectSteps(defaultSteps);
      setIsUsingAIPlan(false);
      setPlanStatus('default');
      setPlanError('プロジェクトにテーマIDが設定されていないため、デフォルトプランを使用しています。');
    }
  }, [project]);

  useEffect(() => {
    if (projectSteps.length > 0) {
      // 保存されたcurrentStepIndexを優先的に使用
      if (project.currentStepIndex !== undefined && project.currentStepIndex >= 0) {
        const newStepIndex = Math.min(project.currentStepIndex, projectSteps.length - 1);
        console.log('📍 保存されたステップインデックスを使用:', newStepIndex);
        setCurrentStepIndex(newStepIndex);
      } else {
        // fallback: プロジェクトの進捗から現在のステップを計算
        const progressIndex = Math.floor((project.progressPercentage / 100) * projectSteps.length);
        const newStepIndex = Math.min(progressIndex, projectSteps.length - 1);
        console.log('📍 進捗からステップインデックスを計算:', newStepIndex);
        setCurrentStepIndex(newStepIndex);
      }
    }
  }, [project.currentStepIndex, project.progressPercentage, projectSteps, project.id]);

  const handleStepComplete = () => {
    console.log('🚀 ステップ完了ボタンがクリックされました:', {
      projectId: project.id,
      currentStepIndex,
      totalSteps: projectSteps.length,
      isLastStep: currentStepIndex >= projectSteps.length - 1
    });

    if (currentStepIndex < projectSteps.length - 1) {
      const newStepIndex = currentStepIndex + 1;
      console.log('➡️ 次のステップに進みます:', {
        from: currentStepIndex,
        to: newStepIndex
      });
      setCurrentStepIndex(newStepIndex);
      onUpdateProgress(project.id, newStepIndex);
    } else {
      // 最後のステップの場合、プロジェクトを完了状態にする
      console.log('🏁 最後のステップです。プロジェクトを完了させます');
      const newStepIndex = currentStepIndex;
      onUpdateProgress(project.id, newStepIndex);
      
      // 研究完了のメッセージを表示
      setShowCompletionMessage(true);
    }
  };

  const handleStepSelect = (stepIndex: number) => {
    setCurrentStepIndex(stepIndex);
  };

  // 写真選択の処理
  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length !== files.length) {
      alert('画像ファイルのみアップロードできます。');
      return;
    }

    // ファイルサイズ制限（2MB）
    const maxSizeBytes = 2 * 1024 * 1024; // 2MB
    const oversizedFiles = imageFiles.filter(file => file.size > maxSizeBytes);
    if (oversizedFiles.length > 0) {
      const oversizedInfo = oversizedFiles.map(f =>
        `${f.name}: ${Math.round(f.size / 1024 / 1024 * 100) / 100}MB`
      ).join('\n');
      alert(`ファイルサイズは2MB以下にしてください。\n\n以下のファイルが大きすぎます:\n${oversizedInfo}`);
      return;
    }

    // 詳細ログ
    console.log('📷 画像選択:', {
      selectedCount: imageFiles.length,
      files: imageFiles.map(f => ({
        name: f.name,
        type: f.type,
        sizeKB: Math.round(f.size / 1024),
        sizeMB: Math.round(f.size / 1024 / 1024 * 100) / 100
      }))
    });

    setSelectedImages(prev => [...prev, ...imageFiles]);

    // プレビュー画像を生成
    imageFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          setImagePreviews(prev => [...prev, e.target!.result as string]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  // 画像を削除
  const handleRemoveImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  // 画像をリセット
  const resetImages = () => {
    setSelectedImages([]);
    setImagePreviews([]);
  };

  // 記録モーダルを開く
  const handleOpenRecordModal = () => {
    // フォームをリセット
    setRecordFormData({
      title: '',
      content: '',
      recordType: 'note',
      tags: [],
      weatherInfo: null,
      locationInfo: null
    });
    resetImages();
    setShowRecordModal(true);
  };

  // 写真モーダルを開く
  const handleOpenPhotoModal = () => {
    resetImages();
    setShowPhotoModal(true);
  };

  // 記録モーダルを閉じる
  const handleCloseRecordModal = () => {
    setShowRecordModal(false);
    resetImages();
  };

  // 写真モーダルを閉じる
  const handleClosePhotoModal = () => {
    setShowPhotoModal(false);
    resetImages();
  };

  // 記録フォームデータの更新
  const handleRecordFormChange = (field: string, value: any) => {
    setRecordFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 画像をBase64に変換する関数（サイズ制限付き）
  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      // ファイルサイズチェック（2MB制限）
      const maxSizeBytes = 2 * 1024 * 1024; // 2MB
      if (file.size > maxSizeBytes) {
        reject(new Error(`ファイルサイズが大きすぎます。最大2MBまでです。現在のサイズ: ${Math.round(file.size / 1024 / 1024 * 100) / 100}MB`));
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          // data:image/jpeg;base64, の部分を除去してBase64文字列だけを取得
          const base64 = (reader.result as string).split(',')[1];

          // Base64サイズもチェック
          const base64SizeKB = Math.round(base64.length / 1024);
          console.log('📷 Base64変換完了:', {
            filename: file.name,
            originalSizeKB: Math.round(file.size / 1024),
            base64SizeKB: base64SizeKB,
            base64Length: base64.length
          });

          resolve(base64);
        } else {
          reject(new Error('ファイルの読み込みに失敗しました'));
        }
      };
      reader.onerror = () => reject(new Error('ファイルの読み込みエラー'));
      reader.readAsDataURL(file);
    });
  };

  // 記録を作成
  const handleCreateRecord = async () => {
    if (!authState.user?.id) {
      alert('ユーザーが認証されていません。再度ログインしてください。');
      return;
    }

    if (!recordFormData.title.trim() || !recordFormData.content.trim()) {
      alert('タイトルと内容を入力してください。');
      return;
    }

    setIsCreatingRecord(true);

    try {
      const currentStep = projectSteps[currentStepIndex];

      // 画像をBase64に変換
      const imageData = await Promise.all(
        selectedImages.map(async (file, index) => ({
          filename: file.name,
          contentType: file.type,
          size: file.size,
          base64Data: await convertImageToBase64(file)
        }))
      );

      // 現地時間で日時を設定
      const now = new Date();
      const localDate = now.getFullYear() + '-' +
                       String(now.getMonth() + 1).padStart(2, '0') + '-' +
                       String(now.getDate()).padStart(2, '0');
      const localTime = String(now.getHours()).padStart(2, '0') + ':' +
                       String(now.getMinutes()).padStart(2, '0');

      const createRequest: CreateRecordRequest = {
        projectId: project.id,
        stepId: `step-${currentStepIndex + 1}`,
        recordType: recordFormData.recordType,
        title: recordFormData.title,
        content: recordFormData.content,
        recordDate: localDate,
        recordTime: localTime,
        data: {
          stepName: currentStep?.title || '',
          stepIndex: currentStepIndex,
          projectGenre: project.genre,
          images: imageData.length > 0 ? imageData : undefined
        },
        tags: recordFormData.tags,
        weatherInfo: recordFormData.weatherInfo,
        locationInfo: recordFormData.locationInfo
      };

      console.log('🔄 記録作成中...', createRequest);
      if (imageData.length > 0) {
        console.log('📷 送信する画像データの詳細:', {
          imageCount: imageData.length,
          images: imageData.map((img, i) => ({
            index: i,
            filename: img.filename,
            contentType: img.contentType,
            size: img.size,
            base64Length: img.base64Data.length,
            base64Sample: img.base64Data.substring(0, 50) + '...'
          }))
        });
      }

      // AWSに記録を保存
      const response = await recordApi.createRecord(authState.user.id, createRequest);

      console.log('✅ 記録作成成功:', response);

      // 成功通知
      alert('記録が正常に保存されました！');

      // 記録一覧とダッシュボードを更新（少し待機してから再読み込み）
      setTimeout(async () => {
        await loadUserRecords();
        await loadDashboardData();
        console.log('📚 記録作成後の記録一覧とダッシュボードを更新しました');
      }, 1000);

      // モーダルを閉じる
      handleCloseRecordModal();

    } catch (error) {
      console.error('❌ 記録作成エラー:', error);

      let errorMessage = '記録の保存に失敗しました。';

      if (error instanceof Error) {
        if (error.message.includes('ファイルサイズが大きすぎます')) {
          errorMessage = error.message;
        } else if (error.message.includes('Network')) {
          errorMessage = 'ネットワークエラーが発生しました。インターネット接続を確認してください。';
        } else if (error.message.includes('413') || error.message.includes('Payload Too Large')) {
          errorMessage = '添付ファイルが大きすぎます。2MB以下の画像を選択してください。';
        } else {
          errorMessage = `エラー: ${error.message}`;
        }
      }

      alert(errorMessage + '\n\nもう一度お試しください。');
    } finally {
      setIsCreatingRecord(false);
    }
  };

  // 写真のみの記録を作成
  const handleCreatePhotoRecord = async () => {
    if (!authState.user?.id) {
      alert('ユーザーが認証されていません。再度ログインしてください。');
      return;
    }

    if (selectedImages.length === 0) {
      alert('写真を選択してください。');
      return;
    }

    setIsCreatingRecord(true);

    try {
      const currentStep = projectSteps[currentStepIndex];

      // 画像をBase64に変換
      const imageData = await Promise.all(
        selectedImages.map(async (file, index) => ({
          filename: file.name,
          contentType: file.type,
          size: file.size,
          base64Data: await convertImageToBase64(file)
        }))
      );

      // 現地時間で日時を設定
      const now = new Date();
      const localDate = now.getFullYear() + '-' +
                       String(now.getMonth() + 1).padStart(2, '0') + '-' +
                       String(now.getDate()).padStart(2, '0');
      const localTime = String(now.getHours()).padStart(2, '0') + ':' +
                       String(now.getMinutes()).padStart(2, '0');

      const createRequest: CreateRecordRequest = {
        projectId: project.id,
        stepId: `step-${currentStepIndex + 1}`,
        recordType: 'photo',
        title: `写真記録 - ${currentStep?.title || 'ステップ記録'}`,
        content: `${selectedImages.length}枚の写真を追加しました。`,
        recordDate: localDate,
        recordTime: localTime,
        data: {
          stepName: currentStep?.title || '',
          stepIndex: currentStepIndex,
          projectGenre: project.genre,
          images: imageData
        },
        tags: ['写真', currentStep?.title || ''],
        weatherInfo: undefined,
        locationInfo: undefined
      };

      console.log('🔄 写真記録作成中...', createRequest);
      console.log('📷 送信する画像データの詳細:', {
        imageCount: imageData.length,
        images: imageData.map((img, i) => ({
          index: i,
          filename: img.filename,
          contentType: img.contentType,
          size: img.size,
          base64Length: img.base64Data.length,
          base64Sample: img.base64Data.substring(0, 50) + '...'
        }))
      });

      // AWSに記録を保存
      const response = await recordApi.createRecord(authState.user.id, createRequest);

      console.log('✅ 写真記録作成成功:', response);
      console.log('📷 作成された記録のメディア情報:', {
        recordId: response.record?.recordId,
        mediaCount: response.media?.length || 0,
        mediaData: response.media || [],
        fullResponse: response
      });

      // 成功通知
      alert('写真が正常に保存されました！');

      // 記録一覧とダッシュボードを更新（少し待機してから再読み込み）
      setTimeout(async () => {
        await loadUserRecords();
        await loadDashboardData();
        console.log('📚 写真記録作成後の記録一覧とダッシュボードを更新しました');
      }, 1500);

      // モーダルを閉じる
      handleClosePhotoModal();

    } catch (error) {
      console.error('❌ 写真記録作成エラー:', error);

      let errorMessage = '写真の保存に失敗しました。';

      if (error instanceof Error) {
        if (error.message.includes('ファイルサイズが大きすぎます')) {
          errorMessage = error.message;
        } else if (error.message.includes('Network')) {
          errorMessage = 'ネットワークエラーが発生しました。インターネット接続を確認してください。';
        } else if (error.message.includes('413') || error.message.includes('Payload Too Large')) {
          errorMessage = '画像ファイルが大きすぎます。2MB以下の画像を選択してください。';
        } else {
          errorMessage = `エラー: ${error.message}`;
        }
      }

      alert(errorMessage + '\n\nもう一度お試しください。');
    } finally {
      setIsCreatingRecord(false);
    }
  };

  const getGenreDisplayName = (genre: Genre) => {
    const genreMap = {
      'experiment': '実験型',
      'observation': '観察型',
      'research': '調査型'
    };
    return genreMap[genre] || '実験型';
  };

  const getGenreIcon = (genre: Genre) => {
    const iconMap = {
      'experiment': '🧪',
      'observation': '👀',
      'research': '📚'
    };
    return iconMap[genre] || '🧪';
  };

  const getPlanStatusMessage = () => {
    switch (planStatus) {
      case 'cached':
        return '保存された研究計画を使用しています';
      case 'generated':
        return '新しい研究計画を生成・保存しました';
      case 'default':
        return 'デフォルトの研究計画を使用しています';
      default:
        return '';
    }
  };

  // ローディング中の表示
  if (isLoadingPlan) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>研究計画を準備中...</h2>
          <p>あなたのテーマに最適な研究計画を取得しています。</p>
        </div>
      </div>
    );
  }

  // ステップがない場合の表示
  if (projectSteps.length === 0) {
    return (
      <div className="page-container">
        <div className="error-container">
          <h2>研究計画の読み込みに失敗しました</h2>
          <p>しばらく待ってから再度お試しください。</p>
          <button onClick={onBack}>ダッシュボードに戻る</button>
        </div>
      </div>
    );
  }

  const currentStep = projectSteps[currentStepIndex];
  const progressPercentage = ((currentStepIndex + 1) / projectSteps.length) * 100;

  return (
    <div className="page-container">
      <div className="header-section">
        <button className="back-button" onClick={onBack}>
          ← ダッシュボードに戻る
        </button>
        <div className="project-header">
          <div className="project-title-section">
            <h1>{project.title}</h1>
            <div className="project-meta">
              <span className="genre-badge">
                {getGenreIcon(project.genre || 'experiment')} {getGenreDisplayName(project.genre || 'experiment')}
              </span>
              {isUsingAIPlan && (
                <span className="ai-badge">
                  🤖 AI研究計画
                </span>
              )}
            </div>
          </div>
          <div className="overall-progress">
            <div className="progress-header">
              <span>全体の進捗</span>
              <span>{Math.round(progressPercentage)}%</span>
            </div>
            <div className="progress-bar-outer">
              <div className="progress-bar-inner" style={{ width: `${progressPercentage}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {planError && (
        <div className="error-notice">
          <span>⚠️ {planError}</span>
        </div>
      )}

      {/* {planStatus && (
        <div className="plan-status-notice">
          <span>ℹ️ {getPlanStatusMessage()}</span>
        </div>
      )} */}

      <div className="active-project-content">
        <div className="steps-timeline">
          <h2>研究の流れ</h2>
          <div className="timeline">
            {projectSteps.map((step, index) => (
              <div
                key={index}
                className={`timeline-item ${index === currentStepIndex ? 'current' : ''} ${
                  index < currentStepIndex ? 'completed' : ''
                }`}
                onClick={() => handleStepSelect(index)}
              >
                <div className="timeline-marker">
                  {index < currentStepIndex ? '✅' : index === currentStepIndex ? '❗️' : '🔸'}
                </div>
                <div className="timeline-content">
                  <div className="step-title">{step.title}</div>
                  <div className="step-duration">{step.duration}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="current-step-detail">
          <div className="step-card">
            <div className="step-header">
              <h2>
                ステップ {currentStepIndex + 1}: {currentStep.title}
              </h2>
              <div className="step-status">
                {currentStepIndex < projectSteps.length - 1 ? '進行中' : '最終ステップ'}
              </div>
            </div>

            <div className="step-description">
              <h3>このステップでやること</h3>
              <p>{currentStep.description}</p>
            </div>

            <div className="step-tips">
              <h3>💡 ポイント</h3>
              <ul>
                {currentStep.tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>

            <div className="step-duration-info">
              <strong>目安時間:</strong> {currentStep.duration}
            </div>

            <div className="step-actions">
              {currentStepIndex < projectSteps.length - 1 ? (
                <button className="step-complete-btn" onClick={handleStepComplete}>
                  このステップを完了して次へ
                </button>
              ) : (
                <button className="step-complete-btn" onClick={handleStepComplete}>
                  研究を完了する
                </button>
              )}

              <div className="secondary-actions">
                <button className="secondary-btn" onClick={handleOpenRecordModal}>
                  📝 記録する
                </button>
                <button className="secondary-btn" onClick={handleOpenPhotoModal}>
                  📷 写真を追加
                </button>
                <button className="secondary-btn">
                  🤖 AI先生に質問
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 記録作成モーダル */}
      {showRecordModal && (
        <div className="modal-overlay" onClick={handleCloseRecordModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>研究記録を作成</h3>
              <button
                className="close-btn"
                onClick={handleCloseRecordModal}
                disabled={isCreatingRecord}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="recordType">記録の種類</label>
                <select
                  id="recordType"
                  value={recordFormData.recordType}
                  onChange={(e) => handleRecordFormChange('recordType', e.target.value)}
                  disabled={isCreatingRecord}
                  className="form-select"
                >
                  <option value="note">メモ</option>
                  <option value="observation">観察記録</option>
                  <option value="experiment">実験記録</option>
                  <option value="data">データ記録</option>
                  <option value="photo">写真記録</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="recordTitle">タイトル</label>
                <input
                  id="recordTitle"
                  type="text"
                  value={recordFormData.title}
                  onChange={(e) => handleRecordFormChange('title', e.target.value)}
                  placeholder="記録のタイトルを入力してください"
                  disabled={isCreatingRecord}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="recordContent">内容</label>
                <textarea
                  id="recordContent"
                  value={recordFormData.content}
                  onChange={(e) => handleRecordFormChange('content', e.target.value)}
                  placeholder="観察した内容、実験の結果、感想などを詳しく記録してください"
                  disabled={isCreatingRecord}
                  className="form-textarea"
                  rows={6}
                />
              </div>

              <div className="form-group">
                <label htmlFor="recordTags">タグ（任意）</label>
                <input
                  id="recordTags"
                  type="text"
                  placeholder="カンマ区切りでタグを入力 (例: 観察, 植物, 成長)"
                  disabled={isCreatingRecord}
                  className="form-input"
                  onChange={(e) => {
                    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                    handleRecordFormChange('tags', tags);
                  }}
                />
              </div>

              <div className="form-group">
                <label htmlFor="recordImages">写真（任意）</label>
                <input
                  id="recordImages"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageSelect}
                  disabled={isCreatingRecord}
                  className="form-input"
                />
                <div className="form-helper-text">
                  最大2MBまでの画像ファイル（JPG、PNG、GIF）をアップロードできます。
                </div>

                {imagePreviews.length > 0 && (
                  <div className="image-preview-container">
                    <div className="image-preview-label">選択された写真:</div>
                    <div className="image-preview-grid">
                      {imagePreviews.map((preview, index) => (
                        <div key={index} className="image-preview-item">
                          <img
                            src={preview}
                            alt={`プレビュー ${index + 1}`}
                            className="image-preview"
                          />
                          <button
                            type="button"
                            className="image-remove-btn"
                            onClick={() => handleRemoveImage(index)}
                            disabled={isCreatingRecord}
                          >
                            ×
                          </button>
                          <div className="image-filename">
                            {selectedImages[index]?.name}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="cancel-btn"
                onClick={handleCloseRecordModal}
                disabled={isCreatingRecord}
              >
                キャンセル
              </button>
              <button
                className="save-btn"
                onClick={handleCreateRecord}
                disabled={isCreatingRecord || !recordFormData.title.trim() || !recordFormData.content.trim()}
              >
                {isCreatingRecord ? '保存中...' : '記録を保存'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 写真アップロードモーダル */}
      {showPhotoModal && (
        <div className="modal-overlay" onClick={handleClosePhotoModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>写真を追加</h3>
              <button
                className="close-btn"
                onClick={handleClosePhotoModal}
                disabled={isCreatingRecord}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="photoUpload">写真を選択</label>
                <input
                  id="photoUpload"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageSelect}
                  disabled={isCreatingRecord}
                  className="form-input"
                />
                <div className="form-helper-text">
                  最大2MBまでの画像ファイル（JPG、PNG、GIF）を複数選択できます。
                </div>
              </div>

              {imagePreviews.length > 0 && (
                <div className="image-preview-container">
                  <div className="image-preview-label">選択された写真 ({selectedImages.length}枚):</div>
                  <div className="image-preview-grid">
                    {imagePreviews.map((preview, index) => (
                      <div key={index} className="image-preview-item">
                        <img
                          src={preview}
                          alt={`プレビュー ${index + 1}`}
                          className="image-preview"
                        />
                        <button
                          type="button"
                          className="image-remove-btn"
                          onClick={() => handleRemoveImage(index)}
                          disabled={isCreatingRecord}
                        >
                          ×
                        </button>
                        <div className="image-filename">
                          {selectedImages[index]?.name}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="cancel-btn"
                onClick={handleClosePhotoModal}
                disabled={isCreatingRecord}
              >
                キャンセル
              </button>
              <button
                className="save-btn"
                onClick={handleCreatePhotoRecord}
                disabled={isCreatingRecord || selectedImages.length === 0}
              >
                {isCreatingRecord ? '保存中...' : '写真を保存'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 研究完了メッセージ */}
      {showCompletionMessage && (
        <div className="modal-overlay" onClick={() => setShowCompletionMessage(false)}>
          <div className="modal-content completion-message" onClick={(e) => e.stopPropagation()}>
            <div className="completion-header">
              <div className="completion-icon">🎉</div>
              <h2>お疲れ様でした！</h2>
            </div>
            <div className="completion-body">
              <h3>研究「{project.title}」が完了しました！</h3>
              <p>あなたの努力と探求心が素晴らしい研究を生み出しました。</p>
              <p>この経験は、きっと将来の学びに活かされることでしょう。</p>
              <p>ダッシュボードで研究の記録を振り返ることができます。</p>
            </div>
            <div className="completion-footer">
              <button 
                className="completion-btn"
                onClick={() => setShowCompletionMessage(false)}
              >
                ありがとう！
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActiveProjectPage;
