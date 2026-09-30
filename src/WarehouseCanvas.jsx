import React from 'react'
import { useStore, WAREHOUSE_MAP, ROWS, COLS, CELL_TYPES, CELL_ICONS } from './store'

export default function WarehouseCanvas() {
  const robots = useStore(s => s.robots)
  const blockedCells = useStore(s => s.blockedCells)
  const selectedRobotId = useStore(s => s.selectedRobotId)
  const selectRobot = useStore(s => s.selectRobot)
  const handleCellClick = useStore(s => s.handleCellClick)
  const manualTaskMode = useStore(s => s.manualTaskMode)
  const pendingPickup = useStore(s => s.pendingPickup)
  const taskQueue = useStore(s => s.taskQueue)
  const activeTasks = useStore(s => s.activeTasks)

  const cellSize = 48, gap = 2
  const selectedRobot = selectedRobotId !== null ? robots.find(r => r.id === selectedRobotId) : null

  // Collect all task pickup/dropoff locations for overlay
  const taskOverlays = new Map()
  for (const t of [...taskQueue, ...activeTasks]) {
    taskOverlays.set(`${t.pickup[0]},${t.pickup[1]}`, { type: 'pickup', task: t })
    taskOverlays.set(`${t.dropoff[0]},${t.dropoff[1]}`, { type: 'dropoff', task: t })
  }

  return (
    <div className="warehouse-canvas">
      {/* Manual task hint */}
      {manualTaskMode && (
        <div style={{
          position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(245,158,11,0.15)', border: '1px solid #f59e0b',
          borderRadius: 8, padding: '6px 16px', fontSize: 12, color: '#f59e0b',
          fontFamily: "'JetBrains Mono', monospace", zIndex: 50,
        }}>
          {!pendingPickup
            ? '📦 Click a cell to set PICKUP location'
            : `✅ Pickup set at (${pendingPickup[0]},${pendingPickup[1]}) — now click DROPOFF location`
          }
        </div>
      )}

      <div
        className="warehouse-grid"
        style={{
          gridTemplateColumns: `repeat(${COLS}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${ROWS}, ${cellSize}px)`,
          width: COLS * (cellSize + gap),
          height: ROWS * (cellSize + gap),
        }}
      >
        {Array.from({ length: ROWS }, (_, r) =>
          Array.from({ length: COLS }, (_, c) => {
            const cellType = WAREHOUSE_MAP[r][c]
            const typeClass = CELL_TYPES[cellType] || 'floor'
            const icon = CELL_ICONS[cellType]
            const isBlocked = blockedCells.has(`${r},${c}`)
            const overlay = taskOverlays.get(`${r},${c}`)
            const isPendingPickup = pendingPickup && pendingPickup[0] === r && pendingPickup[1] === c

            return (
              <div
                key={`${r}-${c}`}
                className={`grid-cell grid-cell--${isBlocked ? 'blocked' : typeClass}`}
                onClick={() => { if (cellType !== 1) handleCellClick(r, c) }}
                title={`(${r},${c}) ${typeClass}${isBlocked ? ' BLOCKED' : ''}`}
                style={{
                  cursor: manualTaskMode ? 'crosshair' : 'pointer',
                  ...(isPendingPickup ? { boxShadow: '0 0 0 2px #f59e0b', background: 'rgba(245,158,11,0.2)' } : {}),
                }}
              >
                {/* Task overlay */}
                {overlay && !isBlocked && (
                  <div style={{
                    position: 'absolute', inset: 0, borderRadius: 4,
                    border: `2px dashed ${overlay.type === 'pickup' ? '#10b981' : '#3b82f6'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 16, opacity: 0.8,
                  }}>
                    {overlay.type === 'pickup' ? '📥' : '📤'}
                  </div>
                )}
                {isBlocked ? (
                  <span className="grid-cell__icon">✖</span>
                ) : icon ? (
                  <span className="grid-cell__icon">{icon}</span>
                ) : null}
              </div>
            )
          })
        )}

        {/* Path preview */}
        {selectedRobot && selectedRobot.path.slice(selectedRobot.pathIndex).map(([r,c], i) => (
          <div key={`path-${i}`} className="path-dot"
            style={{
              left: c*(cellSize+gap)+cellSize/2-3, top: r*(cellSize+gap)+cellSize/2-3,
              background: selectedRobot.color,
              opacity: 0.2 + 0.5*(1-i/(selectedRobot.path.length-selectedRobot.pathIndex||1)),
            }}
          />
        ))}

        {/* Robot sprites */}
        {robots.map(robot => {
          const stateColors = {
            'E-STOP': '#ef4444', 'YIELD': '#f59e0b', 'PICKING': '#10b981',
            'DELIVERING': '#3b82f6', 'CHARGE': '#10b981',
          }
          const borderCol = stateColors[robot.state] || robot.color

          return (
            <div key={`robot-${robot.id}`} className="robot-sprite"
              style={{ left: robot.pos[1]*(cellSize+gap), top: robot.pos[0]*(cellSize+gap) }}
            >
              {robot.intent && robot.state !== 'IDLE' && (
                <div className="intent-bubble" style={{
                  borderColor: `${borderCol}66`,
                  color: borderCol,
                }}>
                  {robot.intent}
                </div>
              )}
              <div className="robot-sprite__body"
                style={{
                  background: robot.state === 'E-STOP' ? '#4a1c1c' : robot.color,
                  boxShadow: `0 0 14px ${borderCol}44`,
                  border: selectedRobotId === robot.id ? '2px solid #fff' : `2px solid ${borderCol}`,
                  cursor: 'pointer', pointerEvents: 'auto',
                  opacity: robot.state === 'E-STOP' ? 0.5 : 1,
                }}
                onClick={(e) => { e.stopPropagation(); selectRobot(robot.id) }}
              >
                {robot.state === 'E-STOP' ? '🛑' : robot.id + 1}
              </div>
              {robot.state !== 'E-STOP' && (
                <span className="robot-sprite__direction">{robot.direction}</span>
              )}
              {/* Carrying indicator */}
              {(robot.state === 'TRANSIT_DROPOFF' || robot.state === 'DELIVERING') && (
                <span style={{ position:'absolute', top: -4, right: -4, fontSize: 12 }}>📦</span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
