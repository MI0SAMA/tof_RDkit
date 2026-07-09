import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api, TaskInfo } from '../api/client'
import { Clock, CheckCircle, XCircle, Loader2, AlertCircle, ExternalLink } from 'lucide-react'

const STATUS_STYLE: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  pending: { icon: <Clock size={14} />, color: 'text-gray-500', bg: 'bg-gray-100' },
  running: { icon: <Loader2 size={14} className="animate-spin" />, color: 'text-blue-600', bg: 'bg-blue-50' },
  completed: { icon: <CheckCircle size={14} />, color: 'text-green-600', bg: 'bg-green-50' },
  failed: { icon: <XCircle size={14} />, color: 'text-red-600', bg: 'bg-red-50' },
}

export default function TasksPage() {
  const navigate = useNavigate()
  const { data: tasks, isLoading, refetch } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => api.getTasks(),
    refetchInterval: 3000, // Auto-refresh every 3s
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  const activeTasks = tasks?.filter(t => t.status === 'pending' || t.status === 'running') || []
  const completedTasks = tasks?.filter(t => t.status === 'completed' || t.status === 'failed') || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tasks</h2>
          <p className="text-sm text-gray-500 mt-1">
            {activeTasks.length} active, {completedTasks.length} completed
          </p>
        </div>
        <button onClick={() => refetch()} className="text-sm text-blue-600 hover:text-blue-800">
          Refresh
        </button>
      </div>

      {/* Active Tasks */}
      {activeTasks.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Active
          </h3>
          <div className="space-y-2">
            {activeTasks.map((task) => (
              <TaskRow key={task.task_id} task={task} navigate={navigate} />
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Completed
          </h3>
          <div className="space-y-2">
            {completedTasks.map((task) => (
              <TaskRow key={task.task_id} task={task} navigate={navigate} />
            ))}
          </div>
        </div>
      )}

      {/* Empty */}
      {(!tasks || tasks.length === 0) && (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
          <AlertCircle size={40} />
          <p className="mt-3 text-sm">No tasks yet</p>
          <p className="text-xs mt-1">Generate a network from the Materials page to see tasks here</p>
        </div>
      )}
    </div>
  )
}

function TaskRow({ task, navigate }: { task: TaskInfo; navigate: (path: string) => void }) {
  const style = STATUS_STYLE[task.status] || STATUS_STYLE.pending
  const elapsed = task.created_at ? getElapsed(task.created_at) : ''

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={style.color}>{style.icon}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-gray-500">{task.task_id}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.bg} ${style.color}`}>
                {task.status}
              </span>
            </div>
            <p className="text-sm text-gray-700 mt-0.5">
              {task.task_type === 'generate_network' ? `Generate: ${task.material_id}` : task.task_type}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {task.status === 'running' && (
            <div className="flex items-center gap-2">
              <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${task.progress}%` }} />
              </div>
              <span className="text-xs text-gray-500">{task.progress}%</span>
            </div>
          )}
          {task.status === 'completed' && (
            <button
              onClick={() => navigate(`/materials/${task.material_id}`)}
              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
            >
              <ExternalLink size={12} /> View
            </button>
          )}
          {task.error_message && (
            <span className="text-xs text-red-500 max-w-xs truncate" title={task.error_message}>
              {task.error_message.substring(0, 60)}
            </span>
          )}
        </div>
      </div>
      {/* Progress details */}
      <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
        {task.current_step && <span>{task.current_step}</span>}
        {elapsed && <span>{elapsed}</span>}
      </div>
    </div>
  )
}

function getElapsed(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m ago`
}
