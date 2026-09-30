import { create } from 'zustand'

// ─── WAREHOUSE MAP ───
// 0=floor, 1=rack, 2=dock-in, 3=dock-out, 4=pick, 5=charge, 6=junction
const WAREHOUSE_MAP = [
  [2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,1,1,1,1,0,6,1,1,1,1,0,6,1,1,1,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,1,1,1,1,0,6,1,1,1,1,0,6,1,1,1,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,5,5,0,5,5],
]

const ROWS = WAREHOUSE_MAP.length
const COLS = WAREHOUSE_MAP[0].length

const CELL_TYPES = { 0:'floor', 1:'rack', 2:'dock', 3:'dock', 4:'pick', 5:'charge', 6:'junction' }
const CELL_ICONS = { 2:'🚪', 3:'🚪', 4:'📦', 5:'⚡', 6:'◆' }

// ─── HELPERS ───
function getWalkableCells() {
  const cells = []
  for (let r = 0; r < ROWS; r++)
    for (let c = 0; c < COLS; c++)
      if (WAREHOUSE_MAP[r][c] !== 1) cells.push([r, c])
  return cells
}

function getCellsOfType(type) {
  const cells = []
  for (let r = 0; r < ROWS; r++)
    for (let c = 0; c < COLS; c++)
      if (WAREHOUSE_MAP[r][c] === type) cells.push([r, c])
  return cells
}

const walkable = getWalkableCells()
const pickStations = getCellsOfType(4)
const dockIn = getCellsOfType(2)
const dockOut = getCellsOfType(3)
const chargeBays = getCellsOfType(5)

function randomFrom(arr) { return arr[Math.floor(Math.random() * arr.length)] }

function dist(a, b) { return Math.abs(a[0]-b[0]) + Math.abs(a[1]-b[1]) }

// ─── A* PATHFINDING ───
function findPath(start, goal, blocked = new Set(), robotPositions = []) {
  if (!start || !goal) return [start || [0,0]]
  const key = (r,c) => `${r},${c}`
  const occupied = new Set(robotPositions.map(p => key(p[0],p[1])))
  const open = [{ pos: start, g: 0, f: dist(start, goal), path: [start] }]
  const closed = new Set()

  let iterations = 0
  while (open.length > 0 && iterations < 2000) {
    iterations++
    open.sort((a,b) => a.f - b.f)
    const cur = open.shift()
    const k = key(...cur.pos)
    if (closed.has(k)) continue
    closed.add(k)
    if (cur.pos[0] === goal[0] && cur.pos[1] === goal[1]) return cur.path

    for (const [dr, dc] of [[-1,0],[1,0],[0,-1],[0,1]]) {
      const nr = cur.pos[0]+dr, nc = cur.pos[1]+dc
      if (nr<0||nr>=ROWS||nc<0||nc>=COLS) continue
      if (WAREHOUSE_MAP[nr][nc] === 1) continue
      if (blocked.has(key(nr,nc))) continue
      if (closed.has(key(nr,nc))) continue
      const g = cur.g + 1
      open.push({ pos:[nr,nc], g, f: g + dist([nr,nc], goal), path:[...cur.path, [nr,nc]] })
    }
  }
  return [start]
}

function getDirection(from, to) {
  if (!from || !to) return '→'
  const dr = to[0]-from[0], dc = to[1]-from[1]
  if (Math.abs(dc) >= Math.abs(dr)) return dc > 0 ? '→' : '←'
  return dr > 0 ? '↓' : '↑'
}

// ─── ROBOT COLORS ───
const ROBOT_COLORS = ['#06b6d4','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899']

// ─── TASK PRIORITIES ───
const PRIORITIES = ['STANDARD','STANDARD','STANDARD','EXPRESS','COLD']

// ─── TASK ID GENERATOR ───
let taskIdCounter = 1000

function generateTaskId() {
  taskIdCounter++
  return `TASK-${String(taskIdCounter).padStart(4,'0')}`
}

