import React from 'react'
import { useStore } from './store'

export default function FleetStrip() {
  const robots = useStore(s => s.robots)
  const selectedRobotId = useStore(s => s.selectedRobotId)
  const selectRobot = useStore(s => s.selectRobot)

  function batteryColor(bat) {
    if (bat > 60) return '#10b981'
    if (bat > 30) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="fleet-strip">
      <div className="fleet-strip__label">🔋 FLEET</div>
      {robots.map(robot => (
        <div
          key={robot.id}
          className={`fleet-card ${selectedRobotId === robot.id ? 'fleet-card--selected' : ''}`}
          onClick={() => selectRobot(robot.id)}
        >
          <div
            className="fleet-card__avatar"
            style={{ background: robot.color }}
          >
            {robot.id + 1}
          </div>
          <div className="fleet-card__info">
            <div className="fleet-card__name">{robot.name}</div>
            <div className="fleet-card__state">
              {robot.state === 'E-STOP' ? '🛑 E-STOP' : robot.state}
            </div>
          </div>
          <div className="fleet-card__battery">
            <div className="fleet-card__battery-bar">
              <div
                className="fleet-card__battery-fill"
                style={{
                  width: `${robot.battery}%`,
                  background: batteryColor(robot.battery),
                }}
              />
            </div>
            <div className="fleet-card__battery-text">
              {Math.round(robot.battery)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
