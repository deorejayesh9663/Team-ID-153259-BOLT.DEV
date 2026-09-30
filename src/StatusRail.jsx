import React from 'react'
import { useStore } from './store'

export default function StatusRail() {
  const tick = useStore(s => s.tick)
  const running = useStore(s => s.running)
  const robots = useStore(s => s.robots)
  const collisions = useStore(s => s.collisions)
  const autonomyOn = useStore(s => s.autonomyOn)
  const messagesPerSec = useStore(s => s.messagesPerSec)

  const aliveCount = robots.filter(r => r.state !== 'E-STOP').length
  const totalCount = robots.length

  // Format tick as time
  const seconds = tick % 60
  const minutes = Math.floor(tick / 60) % 60
  const hours = Math.floor(tick / 3600)
  const timeStr = `${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`

  return (
    <div className="status-rail">
      <div className="status-rail__left">
        <div className="status-rail__logo">VYUHA</div>
        <div className="status-rail__divider" />

        <div className="status-badge">
          <span className={`status-dot ${autonomyOn ? 'status-dot--green' : 'status-dot--amber'}`} />
          AUTONOMY {autonomyOn ? 'ON' : 'OFF'}
        </div>

        <div className="status-badge">
          <span className={`status-dot ${aliveCount === totalCount ? 'status-dot--green' : 'status-dot--amber'}`} />
          MESH {aliveCount}/{totalCount}
        </div>

        <div className="status-badge">
          <span className={`status-dot ${collisions === 0 ? 'status-dot--green' : 'status-dot--red'}`} />
          COLLISIONS {collisions}
        </div>

        <div className="status-badge">
          <span className="status-dot status-dot--cyan" />
          MSG/s {messagesPerSec}
        </div>
      </div>

      <div className="status-rail__right">
        <div className="status-badge">
          {running ? '▶' : '⏸'} {running ? 'RUNNING' : 'PAUSED'}
        </div>
        <div className="status-rail__clock">🕐 {timeStr}</div>
      </div>
    </div>
  )
}