// ─── AI BRAIN: BID CALCULATION ───
function computeBid(robot, task, blocked) {
  if (robot.state === 'E-STOP' || robot.state === 'CHARGE') return Infinity
  if (robot.battery < 20) return Infinity

  const pathToPickup = findPath(robot.pos, task.pickup, blocked)
  const pathToDropoff = findPath(task.pickup, task.dropoff, blocked)
  const totalDist = pathToPickup.length + pathToDropoff.length

  // w1*distance + w2*(1/battery) + w3*priority_mismatch + w4*current_load
  const w1 = 1.0, w2 = 50, w3 = 5, w4 = 10
  const batteryPenalty = w2 * (1 / Math.max(robot.battery, 1))
  const priorityBonus = task.priority === 'EXPRESS' && robot.priorityClass === 'EXPRESS' ? -10 : 0
  const loadPenalty = robot.currentTask ? w4 : 0

  return w1 * totalDist + batteryPenalty + priorityBonus + loadPenalty
}

// ─── AI BRAIN: CONFLICT ARBITER ───
function arbitrate(robotA, robotB) {
  const prioMap = { 'EXPRESS': 3, 'STANDARD': 2, 'COLD': 1, 'IDLE': 0 }
  const pa = prioMap[robotA.missionPriority || 'STANDARD'] || 0
  const pb = prioMap[robotB.missionPriority || 'STANDARD'] || 0
  if (pa !== pb) return pa > pb ? 'A' : 'B'
  if (robotA.remainingSteps !== robotB.remainingSteps)
    return robotA.remainingSteps < robotB.remainingSteps ? 'A' : 'B'
  return robotA.id < robotB.id ? 'A' : 'B'
}

// ─── TRACE & LOG GENERATORS ───
function makeTrace(type, detail, tick) {
  const classMap = { CONFLICT:'conflict', YIELD:'yield', WIN:'win', 'AI ADVICE':'ai', TASK:'win', REPLAN:'conflict', AUCTION:'ai' }
  return { type, className: classMap[type] || 'ai', detail, tick }
}

function makeTermLine(level, text, tick) {
  return { level, text: `[t=${String(tick).padStart(5)}] ${text}` }
}

function makeMeshMsg(type, from, content, tick) {
  return { type, from, content, tick }
}


