import React from 'react'
import { useStore } from './store'

export default function TaskPanel() {
  const taskQueue = useStore(s => s.taskQueue)
  const activeTasks = useStore(s => s.activeTasks)
  const completedTasks = useStore(s => s.completedTasks)
  const taskLog = useStore(s => s.taskLog)
  const tasksCreated = useStore(s => s.tasksCreated)
  const tasksCompleted = useStore(s => s.tasksCompleted)
  const robots = useStore(s => s.robots)
  const autoGenerateTask = useStore(s => s.autoGenerateTask)
  const toggleManualTaskMode = useStore(s => s.toggleManualTaskMode)
  const manualTaskMode = useStore(s => s.manualTaskMode)
  const tick = useStore(s => s.tick)

  const [tab, setTab] = React.useState('LIVE')

  const prioColor = { EXPRESS: '#ef4444', STANDARD: '#06b6d4', COLD: '#8b5cf6' }

  return (
    <div className="task-panel">
      <div className="task-panel__header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 14 }}>📋</span>
          <span style={{ fontWeight: 600, fontSize: 13 }}>TASKS</span>
          <span className="status-badge" style={{ fontSize: 9, padding: '2px 6px' }}>
            {taskQueue.length} queued · {activeTasks.length} active · {tasksCompleted} done
          </span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          <button className="task-btn task-btn--create" onClick={autoGenerateTask}>
            ✨ Auto Task
          </button>
          <button
            className={`task-btn ${manualTaskMode ? 'task-btn--active' : 'task-btn--manual'}`}
            onClick={toggleManualTaskMode}
          >
            {manualTaskMode ? '✕ Cancel' : '📍 Manual Task'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="side-panel__tabs" style={{ paddingTop: 0 }}>
        {['LIVE', 'QUEUE', 'ACTIVE', 'DONE'].map(t => (
          <button key={t}
            className={`side-panel__tab ${tab === t ? 'side-panel__tab--active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="task-panel__body">
        {tab === 'LIVE' && (
          <div className="task-log">
            {taskLog.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: 11, padding: 8 }}>
                Waiting for tasks…
              </div>
            )}
            {taskLog.map((entry, i) => (
              <div key={i} className="task-log__entry">
                <span className="task-log__tick">t={entry.tick}</span>
                <span>{entry.msg}</span>
              </div>
            ))}
          </div>
        )}

        {tab === 'QUEUE' && (
          <div>
            {taskQueue.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: 11, padding: 8 }}>
                No tasks in queue — they'll appear automatically or create one manually.
              </div>
            )}
            {taskQueue.map(task => (
              <TaskCard key={task.id} task={task} robots={robots} prioColor={prioColor} />
            ))}
          </div>
        )}

        {tab === 'ACTIVE' && (
          <div>
            {activeTasks.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: 11, padding: 8 }}>
                No active tasks.
              </div>
            )}
            {activeTasks.map(task => {
              const bot = robots.find(r => r.id === task.assignedTo)
              return <TaskCard key={task.id} task={task} bot={bot} robots={robots} prioColor={prioColor} />
            })}
          </div>
        )}

        {tab === 'DONE' && (
          <div>
            {completedTasks.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: 11, padding: 8 }}>
                No completed tasks yet.
              </div>
            )}
            {completedTasks.map(task => (
              <div key={task.id} className="task-card task-card--done">
                <div className="task-card__header">
                  <span className="task-card__id">{task.id}</span>
                  <span className="task-card__prio" style={{ background: `${prioColor[task.priority]}22`, color: prioColor[task.priority] }}>
                    {task.priority}
                  </span>
                  <span style={{ color: '#10b981', fontSize: 10, fontWeight: 600 }}>✅ DONE</span>
                </div>
                <div className="task-card__detail">
                  Completed in {task.completedAt - task.createdAt} ticks by AMR-{String((task.assignedTo||0)+1).padStart(2,'0')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function TaskCard({ task, bot, robots, prioColor }) {
  const statusIcon = {
    QUEUED: '⏳', ASSIGNED: '🚚', PICKING: '📥', TRANSIT: '🚚', COMPLETED: '✅'
  }

  return (
    <div className="task-card">
      <div className="task-card__header">
        <span className="task-card__id">{task.id}</span>
        <span className="task-card__prio" style={{
          background: `${prioColor[task.priority]}22`,
          color: prioColor[task.priority],
        }}>
          {task.priority}
        </span>
        <span className="task-card__status">
          {task.assignedTo !== null && task.assignedTo !== undefined
            ? `→ AMR-${String(task.assignedTo+1).padStart(2,'0')}`
            : 'unassigned'}
        </span>
      </div>
      <div className="task-card__detail">
        📥 ({task.pickup[0]},{task.pickup[1]}) → 📤 ({task.dropoff[0]},{task.dropoff[1]})
      </div>
      {bot && (
        <div className="task-card__detail" style={{ color: bot.color }}>
          {bot.state} · bat {Math.round(bot.battery)}% · {bot.remainingSteps} steps left
        </div>
      )}
      {task.bids && task.bids.length > 0 && (
        <div className="task-card__bids">
          {task.bids.map((b, i) => (
            <span key={i} className="task-card__bid">
              {i === 0 ? '🏆' : ''} AMR-{String(b.robotId+1).padStart(2,'0')}: {b.cost.toFixed(1)}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
