import React from 'react'
import { useStore } from './store'

export default function RobotPanel() {
  const selectedRobotId = useStore(s => s.selectedRobotId)
  const robots = useStore(s => s.robots)
  const selectedTab = useStore(s => s.selectedTab)
  const setTab = useStore(s => s.setTab)
  const deselectRobot = useStore(s => s.deselectRobot)

  if (selectedRobotId === null) return null
  const robot = robots.find(r => r.id === selectedRobotId)
  if (!robot) return null

  const tabs = ['TRACES', 'TERMINAL', 'MESH', 'BUILD']
  const stateEmoji = {
    'IDLE': '⏸', 'TRANSIT_PICKUP': '🚚', 'PICKING': '📥',
    'TRANSIT_DROPOFF': '📦', 'DELIVERING': '📤', 'CHARGE': '⚡',
    'YIELD': '⏳', 'REROUTE': '↻', 'E-STOP': '🛑',
  }

  return (
    <div className="side-panel">
      <div className="side-panel__header">
        <div className="side-panel__robot-info">
          <div className="side-panel__robot-avatar" style={{ background: robot.color }}>
            {robot.state === 'E-STOP' ? '🛑' : robot.id + 1}
          </div>
          <div>
            <div className="side-panel__robot-name">{robot.name}</div>
            <div className="side-panel__robot-status">
              <span className={`status-dot status-dot--${robot.state === 'E-STOP' ? 'red' : robot.state === 'YIELD' ? 'amber' : 'green'}`}
                    style={{ width: 6, height: 6 }} />
              {stateEmoji[robot.state] || ''} {robot.state} · ({robot.pos[0]},{robot.pos[1]})
            </div>
          </div>
        </div>
        <button className="side-panel__close" onClick={deselectRobot}>✕</button>
      </div>

      {/* Stats */}
      <div style={{ padding: '8px 12px' }}>
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-card__value" style={{ color: robot.battery > 30 ? '#10b981' : '#ef4444' }}>
              {Math.round(robot.battery)}%
            </div>
            <div className="stat-card__label">Battery</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__value" style={{ color: '#06b6d4' }}>
              {robot.priorityClass}
            </div>
            <div className="stat-card__label">Class</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__value" style={{ color: '#8b5cf6' }}>
              {robot.remainingSteps}
            </div>
            <div className="stat-card__label">Steps</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__value" style={{ color: '#f59e0b' }}>
              {robot.tasksFinished}
            </div>
            <div className="stat-card__label">Done</div>
          </div>
        </div>

        {/* Current task */}
        {robot.currentTask && (
          <div style={{
            background: 'var(--bg-primary)', borderRadius: 6, padding: '6px 10px',
            fontSize: 11, fontFamily: "'JetBrains Mono', monospace",
            border: '1px solid rgba(6,182,212,0.2)', marginTop: 4,
          }}>
            <div style={{ color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: 2 }}>
              📋 {robot.currentTask.id} ({robot.currentTask.priority})
            </div>
            <div style={{ color: 'var(--text-muted)' }}>
              📥 ({robot.currentTask.pickup[0]},{robot.currentTask.pickup[1]}) → 📤 ({robot.currentTask.dropoff[0]},{robot.currentTask.dropoff[1]})
            </div>
          </div>
        )}
      </div>

      <div className="side-panel__tabs">
        {tabs.map(tab => (
          <button key={tab}
            className={`side-panel__tab ${selectedTab === tab ? 'side-panel__tab--active' : ''}`}
            onClick={() => setTab(tab)}>
            {tab === 'TRACES' && '🧾'} {tab === 'TERMINAL' && '📟'}
            {tab === 'MESH' && '📡'} {tab === 'BUILD' && '🔖'}
            {' '}{tab}
          </button>
        ))}
      </div>

      <div className="side-panel__body">
        {selectedTab === 'TRACES' && <TracesTab traces={robot.traces} />}
        {selectedTab === 'TERMINAL' && <TerminalTab lines={robot.terminalLog} />}
        {selectedTab === 'MESH' && <MeshTab messages={robot.meshMessages} />}
        {selectedTab === 'BUILD' && <BuildTab robot={robot} />}
      </div>
    </div>
  )
}

function TracesTab({ traces }) {
  if (traces.length === 0) return <div style={{ color: 'var(--text-muted)', fontSize: 12, padding: 8 }}>No traces yet…</div>
  return traces.map((t, i) => (
    <div key={i} className={`trace-entry trace-entry--${t.className}`}>
      <div className="trace-entry__header">
        <span className="trace-entry__type">{t.type}</span>
        <span>t={t.tick}</span>
      </div>
      <div className="trace-entry__detail">{t.detail}</div>
    </div>
  ))
}

function TerminalTab({ lines }) {
  if (lines.length === 0) return <div style={{ color: 'var(--text-muted)', fontSize: 12, padding: 8 }}>Waiting…</div>
  return (
    <div className="terminal-log">
      {lines.map((line, i) => (
        <div key={i} className={`terminal-line terminal-line--${line.level}`}>{line.text}</div>
      ))}
    </div>
  )
}

function MeshTab({ messages }) {
  if (messages.length === 0) return <div style={{ color: 'var(--text-muted)', fontSize: 12, padding: 8 }}>No messages…</div>
  return messages.map((msg, i) => (
    <div key={i} className="mesh-message">
      <span className={`mesh-message__type mesh-message__type--${msg.type}`}>{msg.type}</span>
      <span style={{ color: 'var(--text-secondary)' }}>{msg.from}</span>
      <span style={{ color: 'var(--text-muted)', flex: 1 }}>{msg.content}</span>
    </div>
  ))
}

function BuildTab({ robot }) {
  return (
    <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>
      <div className="trace-entry">
        <div className="trace-entry__header"><span className="trace-entry__type">IDENTITY</span></div>
        <div className="trace-entry__detail">
          id: {robot.name}<br/>
          class: {robot.priorityClass}<br/>
          chassis: differential drive<br/>
          footprint: 0.6m × 0.4m<br/>
          total distance: {robot.totalDistanceTravelled} cells<br/>
          tasks completed: {robot.tasksFinished}
        </div>
      </div>
      <div className="trace-entry">
        <div className="trace-entry__header"><span className="trace-entry__type">EDGE ENGINE</span></div>
        <div className="trace-entry__detail">
          target: Raspberry Pi 5<br/>
          planner: A* + D* Lite<br/>
          arbiter: deterministic priority<br/>
          AI advisor: ON<br/>
          radio range: 18m<br/>
          tick rate: 10 Hz
        </div>
      </div>
      <div className="trace-entry">
        <div className="trace-entry__header"><span className="trace-entry__type">FIRMWARE</span></div>
        <div className="trace-entry__detail">
          hash: a3f7c21e<br/>
          version: 1.0.0-alpha<br/>
          built: 2026-09-29
        </div>
      </div>
    </div>
  )
}
