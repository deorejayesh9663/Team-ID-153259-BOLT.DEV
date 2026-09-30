import React from 'react'
import { useStore } from './store'

export default function ControlRail() {
  const running = useStore(s => s.running)
  const toggleRunning = useStore(s => s.toggleRunning)
  const simSpeed = useStore(s => s.simSpeed)
  const setSimSpeed = useStore(s => s.setSimSpeed)
  const autonomyOn = useStore(s => s.autonomyOn)
  const toggleAutonomy = useStore(s => s.toggleAutonomy)
  const aiAdvisorOn = useStore(s => s.aiAdvisorOn)
  const toggleAiAdvisor = useStore(s => s.toggleAiAdvisor)
  const selectedRobotId = useStore(s => s.selectedRobotId)
  const eStopRobot = useStore(s => s.eStopRobot)
  const resumeRobot = useStore(s => s.resumeRobot)
  const sendToCharge = useStore(s => s.sendToCharge)
  const robots = useStore(s => s.robots)
  const tick = useStore(s => s.tick)
  const tasksCompleted = useStore(s => s.tasksCompleted)
  const showTaskPanel = useStore(s => s.showTaskPanel)
  const toggleTaskPanel = useStore(s => s.toggleTaskPanel)
  const deadlocksResolved = useStore(s => s.deadlocksResolved)

  const selectedRobot = selectedRobotId !== null ? robots.find(r => r.id === selectedRobotId) : null
  const speeds = [0.5, 1, 2, 4]

  return (
    <div className="control-rail">
      <button className={`control-btn ${running ? 'control-btn--active' : ''}`}
        onClick={toggleRunning}>
        {running ? '⏸ Pause' : '▶ Resume'}
      </button>

      <div className="sim-speed">
        {speeds.map(sp => (
          <button key={sp} className="sim-speed__btn"
            onClick={() => setSimSpeed(sp)}
            style={simSpeed === sp ? { background: 'rgba(6,182,212,0.2)', color: '#06b6d4' } : {}}>
            {sp}×
          </button>
        ))}
      </div>

      <div className="status-rail__divider" style={{ height: 20, margin: '0 6px' }} />

      <button className={`control-btn ${autonomyOn ? 'control-btn--active' : ''}`}
        onClick={toggleAutonomy}>
        🟢 Autonomy {autonomyOn ? 'ON' : 'OFF'}
      </button>

      <button className={`control-btn ${aiAdvisorOn ? 'control-btn--active' : ''}`}
        onClick={toggleAiAdvisor}>
        🧠 AI {aiAdvisorOn ? 'ON' : 'OFF'}
      </button>

      <div className="status-rail__divider" style={{ height: 20, margin: '0 6px' }} />

      {/* Robot-specific controls */}
      {selectedRobot && (
        <>
          {selectedRobot.state === 'E-STOP' ? (
            <button className="control-btn" style={{ borderColor: '#10b981', color: '#10b981' }}
              onClick={() => resumeRobot(selectedRobotId)}>
              ▶ Resume {selectedRobot.name}
            </button>
          ) : (
            <button className="control-btn control-btn--danger"
              onClick={() => eStopRobot(selectedRobotId)}>
              🛑 E-Stop {selectedRobot.name}
            </button>
          )}
          <button className="control-btn" style={{ borderColor: '#10b981', color: '#10b981' }}
            onClick={() => sendToCharge(selectedRobotId)}>
            ⚡ Charge {selectedRobot.name}
          </button>
        </>
      )}

      <button className="control-btn control-btn--warning"
        title="Click any floor cell to drop/remove an obstacle">
        📦 Drop Obstacle
      </button>

      <button className={`control-btn ${showTaskPanel ? 'control-btn--active' : ''}`}
        onClick={toggleTaskPanel}>
        📋 Tasks
      </button>

      <div className="control-rail__spacer" />

      <div className="status-badge" style={{ fontSize: 10 }}>✅ {tasksCompleted}</div>
      <div className="status-badge" style={{ fontSize: 10 }}>⏱ {tick}</div>
    </div>
  )
}
