import React, { useState, useEffect, useMemo } from 'react';
import { Record, ResearchProject, Schedule } from '../types';
import { useApp } from '../context/AppContext';
import '../styles/RecordCalendar.css';
import '../styles/Common.css';

interface RecordCalendarPageProps {
  activeProjects: ResearchProject[];
  records: Record[];
  schedules: Schedule[];
  onBack: () => void;
  onAddRecord: (record: Partial<Record>) => void;
  onViewRecord: (record: Record) => void;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  hasActions: boolean;
  hasObservations: boolean;
  actionCount: number;
  records: Record[];
  schedules: Schedule[];
}

const RecordCalendarPage: React.FC<RecordCalendarPageProps> = ({
  activeProjects,
  records,
  schedules,
  onBack,
  onAddRecord,
  onViewRecord
}) => {
  const { loadUserRecords, authState } = useApp();

  // 🔍 デバッグ情報を詳しく出力
  console.log('📅 RecordCalendarPage表示 - 詳細デバッグ:', {
    // 基本情報
    recordsCount: records.length,
    schedulesCount: schedules.length,
    activeProjectsCount: activeProjects.length,

    // 認証情報
    isAuthenticated: authState.isAuthenticated,
    userId: authState.user?.id,

    // 現在の日付
    currentDate: new Date(),
    currentDateString: new Date().toLocaleDateString('ja-JP'),

    // 記録データの詳細
    recordsDetails: records.map(r => ({
      id: r.id,
      title: r.title,
      recordType: r.recordType,
      recordDate: r.recordDate,
      recordDateAsDate: new Date(r.recordDate),
      recordDateString: new Date(r.recordDate).toLocaleDateString('ja-JP'),
      hasImages: !!(r.data?.images && r.data.images.length > 0),
      imageCount: r.data?.images?.length || 0,
      dataStructure: r.data ? Object.keys(r.data) : [],
      fullRecord: r
    })),

    // 今日の記録があるかチェック
    todayString: new Date().toLocaleDateString('ja-JP'),
    recordsToday: records.filter(r => {
      const recordDate = new Date(r.recordDate);
      const today = new Date();
      return recordDate.toDateString() === today.toDateString();
    }).length,

    // 12月19日の記録があるかチェック
    testDateString: '2024-12-19',
    recordsOn1219: records.filter(r => r.recordDate.startsWith('2024-12-19')).length,
    recordsOn1219Details: records.filter(r => r.recordDate.startsWith('2024-12-19')).map(r => ({
      title: r.title,
      recordDate: r.recordDate,
      recordType: r.recordType
    }))
  });

  // ページ表示時に記録データを再読み込み
  useEffect(() => {
    console.log('🔄 記録カレンダーページで記録データを再読み込み中...');
    loadUserRecords();
  }, [loadUserRecords]);

  // 記録データが変更された時にカレンダーを更新
  useEffect(() => {
    console.log('📅 記録データが更新されました:', {
      recordsCount: records.length,
      lastUpdate: new Date().toLocaleTimeString()
    });
  }, [records]);

  // 📅 記録データに基づいて適切な月を表示
  const [currentDate, setCurrentDate] = useState(() => {
    // 初期値は今日の日付
    return new Date();
  });

  // 記録データが更新されたときに、最新の記録がある月を表示するように調整
  useEffect(() => {
    if (records.length > 0) {
      // 最新の記録の日付を取得
      const sortedRecords = [...records].sort((a, b) => 
        new Date(b.recordDate).getTime() - new Date(a.recordDate).getTime()
      );
      
      const latestRecord = sortedRecords[0];
      const latestRecordDate = new Date(latestRecord.recordDate);
      
      console.log('📅 最新記録に基づいてカレンダー月を設定:', {
        latestRecordTitle: latestRecord.title,
        latestRecordDate: latestRecord.recordDate,
        parsedDate: latestRecordDate,
        currentCalendarMonth: currentDate.getMonth() + 1,
        currentCalendarYear: currentDate.getFullYear(),
        latestRecordMonth: latestRecordDate.getMonth() + 1,
        latestRecordYear: latestRecordDate.getFullYear()
      });
      
      // 現在表示している月と最新記録の月が異なる場合、最新記録の月に移動
      if (currentDate.getFullYear() !== latestRecordDate.getFullYear() || 
          currentDate.getMonth() !== latestRecordDate.getMonth()) {
        console.log('📅 カレンダーを最新記録の月に移動:', {
          from: `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`,
          to: `${latestRecordDate.getFullYear()}年${latestRecordDate.getMonth() + 1}月`
        });
        setCurrentDate(new Date(latestRecordDate.getFullYear(), latestRecordDate.getMonth(), 1));
      }
    }
  }, [records]);

  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [newRecordType, setNewRecordType] = useState<'observation' | 'experiment' | 'note'>('observation');
  const [newRecordContent, setNewRecordContent] = useState('');
  const [selectedProject, setSelectedProject] = useState<string>('');

  // 記録詳細表示用の状態
  const [selectedRecord, setSelectedRecord] = useState<Record | null>(null);
  const [showRecordDetail, setShowRecordDetail] = useState(false);

  // 画像拡大表示用の状態
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);

  // 月の表示名を取得
  const getMonthName = (date: Date) => {
    return date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long' });
  };

  // カレンダーの日付データを生成
  const generateCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // 月の最初の日と最後の日
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    // カレンダーの開始日（前月の日曜日から）
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    // カレンダーの終了日（翌月の土曜日まで）
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()));

    const days: CalendarDay[] = [];
    const current = new Date(startDate);

    console.log('📅 カレンダー生成開始:', {
      year: year,
      month: month + 1,
      monthName: getMonthName(currentDate),
      startDate: startDate.toLocaleDateString('ja-JP'),
      endDate: endDate.toLocaleDateString('ja-JP'),
      totalRecords: records.length
    });

    while (current <= endDate) {
      // 現地時間で日付文字列を生成
      const localDateStr = current.getFullYear() + '-' +
                          String(current.getMonth() + 1).padStart(2, '0') + '-' +
                          String(current.getDate()).padStart(2, '0');

      const dayRecords = records.filter(r => r.recordDate.startsWith(localDateStr));
      const daySchedules = schedules.filter(s => s.scheduledAt && s.scheduledAt.startsWith(localDateStr));

      // 🔍 各日の記録データを詳しくログ出力
      if (dayRecords.length > 0) {
        console.log(`📅 ${localDateStr}の記録詳細:`, {
          totalRecords: dayRecords.length,
          records: dayRecords.map(r => ({
            id: r.id,
            title: r.title,
            recordType: r.recordType,
            recordDate: r.recordDate,
            hasImages: !!(r.data?.images && r.data.images.length > 0),
            imageCount: r.data?.images?.length || 0
          }))
        });

        const recordsWithImages = dayRecords.filter(r => r.data?.images && r.data.images.length > 0);
        if (recordsWithImages.length > 0) {
          console.log(`📷 ${localDateStr}の画像付き記録:`, {
            totalRecords: dayRecords.length,
            recordsWithImages: recordsWithImages.length,
            records: recordsWithImages.map(r => ({
              title: r.title,
              imageCount: r.data.images.length
            }))
          });
        }
      }

      days.push({
        date: new Date(current),
        isCurrentMonth: current.getMonth() === month,
        hasActions: dayRecords.length > 0 || daySchedules.some(s => s.isCompleted),
        hasObservations: dayRecords.some(r => r.recordType === 'observation'),
        actionCount: dayRecords.length + daySchedules.filter(s => s.isCompleted).length,
        records: dayRecords,
        schedules: daySchedules
      });

      current.setDate(current.getDate() + 1);
    }

    // 🔍 カレンダー生成結果をログ出力
    const totalRecordsInCalendar = days.reduce((sum, day) => sum + day.records.length, 0);
    const daysWithRecords = days.filter(day => day.records.length > 0);

    console.log('📅 カレンダー生成完了:', {
      totalDays: days.length,
      totalRecordsInCalendar: totalRecordsInCalendar,
      daysWithRecords: daysWithRecords.length,
      daysWithRecordsDetails: daysWithRecords.map(day => ({
        date: day.date.toLocaleDateString('ja-JP'),
        recordsCount: day.records.length,
        recordTitles: day.records.map(r => r.title)
      }))
    });

    return days;
  };

  const calendarDays = useMemo(() => generateCalendarDays(), [currentDate, records, schedules]);

  // 前月・次月の移動
  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + (direction === 'prev' ? -1 : 1));
    setCurrentDate(newDate);
  };

  // 日付をクリック
  const handleDateClick = (day: CalendarDay) => {
    setSelectedDate(day.date);
  };

  // 記録を追加
  const handleAddRecord = () => {
    if (!selectedDate || !selectedProject || !newRecordContent.trim()) return;

    const newRecord: Partial<Record> = {
      projectId: selectedProject,
      recordType: newRecordType,
      title: `${newRecordType === 'observation' ? '観察記録' : newRecordType === 'experiment' ? '実験記録' : 'メモ'}`,
      content: newRecordContent,
      recordDate: selectedDate.toISOString(),
      data: {}
    };

    onAddRecord(newRecord);
    setNewRecordContent('');
    setShowRecordModal(false);
  };

  // 観察型プロジェクトを取得
  const observationProjects = activeProjects.filter(p => p.genre === 'observation');

  // 記録詳細を表示
  const handleViewRecordDetail = (record: Record) => {
    console.log('📋 記録詳細表示:', {
      recordId: record.id,
      title: record.title,
      recordType: record.recordType,
      hasImages: !!(record.data?.images && record.data.images.length > 0),
      imageCount: record.data?.images?.length || 0,
      imageData: record.data?.images || [],
      fullRecord: record
    });

    setSelectedRecord(record);
    setShowRecordDetail(true);
  };

  // 記録詳細モーダルを閉じる
  const handleCloseRecordDetail = () => {
    setSelectedRecord(null);
    setShowRecordDetail(false);
  };

    // Base64画像のデータURIを生成
  const getImageDataUri = (image: any) => {
    console.log('🖼️ 画像データURI生成開始:', {
      imageObject: image,
      imageType: typeof image,
      imageKeys: image ? Object.keys(image) : [],
      hasBase64Data: !!image?.base64Data,
      hasContentType: !!image?.contentType,
      contentType: image?.contentType,
      base64Length: image?.base64Data?.length || 0,
      filename: image?.filename,
      base64Sample: image?.base64Data ? image.base64Data.substring(0, 50) + '...' : 'なし'
    });

    // より詳細な検証
    if (!image) {
      console.error('❌ 画像オブジェクトがnullまたはundefinedです');
      return null;
    }

    if (!image.base64Data) {
      console.error('❌ base64Dataが存在しません:', {
        imageProperties: Object.keys(image),
        imageValues: image
      });
      return null;
    }

    if (!image.contentType) {
      console.error('❌ contentTypeが存在しません:', {
        imageProperties: Object.keys(image),
        imageValues: image
      });
      return null;
    }

    try {
      const dataUri = `data:${image.contentType};base64,${image.base64Data}`;
      console.log('✅ データURI生成成功:', {
        contentType: image.contentType,
        dataUriLength: dataUri.length,
        dataUriStart: dataUri.substring(0, 100) + '...'
      });

      return dataUri;
    } catch (error) {
      console.error('❌ データURI生成でエラー:', error);
      return null;
    }
  };

  // 画像データが有効かチェック
  const isValidImage = (image: any) => {
    return image &&
           image.base64Data &&
           image.contentType &&
           typeof image.base64Data === 'string' &&
           typeof image.contentType === 'string' &&
           image.base64Data.length > 0;
  };

  // 記録から画像を取得する関数（record.data.imagesのみ使用）
  const getAllImages = (record: Record) => {
    const images: any[] = [];
    
    // record.data.images から取得（統一方式）
    if (record.data?.images && Array.isArray(record.data.images)) {
      record.data.images.forEach((img: any) => {
        if (isValidImage(img)) {
          images.push(img);
        }
      });
    }
    
    console.log(`📷 記録 ${record.title} の画像取得:`, {
      recordId: record.id,
      dataImages: record.data?.images?.length || 0,
      validImages: images.length,
      images: images.map(img => ({
        filename: img.filename,
        contentType: img.contentType,
        base64Length: img.base64Data?.length || 0
      }))
    });
    
    return images;
  };

  // 画像拡大表示を開く
  const handleOpenImageModal = (imageIndex: number) => {
    setSelectedImageIndex(imageIndex);
    setShowImageModal(true);
  };

  // 画像拡大表示を閉じる
  const handleCloseImageModal = () => {
    setSelectedImageIndex(null);
    setShowImageModal(false);
  };

  // 次の画像を表示
  const handleNextImage = () => {
    if (selectedRecord && selectedImageIndex !== null) {
      const validImages = getAllImages(selectedRecord);
      const nextIndex = (selectedImageIndex + 1) % validImages.length;
      setSelectedImageIndex(nextIndex);
    }
  };

  // 前の画像を表示
  const handlePrevImage = () => {
    if (selectedRecord && selectedImageIndex !== null) {
      const validImages = getAllImages(selectedRecord);
      const prevIndex = selectedImageIndex === 0
        ? validImages.length - 1
        : selectedImageIndex - 1;
      setSelectedImageIndex(prevIndex);
    }
  };

  return (
    <div className="record-calendar-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}>
          ← 戻る
        </button>
        <h1 className="page-title">📅 記録カレンダー</h1>
        {/* <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="reload-btn"
            onClick={() => {
              console.log('🔄 手動で記録データを再読み込み');
              loadUserRecords();
            }}
            style={{
              padding: '8px 16px',
              background: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            🔄 記録再読み込み
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            style={{
              padding: '8px 16px',
              background: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            📅 今月
          </button>
        </div> */}
      </div>

      <div className="calendar-container">
        {/* カレンダーヘッダー */}
        <div className="calendar-header">
          <button className="nav-btn" onClick={() => navigateMonth('prev')}>
            ‹
          </button>
          <h2 className="month-title">{getMonthName(currentDate)}</h2>
          <button className="nav-btn" onClick={() => navigateMonth('next')}>
            ›
          </button>
        </div>

        {/* 曜日ヘッダー */}
        <div className="calendar-weekdays">
          {['日', '月', '火', '水', '木', '金', '土'].map(day => (
            <div key={day} className="weekday-header">{day}</div>
          ))}
        </div>

        {/* カレンダーグリッド */}
        <div className="calendar-grid">
                  {calendarDays.map((day) => (
          <div
            key={day.date.toISOString()}
              className={`calendar-day ${!day.isCurrentMonth ? 'other-month' : ''} ${
                day.hasActions ? 'has-actions' : ''
              } ${day.hasObservations ? 'has-observations' : ''} ${
                selectedDate?.toDateString() === day.date.toDateString() ? 'selected' : ''
              }`}
              onClick={() => handleDateClick(day)}
            >
              <div className="day-number">{day.date.getDate()}</div>
              {day.hasActions && (
                <div className="activity-indicators">
                  {day.hasObservations && <div className="observation-dot">🔍</div>}
                  {day.actionCount > 0 && (
                    <div className="action-count">{day.actionCount}</div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 凡例 */}
        <div className="calendar-legend">
          <div className="legend-item">
            <div className="legend-color has-actions-color"></div>
            <span>アクション実行日</span>
          </div>
          <div className="legend-item">
            <div className="legend-icon">🔍</div>
            <span>観察記録あり</span>
          </div>
        </div>
      </div>

      {/* 選択した日の詳細 */}
      {selectedDate && (
        <div className="selected-date-details">
          <div className="details-header">
            <h3>{selectedDate.toLocaleDateString('ja-JP', {
              month: 'long',
              day: 'numeric',
              weekday: 'long'
            })}</h3>
            {observationProjects.length > 0 && (
              <button
                className="add-record-btn"
                onClick={() => setShowRecordModal(true)}
              >
                + 記録追加
              </button>
            )}
          </div>

          <div className="day-records">
            {(() => {
              const dayData = calendarDays.find(d =>
                d.date.toDateString() === selectedDate.toDateString()
              );

              if (!dayData || (dayData.records.length === 0 && dayData.schedules.length === 0)) {
                return <p className="no-records">この日の記録はありません</p>;
              }

              return (
                <div className="records-list">
                  {/* 記録 */}
                  {dayData.records.map(record => (
                    <div key={record.id} className="record-item" onClick={() => handleViewRecordDetail(record)}>
                      <div className="record-type-icon">
                        {record.recordType === 'observation' ? '🔍' :
                         record.recordType === 'experiment' ? '⚗️ ' :
                         record.recordType === 'photo' ? '📷' : '📝'}
                      </div>
                      <div className="record-content">
                        <div className="record-title">
                          {record.title}
                          {(() => {
                            const allImages = getAllImages(record);
                            return allImages.length > 0 && (
                              <span className="record-image-indicator">📷 {allImages.length}枚</span>
                            );
                          })()}
                        </div>
                        <div className="record-preview">{record.content.substring(0, 50)}...</div>
                        {record.tags && record.tags.length > 0 && (
                          <div className="record-tags">
                            {record.tags.slice(0, 2).map((tag, index) => (
                              <span key={index} className="record-tag">#{tag}</span>
                            ))}
                          </div>
                        )}
                        {/* 写真プレビュー */}
                        {(() => {
                          const allImages = getAllImages(record);
                          return allImages.length > 0 && (
                            <div className="record-image-preview">
                              {allImages.slice(0, 3).map((image: any, index: number) => {
                                console.log(`🖼️ プレビュー画像${index + 1}をレンダリング中:`, {
                                  recordTitle: record.title,
                                  image: image,
                                  imageIndex: index,
                                  isValid: isValidImage(image)
                                });

                                const imageUri = getImageDataUri(image);
                                console.log(`🔗 生成されたURI:`, imageUri ? `${imageUri.substring(0, 50)}...` : 'null');

                                if (!imageUri) {
                                  console.warn(`⚠️ 画像${index + 1}のURIが生成できませんでした`);
                                  return null;
                                }

                                return (
                                  <div key={index} className="record-preview-image">
                                    <img
                                      src={imageUri}
                                      alt={`プレビュー ${index + 1}`}
                                      className="record-preview-img"
                                      onLoad={() => console.log(`✅ プレビュー画像${index + 1}の読み込み成功`)}
                                      onError={(e) => {
                                        console.error(`❌ プレビュー画像${index + 1}の読み込み失敗:`, e);
                                        console.error('エラー詳細:', {
                                          src: imageUri,
                                          image: image,
                                          target: e.target
                                        });
                                      }}
                                    />
                                  </div>
                                );
                              })}
                              {allImages.length > 3 && (
                                <div className="record-more-images">
                                  +{allImages.length - 3}
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                      <div className="record-time">
                        {new Date(record.recordDate).toLocaleTimeString('ja-JP', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  ))}

                  {/* 完了したスケジュール */}
                  {dayData.schedules.filter(s => s.isCompleted).map(schedule => (
                    <div key={schedule.id} className="schedule-item completed">
                      <div className="schedule-icon">✅</div>
                      <div className="schedule-content">
                        <div className="schedule-title">{schedule.title}</div>
                        <div className="schedule-description">{schedule.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* 記録追加モーダル */}
      {showRecordModal && (
        <div className="modal-overlay" onClick={() => setShowRecordModal(false)}>
          <div className="record-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>記録を追加</h3>
              <button className="close-btn" onClick={() => setShowRecordModal(false)}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>プロジェクト</label>
                <select
                  value={selectedProject}
                  onChange={e => setSelectedProject(e.target.value)}
                >
                  <option value="">プロジェクトを選択</option>
                  {observationProjects.map(project => (
                    <option key={project.id} value={project.id}>
                      {project.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>記録の種類</label>
                <div className="record-type-buttons">
                  {['observation', 'experiment', 'note'].map(type => (
                    <button
                      key={type}
                      className={`type-btn ${newRecordType === type ? 'active' : ''}`}
                      onClick={() => setNewRecordType(type as any)}
                    >
                      {type === 'observation' ? '🔍 観察' :
                       type === 'experiment' ? '⚗️ 実験' : '📝 メモ'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>記録内容</label>
                <textarea
                  value={newRecordContent}
                  onChange={e => setNewRecordContent(e.target.value)}
                  placeholder="今日の観察や実験の結果を記録しましょう..."
                  rows={4}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="cancel-btn" onClick={() => setShowRecordModal(false)}>
                キャンセル
              </button>
              <button
                className="save-btn"
                onClick={handleAddRecord}
                disabled={!selectedProject || !newRecordContent.trim()}
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 記録詳細表示モーダル */}
      {showRecordDetail && selectedRecord && (
        <div className="modal-overlay" onClick={handleCloseRecordDetail}>
          <div className="record-detail-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {selectedRecord.recordType === 'observation' ? '🔍' :
                 selectedRecord.recordType === 'experiment' ? '⚗️' :
                 selectedRecord.recordType === 'photo' ? '📷' : '📝'}
                {selectedRecord.title}
              </h3>
              <button className="close-btn" onClick={handleCloseRecordDetail}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="record-meta">
                <div className="record-date">
                  📅 {new Date(selectedRecord.recordDate).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'long'
                  })}
                </div>
                <div className="record-time">
                  🕐 {new Date(selectedRecord.recordDate).toLocaleTimeString('ja-JP', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>

              <div className="record-content-detail">
                <h4>記録内容</h4>
                <p>{selectedRecord.content}</p>
              </div>

              {selectedRecord.tags && selectedRecord.tags.length > 0 && (
                <div className="record-tags-detail">
                  <h4>タグ</h4>
                  <div className="tags-list">
                    {selectedRecord.tags.map((tag, index) => (
                      <span key={index} className="tag-item">#{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              {(() => {
                const allImages = getAllImages(selectedRecord);
                return allImages.length > 0 && (
                  <div className="record-images-detail">
                    <h4>画像 ({allImages.length}枚)</h4>
                    <div className="images-grid">
                      {allImages.map((image: any, index: number) => {
                        const imageUri = getImageDataUri(image);
                        if (!imageUri) return null;

                        return (
                          <div key={index} className="image-item" onClick={() => handleOpenImageModal(index)}>
                            <img
                              src={imageUri}
                              alt={`画像 ${index + 1}`}
                              className="record-detail-img"
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* 画像拡大表示モーダル */}
      {showImageModal && selectedRecord && selectedImageIndex !== null && (
        <div className="modal-overlay" onClick={handleCloseImageModal}>
          <div className="image-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>画像 {selectedImageIndex + 1} / {getAllImages(selectedRecord).length}</h3>
              <button className="close-btn" onClick={handleCloseImageModal}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="image-navigation">
                <button
                  className="nav-btn prev"
                  onClick={handlePrevImage}
                  disabled={getAllImages(selectedRecord).length <= 1}
                >
                  ‹
                </button>

                <div className="image-container">
                  {(() => {
                    const validImages = getAllImages(selectedRecord);
                    const currentImage = validImages[selectedImageIndex];
                    const imageUri = getImageDataUri(currentImage);

                    if (!imageUri) {
                      return <div className="image-error">画像を読み込めませんでした</div>;
                    }

                    return (
                      <img
                        src={imageUri}
                        alt={`拡大画像 ${selectedImageIndex + 1}`}
                        className="expanded-image"
                      />
                    );
                  })()}
                </div>

                <button
                  className="nav-btn next"
                  onClick={handleNextImage}
                  disabled={getAllImages(selectedRecord).length <= 1}
                >
                  ›
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordCalendarPage;
