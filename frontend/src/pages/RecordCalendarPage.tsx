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
      const dateStr = current.toISOString().split('T')[0];
      const dayRecords = records.filter(r => r.recordDate.startsWith(dateStr));
      const daySchedules = schedules.filter(s => s.scheduledAt.startsWith(dateStr));

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
                    <div key={record.id} className="record-item" onClick={() => onViewRecord(record)}>
                      <div className="record-type-icon">
                        {record.recordType === 'observation' ? '🔍' :
                         record.recordType === 'experiment' ? '⚗️' : '📝'}
                      </div>
                      <div className="record-content">
                        <div className="record-title">{record.title}</div>
                        <div className="record-preview">{record.content.substring(0, 50)}...</div>
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
    </div>
  );
};

export default RecordCalendarPage;