// ═══════════════════════════════════════
// ═══════ ZUSTAND STORE ═══════════════
// ═══════════════════════════════════════
const useStore = create((set, get) => ({
  // ─── CLOCK ───
  tick: 0,
  running: true,
  simSpeed: 1,

  // ─── GLOBAL STATS ───
  collisions: 0,
  tasksCompleted: 0,
  tasksCreated: 0,
  deadlocksResolved: 0,
  messagesPerSec: 0,

  // ─── TASKS ───
  taskQueue: [],        // unassigned tasks waiting for bids
  activeTasks: [],      // tasks currently being executed
  completedTasks: [],   // finished tasks
  taskLog: [],          // auction log entries

  // ─── ROBOTS ───
  robots: Array.from({ length: 6 }, (_, i) => {
    const spawnPoints = [[1,0],[1,5],[1,12],[1,17],[10,0],[10,12]]
    return {
      id: i,
      name: `AMR-${String(i+1).padStart(2,'0')}`,
      color: ROBOT_COLORS[i],
      pos: spawnPoints[i] || [1, i*3],
      goal: null,
      path: [],
      pathIndex: 0,
      state: 'IDLE',          // IDLE, TRANSIT_PICKUP, PICKING, TRANSIT_DROPOFF, DELIVERING, CHARGE, YIELD, REROUTE, E-STOP
      battery: 50 + Math.floor(Math.random() * 50),
      priorityClass: i < 2 ? 'EXPRESS' : 'STANDARD',
      missionPriority: 'IDLE',
      direction: '→',
      intent: 'standby',
      currentTask: null,
      remainingSteps: 0,
      yieldingTo: null,
      yieldTimer: 0,
      pickTimer: 0,
      deliverTimer: 0,
      traces: [],
      meshMessages: [],
      terminalLog: [],
      totalDistanceTravelled: 0,
      tasksFinished: 0,
    }
  }),

  // ─── UI STATE ───
  selectedRobotId: null,
  selectedTab: 'TRACES',
  blockedCells: new Set(),
  autonomyOn: true,
  aiAdvisorOn: true,
  showTaskPanel: true,
  manualTaskMode: false,  // when true, next 2 cell clicks = pickup + dropoff

  // ─── MANUAL TASK CREATION STATE ───
  pendingPickup: null,

  // ═══════ ACTIONS ═══════

  toggleRunning: () => set(s => ({ running: !s.running })),
  setSimSpeed: (sp) => set({ simSpeed: sp }),
  selectRobot: (id) => set({ selectedRobotId: id }),
  deselectRobot: () => set({ selectedRobotId: null }),
  setTab: (tab) => set({ selectedTab: tab }),
  toggleAutonomy: () => set(s => ({ autonomyOn: !s.autonomyOn })),
  toggleAiAdvisor: () => set(s => ({ aiAdvisorOn: !s.aiAdvisorOn })),
  toggleTaskPanel: () => set(s => ({ showTaskPanel: !s.showTaskPanel })),
  toggleManualTaskMode: () => set(s => ({ manualTaskMode: !s.manualTaskMode, pendingPickup: null })),

  // Block/unblock a cell
  toggleBlockedCell: (r, c) => set(s => {
    const key = `${r},${c}`
    const next = new Set(s.blockedCells)
    if (next.has(key)) next.delete(key); else next.add(key)
    return { blockedCells: next }
  }),

  // E-Stop a robot
  eStopRobot: (id) => set(s => {
    const robots = s.robots.map(r => {
      if (r.id !== id) return r
      // Release its current task back to queue
      const released = r.currentTask
      return { ...r, state: 'E-STOP', path: [], goal: null, currentTask: null, intent: '🛑 E-STOP', missionPriority: 'IDLE' }
    })
    // Re-queue the released task
    let taskQueue = [...s.taskQueue]
    const bot = s.robots.find(r => r.id === id)
    if (bot?.currentTask) {
      taskQueue.push({ ...bot.currentTask, status: 'QUEUED', assignedTo: null })
    }
    return { robots, taskQueue }
  }),

  // Resume a stopped robot
  resumeRobot: (id) => set(s => ({
    robots: s.robots.map(r => r.id === id ? { ...r, state: 'IDLE', intent: 'standby' } : r)
  })),

  // Send robot to charge manually
  sendToCharge: (id) => set(s => {
    const robot = s.robots.find(r => r.id === id)
    if (!robot || robot.state === 'E-STOP') return {}
    const nearest = chargeBays.reduce((best, bay) =>
      dist(robot.pos, bay) < dist(robot.pos, best) ? bay : best, chargeBays[0])
    const path = findPath(robot.pos, nearest, s.blockedCells)
    return {
      robots: s.robots.map(r => r.id === id ? {
        ...r, state: 'CHARGE', goal: nearest, path, pathIndex: 0,
        currentTask: null, intent: `heading to charge ⚡`, missionPriority: 'IDLE'
      } : r)
    }
  }),

  // Create a task manually
  createManualTask: (pickup, dropoff, priority = 'STANDARD') => set(s => {
    const task = {
      id: generateTaskId(),
      pickup,
      dropoff,
      priority,
      status: 'QUEUED',
      assignedTo: null,
      createdAt: s.tick,
      completedAt: null,
      bids: [],
    }
    return {
      taskQueue: [...s.taskQueue, task],
      tasksCreated: s.tasksCreated + 1,
      taskLog: [{ tick: s.tick, msg: `📦 ${task.id} created (${priority}) pickup=(${pickup}) drop=(${dropoff})` }, ...s.taskLog].slice(0, 50),
      manualTaskMode: false,
      pendingPickup: null,
    }
  }),

  // Handle cell click for manual task
  handleCellClick: (r, c) => {
    const s = get()
    if (s.manualTaskMode) {
      if (!s.pendingPickup) {
        set({ pendingPickup: [r, c] })
      } else {
        // Create task with pending pickup and this as dropoff
        get().createManualTask(s.pendingPickup, [r, c], 'STANDARD')
      }
    } else {
      get().toggleBlockedCell(r, c)
    }
  },

  // Auto-generate a random task
  autoGenerateTask: () => set(s => {
    const pickup = randomFrom(pickStations) || randomFrom(dockIn)
    const dropoff = randomFrom(dockOut) || randomFrom(walkable.filter(([r,c]) => WAREHOUSE_MAP[r][c] === 0))
    const priority = randomFrom(PRIORITIES)
    const task = {
      id: generateTaskId(),
      pickup,
      dropoff,
      priority,
      status: 'QUEUED',
      assignedTo: null,
      createdAt: s.tick,
      completedAt: null,
      bids: [],
    }
    return {
      taskQueue: [...s.taskQueue, task],
      tasksCreated: s.tasksCreated + 1,
      taskLog: [{ tick: s.tick, msg: `📦 ${task.id} auto-created (${priority})` }, ...s.taskLog].slice(0, 50),
    }
  }),


  // ═══════════════════════════════════
  // ═══════ MAIN SIMULATION TICK ═════
  // ═══════════════════════════════════
  simulateTick: () => {
    const s = get()
    if (!s.running) return

    const tick = s.tick + 1
    let { taskQueue, activeTasks, completedTasks, tasksCompleted, deadlocksResolved, taskLog } = s
    const { blockedCells, autonomyOn, aiAdvisorOn } = s

    taskQueue = [...taskQueue]
    activeTasks = [...activeTasks]
    completedTasks = [...completedTasks]
    taskLog = [...taskLog]

    // ─── AUTO TASK GENERATION (every ~30 ticks) ───
    if (tick % 30 === 0 && taskQueue.length < 4 && autonomyOn) {
      const pickup = randomFrom(pickStations) || randomFrom(dockIn)
      const dropoff = randomFrom(dockOut)
      const priority = randomFrom(PRIORITIES)
      if (pickup && dropoff) {
        const task = {
          id: generateTaskId(), pickup, dropoff, priority,
          status: 'QUEUED', assignedTo: null, createdAt: tick, completedAt: null, bids: [],
        }
        taskQueue.push(task)
        taskLog.unshift({ tick, msg: `📦 ${task.id} appeared at pick station (${priority})` })
      }
    }

    // ─── TASK AUCTION (Contract Net) ───
    const newTaskQueue = []
    for (const task of taskQueue) {
      if (task.status !== 'QUEUED') { newTaskQueue.push(task); continue }

      // Collect bids from all available robots
      const bids = s.robots
        .filter(r => r.state !== 'E-STOP' && !r.currentTask && r.battery > 20)
        .map(r => ({ robotId: r.id, cost: computeBid(r, task, blockedCells) }))
        .filter(b => b.cost < Infinity)
        .sort((a, b) => a.cost - b.cost)

      if (bids.length > 0) {
        const winner = bids[0]
        task.status = 'ASSIGNED'
        task.assignedTo = winner.robotId
        task.bids = bids.slice(0, 3) // keep top 3 for display
        activeTasks.push(task)
        taskLog.unshift({ tick, msg: `🏆 ${task.id} → AMR-${String(winner.robotId+1).padStart(2,'0')} (bid=${winner.cost.toFixed(1)}, ${bids.length} bidders)` })
      } else {
        newTaskQueue.push(task) // no bidder, keep in queue
      }
    }
    taskQueue = newTaskQueue

    // ─── UPDATE EACH ROBOT ───
    let robots = s.robots.map(robot => {
      if (robot.state === 'E-STOP') return robot

      let { pos, goal, path, pathIndex, state, battery, direction, intent,
            currentTask, remainingSteps, yieldingTo, yieldTimer,
            pickTimer, deliverTimer, traces, meshMessages, terminalLog,
            totalDistanceTravelled, tasksFinished, missionPriority } = robot

      traces = [...traces]
      meshMessages = [...meshMessages]
      terminalLog = [...terminalLog]

      // ── Battery drain / charge ──
      if (state === 'CHARGE' && WAREHOUSE_MAP[pos[0]]?.[pos[1]] === 5) {
        battery = Math.min(100, battery + 0.8)
        intent = `charging ${Math.round(battery)}%▲`
        if (battery >= 95) {
          state = 'IDLE'
          goal = null; path = []; pathIndex = 0
          intent = 'fully charged ✓'
          terminalLog.unshift(makeTermLine('success', `battery full — resuming operations`, tick))
        }
      } else {
        battery = Math.max(0, battery - 0.04)
      }

      // ── Force charge if critically low ──
      if (battery < 12 && state !== 'CHARGE' && state !== 'E-STOP') {
        const nearest = chargeBays.reduce((best, bay) => dist(pos, bay) < dist(pos, best) ? bay : best, chargeBays[0])
        goal = nearest
        path = findPath(pos, nearest, blockedCells)
        pathIndex = 0
        state = 'CHARGE'
        intent = `⚠ low battery → docking`
        missionPriority = 'IDLE'
        // Release current task
        if (currentTask) {
          taskQueue.push({ ...currentTask, status: 'QUEUED', assignedTo: null })
          taskLog.unshift({ tick, msg: `🔋 ${currentTask.id} released by AMR-${String(robot.id+1).padStart(2,'0')} (low battery)` })
          currentTask = null
        }
        traces.unshift(makeTrace('REPLAN', `battery critical ${Math.round(battery)}% → heading to charge bay`, tick))
      }

      // ── Assign task from activeTasks ──
      if (!currentTask && state === 'IDLE' && autonomyOn) {
        const myTask = activeTasks.find(t => t.assignedTo === robot.id && t.status === 'ASSIGNED')
        if (myTask) {
          currentTask = myTask
          goal = myTask.pickup
          path = findPath(pos, myTask.pickup, blockedCells)
          pathIndex = 0
          state = 'TRANSIT_PICKUP'
          missionPriority = myTask.priority
          intent = `📦 heading to pickup`
          traces.unshift(makeTrace('TASK', `assigned ${myTask.id} (${myTask.priority}) → pickup (${myTask.pickup})`, tick))
          terminalLog.unshift(makeTermLine('info', `[task] ${myTask.id} assigned · heading to pickup`, tick))
          meshMessages.unshift(makeMeshMsg('intent', robot.name, `claiming ${myTask.id}`, tick))
        }
      }

      // ── YIELD TIMER ──
      if (state === 'YIELD') {
        yieldTimer--
        if (yieldTimer <= 0) {
          state = currentTask ? (goal === currentTask?.pickup ? 'TRANSIT_PICKUP' : 'TRANSIT_DROPOFF') : 'IDLE'
          yieldingTo = null
          intent = currentTask ? `resuming after yield` : 'standby'
        }
      }

      // ── PICKING TIMER ──
      if (state === 'PICKING') {
        pickTimer--
        intent = `picking up… ${pickTimer} ticks left`
        if (pickTimer <= 0) {
          // Head to dropoff
          if (currentTask) {
            goal = currentTask.dropoff
            path = findPath(pos, currentTask.dropoff, blockedCells)
            pathIndex = 0
            state = 'TRANSIT_DROPOFF'
            intent = `📦 carrying → dropoff`
            traces.unshift(makeTrace('TASK', `picked up → heading to dropoff (${currentTask.dropoff})`, tick))
            terminalLog.unshift(makeTermLine('success', `[task] pickup complete · transit to dropoff`, tick))
          }
        }
      }

      // ── DELIVERING TIMER ──
      if (state === 'DELIVERING') {
        deliverTimer--
        intent = `delivering… ${deliverTimer} ticks left`
        if (deliverTimer <= 0) {
          // Task complete!
          if (currentTask) {
            const finished = { ...currentTask, status: 'COMPLETED', completedAt: tick }
            completedTasks.unshift(finished)
            activeTasks = activeTasks.filter(t => t.id !== currentTask.id)
            tasksCompleted++
            tasksFinished++
            taskLog.unshift({ tick, msg: `✅ ${currentTask.id} completed by AMR-${String(robot.id+1).padStart(2,'0')} in ${tick - currentTask.createdAt} ticks` })
            traces.unshift(makeTrace('TASK', `✅ ${currentTask.id} COMPLETED`, tick))
            terminalLog.unshift(makeTermLine('success', `[task] ${currentTask.id} delivered ✓`, tick))
            meshMessages.unshift(makeMeshMsg('intent', robot.name, `RELEASE ${currentTask.id}`, tick))
          }
          currentTask = null
          goal = null; path = []; pathIndex = 0
          state = 'IDLE'
          missionPriority = 'IDLE'
          intent = 'standby — awaiting next task'
        }
      }

      // ── MOVEMENT (for TRANSIT states and CHARGE heading) ──
      if ((state === 'TRANSIT_PICKUP' || state === 'TRANSIT_DROPOFF' || (state === 'CHARGE' && pathIndex < path.length)) && path.length > 0 && pathIndex < path.length) {
        const nextPos = path[pathIndex]
        if (!nextPos) { pathIndex++; }
        else {
          const cellKey = `${nextPos[0]},${nextPos[1]}`

          // Check if blocked
          if (blockedCells.has(cellKey)) {
            // D* Lite style replan
            const newPath = findPath(pos, goal, blockedCells)
            path = newPath; pathIndex = 0
            state = state === 'CHARGE' ? 'CHARGE' : (currentTask && goal === currentTask.pickup ? 'TRANSIT_PICKUP' : 'TRANSIT_DROPOFF')
            traces.unshift(makeTrace('REPLAN', `cell ${cellKey} blocked → replanned path (${newPath.length} steps)`, tick))
            terminalLog.unshift(makeTermLine('warn', `[planner] D* Lite replan · blocked cell ${cellKey}`, tick))
            meshMessages.unshift(makeMeshMsg('blocked', robot.name, `cell ${cellKey} TTL=5`, tick))
          } else {
            // Check collision with other robot
            const otherRobot = s.robots.find(o =>
              o.id !== robot.id && o.pos[0] === nextPos[0] && o.pos[1] === nextPos[1] && o.state !== 'E-STOP'
            )
            if (otherRobot) {
              // Arbitrate
              const winner = arbitrate(
                { ...robot, remainingSteps: path.length - pathIndex },
                { ...otherRobot, remainingSteps: (otherRobot.path?.length || 0) - (otherRobot.pathIndex || 0) }
              )
              if (winner === 'A') {
                // We win — proceed
                direction = getDirection(pos, nextPos)
                pos = nextPos; pathIndex++; totalDistanceTravelled++
                traces.unshift(makeTrace('WIN', `priority WIN vs ${otherRobot.name} · proceed`, tick))
                meshMessages.unshift(makeMeshMsg('reserve', robot.name, `cell (${nextPos[0]},${nextPos[1]})`, tick))
              } else {
                // We yield
                state = 'YIELD'
                yieldTimer = 3 + Math.floor(Math.random() * 3)
                yieldingTo = otherRobot.id
                intent = `yielding to ${otherRobot.name}`
                traces.unshift(makeTrace('YIELD', `YIELD to ${otherRobot.name} · hold ${yieldTimer} ticks · reason RW_PRIO`, tick))
                meshMessages.unshift(makeMeshMsg('yield', robot.name, `to ${otherRobot.name} · ${yieldTimer}t`, tick))
                terminalLog.unshift(makeTermLine('warn', `[arbiter] yielding to ${otherRobot.name}`, tick))
              }
            } else {
              // Move freely
              direction = getDirection(pos, nextPos)
              pos = nextPos; pathIndex++; totalDistanceTravelled++
            }
          }

          // Arrived at pickup?
          if (state === 'TRANSIT_PICKUP' && currentTask && pos[0] === currentTask.pickup[0] && pos[1] === currentTask.pickup[1]) {
            state = 'PICKING'
            pickTimer = 5 + Math.floor(Math.random() * 3)
            intent = `picking up 📦 (${pickTimer} ticks)`
            terminalLog.unshift(makeTermLine('info', `[task] arrived at pickup · loading`, tick))
          }

          // Arrived at dropoff?
          if (state === 'TRANSIT_DROPOFF' && currentTask && pos[0] === currentTask.dropoff[0] && pos[1] === currentTask.dropoff[1]) {
            state = 'DELIVERING'
            deliverTimer = 4
            intent = `delivering 📦 (${deliverTimer} ticks)`
            terminalLog.unshift(makeTermLine('info', `[task] arrived at dropoff · unloading`, tick))
          }
        }
      }

      // ── IDLE intent ──
      if (state === 'IDLE') intent = 'standby'

      remainingSteps = Math.max(0, path.length - pathIndex)

      // ── Periodic mesh & terminal ──
      if (tick % 4 === 0) {
        meshMessages.unshift(makeMeshMsg('pose', robot.name, `(${pos[0]},${pos[1]}) θ=${Math.floor(Math.random()*360)}°`, tick))
      }
      if (tick % 8 === 0) {
        meshMessages.unshift(makeMeshMsg('heartbeat', robot.name, `alive bat=${Math.round(battery)}% ${state}`, tick))
      }
      if (tick % 6 === 0) {
        terminalLog.unshift(makeTermLine('info', `[planner] A* path: ${remainingSteps} cells · ${(Math.random()*2).toFixed(1)}ms`, tick))
      }
      if (tick % 10 === 0 && aiAdvisorOn) {
        const congestion = (Math.random()).toFixed(2)
        traces.unshift(makeTrace('AI ADVICE', `congestion forecast(t+5s) = ${congestion} ${congestion > 0.6 ? 'HIGH' : 'LOW'} · ADVISORY ONLY`, tick))
      }

      // Trim logs
      if (traces.length > 40) traces = traces.slice(0, 40)
      if (meshMessages.length > 50) meshMessages = meshMessages.slice(0, 50)
      if (terminalLog.length > 60) terminalLog = terminalLog.slice(0, 60)

      return {
        ...robot,
        pos, goal, path, pathIndex, state, battery: Math.round(battery*10)/10,
        direction, intent, currentTask, remainingSteps,
        yieldingTo, yieldTimer, pickTimer, deliverTimer,
        traces, meshMessages, terminalLog,
        totalDistanceTravelled, tasksFinished, missionPriority,
      }
    })

    // Keep taskLog trimmed
    if (taskLog.length > 50) taskLog = taskLog.slice(0, 50)
    if (completedTasks.length > 30) completedTasks = completedTasks.slice(0, 30)

    set({
      tick,
      robots,
      taskQueue,
      activeTasks,
      completedTasks,
      tasksCompleted,
      deadlocksResolved,
      taskLog,
      messagesPerSec: 6 * 10 + Math.floor(Math.random() * 20),
    })
  },
}))

export {
  useStore,
  WAREHOUSE_MAP, ROWS, COLS,
  CELL_TYPES, CELL_ICONS,
  ROBOT_COLORS,
  pickStations, dockIn, dockOut, chargeBays,
}
