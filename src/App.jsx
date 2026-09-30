import React, { useEffect } from 'react'
import { useStore } from './store'
import StatusRail from './StatusRail'
import WarehouseCanvas from './WarehouseCanvas'
import RobotPanel from './RobotPanel'
import ControlRail from './ControlRail'
import FleetStrip from './FleetStrip'
import TaskPanel from './TaskPanel'

export default function App() {
  const simulateTick = useStore(s => s.simulateTick)
  const running = useStore(s => s.running)
  const simSpeed = useStore(s => s.simSpeed)
  const showTaskPanel = useStore(s => s.showTaskPanel)

  useEffect(() => {
    if (!running) return
    const interval = setInterval(() => { simulateTick() }, 500 / simSpeed)
    return () => clearInterval(interval)
  }, [running, simSpeed, simulateTick])

  return (
    <div className="app-container">
      <StatusRail />
      <div className="main-content">
        {showTaskPanel && <TaskPanel />}
        <div className="warehouse-panel">
          <WarehouseCanvas />
          <ControlRail />
        </div>
        <RobotPanel />
      </div>
      <FleetStrip />
    </div>
  )
}
