import React, { useState, useEffect, useMemo } from 'react';
import { Record, ResearchProject, Schedule } from '../types';
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
  const [currentDate, setCurrentDate] = useState(new Date());
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

    while (current <= endDate) {
      // 現地時間で日付文字列を生成
      const localDateStr = current.getFullYear() + '-' +
                          String(current.getMonth() + 1).padStart(2, '0') + '-' +
                          String(current.getDate()).padStart(2, '0');

      const dayRecords = records.filter(r => r.recordDate.startsWith(localDateStr));
      const daySchedules = schedules.filter(s => s.scheduledAt && s.scheduledAt.startsWith(localDateStr));

      // この日の記録に画像があるかデバッグ
      if (dayRecords.length > 0) {
        const recordsWithImages = dayRecords.filter(r => r.data?.images && r.data.images.length > 0);
        if (recordsWithImages.length > 0) {
          console.log(`📅 ${localDateStr}の画像付き記録:`, {
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
    console.log('🖼️ 画像データURI生成:', {
      hasBase64Data: !!image.base64Data,
      hasContentType: !!image.contentType,
      contentType: image.contentType,
      base64Length: image.base64Data?.length || 0,
      filename: image.filename
    });

    if (!image.base64Data || !image.contentType) {
      console.warn('⚠️ 画像データが不完全です:', image);
      return null;
    }

    const dataUri = `data:${image.contentType};base64,${image.base64Data}`;
    console.log('✅ データURI生成成功:', {
      contentType: image.contentType,
      dataUriLength: dataUri.length
    });

    return dataUri;
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
      const nextIndex = (selectedImageIndex + 1) % selectedRecord.data.images.length;
      setSelectedImageIndex(nextIndex);
    }
  };

  // 前の画像を表示
  const handlePrevImage = () => {
    if (selectedRecord && selectedImageIndex !== null) {
      const prevIndex = selectedImageIndex === 0
        ? selectedRecord.data.images.length - 1
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
                          {record.data?.images && record.data.images.length > 0 && (
                            <span className="record-image-indicator">📷 {record.data.images.length}枚</span>
                          )}
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
                        {record.data?.images && record.data.images.length > 0 && (
                          <div className="record-image-preview">
                            {record.data.images.slice(0, 3).map((image: any, index: number) => {
                              const imageUri = getImageDataUri(image);
                              if (!imageUri) return null;
                              return (
                                <div key={index} className="record-preview-image">
                                  <img
                                    src={imageUri}
                                    alt={`プレビュー ${index + 1}`}
                                    className="record-preview-img"
                                  />
                                </div>
                              );
                            })}
                            {record.data.images.length > 3 && (
                              <div className="record-more-images">
                                +{record.data.images.length - 3}
                              </div>
                            )}
                          </div>
                        )}
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
              <h3>記録詳細</h3>
              <button className="close-btn" onClick={handleCloseRecordDetail}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="record-detail-info">
                <div className="record-detail-meta">
                  <span className="record-type-badge">
                    {selectedRecord.recordType === 'observation' ? '🔍 観察記録' :
                     selectedRecord.recordType === 'experiment' ? '⚗️ 実験記録' :
                     selectedRecord.recordType === 'photo' ? '📷 写真記録' :
                     selectedRecord.recordType === 'data' ? '📊 データ記録' : '📝 メモ'}
                  </span>
                  <span className="record-date">
                    {new Date(selectedRecord.recordDate).toLocaleDateString('ja-JP', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      weekday: 'long'
                    })} {new Date(selectedRecord.recordDate).toLocaleTimeString('ja-JP', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>

                <h4 className="record-detail-title">{selectedRecord.title}</h4>

                <div className="record-detail-content">
                  <h5>内容</h5>
                  <p>{selectedRecord.content}</p>
                </div>

                {/* 画像表示 */}
                {selectedRecord.data?.images && selectedRecord.data.images.length > 0 && (
                  <div className="record-detail-images">
                    <h5>写真 ({selectedRecord.data.images.length}枚)</h5>
                    <div className="record-images-grid">
                      {selectedRecord.data.images.map((image: any, index: number) => {
                        const imageUri = getImageDataUri(image);
                        if (!imageUri) return null;

                        return (
                          <div key={index} className="record-image-item">
                            <img
                              src={imageUri}
                              alt={`記録画像 ${index + 1}`}
                              className="record-detail-image"
                              onClick={() => handleOpenImageModal(index)}
                            />
                            <div className="record-image-filename">{image.filename || `画像${index + 1}`}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* タグ表示 */}
                {selectedRecord.tags && selectedRecord.tags.length > 0 && (
                  <div className="record-detail-tags">
                    <h5>タグ</h5>
                    <div className="tags-list">
                      {selectedRecord.tags.map((tag, index) => (
                        <span key={index} className="tag-item">#{tag}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 研究ステップ情報 */}
                {selectedRecord.data?.stepName && (
                  <div className="record-detail-step">
                    <h5>研究ステップ</h5>
                    <p>{selectedRecord.data.stepName}</p>
                  </div>
                )}

                {/* 天気情報 */}
                {selectedRecord.weatherInfo && (
                  <div className="record-detail-weather">
                    <h5>天気情報</h5>
                    <p>{JSON.stringify(selectedRecord.weatherInfo)}</p>
                  </div>
                )}

                {/* 位置情報 */}
                {selectedRecord.locationInfo && (
                  <div className="record-detail-location">
                    <h5>位置情報</h5>
                    <p>{JSON.stringify(selectedRecord.locationInfo)}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button className="close-detail-btn" onClick={handleCloseRecordDetail}>
                閉じる
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 画像拡大表示モーダル */}
      {showImageModal && selectedRecord && selectedImageIndex !== null && (
        <div className="image-modal-overlay" onClick={handleCloseImageModal}>
          <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="image-modal-header">
              <h4>画像 {selectedImageIndex + 1} / {selectedRecord.data.images.length}</h4>
              <button className="close-btn" onClick={handleCloseImageModal}>
                ×
              </button>
            </div>

            <div className="image-modal-body">
              {selectedRecord.data.images[selectedImageIndex] && (
                <img
                  src={getImageDataUri(selectedRecord.data.images[selectedImageIndex])}
                  alt={`画像 ${selectedImageIndex + 1}`}
                  className="modal-image"
                />
              )}
            </div>

            <div className="image-modal-navigation">
              {selectedRecord.data.images.length > 1 && (
                <>
                  <button
                    className="nav-btn prev-btn"
                    onClick={handlePrevImage}
                    title="前の画像"
                  >
                    ◀
                  </button>
                  <button
                    className="nav-btn next-btn"
                    onClick={handleNextImage}
                    title="次の画像"
                  >
                    ▶
                  </button>
                </>
              )}
            </div>

            <div className="image-modal-info">
              <p>
                {selectedRecord.data.images[selectedImageIndex]?.filename || `画像${selectedImageIndex + 1}`}
              </p>
              <p className="image-size">
                {selectedRecord.data.images[selectedImageIndex]?.size &&
                  `${Math.round(selectedRecord.data.images[selectedImageIndex].size / 1024)}KB`
                }
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordCalendarPage;
