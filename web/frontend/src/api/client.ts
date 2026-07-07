const API_BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

export interface Material {
  compound_id: string
  name: string
  smiles: string
  formula: string
  group: string
  material_type: string
  notes: string
  has_manual_labels: boolean
}

export interface DashboardData {
  global: {
    total_materials: number
    total_formulas: number
    total_val_diag: number
    total_val_gen: number
    total_struct_only: number
    total_gen_hc: number
    hidden_ratio: number
    strategy_distribution: Record<string, number>
  }
  materials: MaterialCard[]
}

export interface MaterialCard {
  compound_id: string
  name: string
  group: string
  total_formulas: number
  val_diag: number
  val_gen: number
  feat_supp: number
  gen_hc: number
  struct_only: number
  val_diag_pct: number
  formula_evidence: string
  pattern_evidence: string
  final_evidence: string
  pom_pattern_score: number
  background_level: string
}

export interface FormulaItem {
  formula: string
  ion_mode: string
  charge: number
  exact_mass: number
  formula_score: number
  best_path_score: number
  path_count: number
  mechanism_count: number
  source_fragment_count: number
  generation_types: string
  diagnostic_tag: string
  material_diagnostic_score: number
  is_hidden: boolean
  is_generic_hc: boolean
  representative_path: string
}

export interface FormulaListResponse {
  material_id: string
  total: number
  page: number
  page_size: number
  total_pages: number
  tag_counts: Record<string, number>
  items: FormulaItem[]
}

export interface NetworkData {
  compound_id: string
  nodes: NetworkNodeData[]
  edges: NetworkEdgeData[]
  node_count: number
  edge_count: number
}

export interface NetworkNodeData {
  node_id: string
  formula: string
  ion_mode: string
  charge: number
  exact_mass: number
  generation_type: string
  operation: string
  rule_pack: string
  trigger_feature: string
  path_score: number
  formula_score: number
  structure_score: number
  path: string
  diagnostic_tag: string
  is_generic_hc: boolean
}

export interface NetworkEdgeData {
  edge_id: string
  source_node: string
  target_node: string
  operation: string
  operation_type: string
  weight: number
}

export interface EvidenceData {
  compound_id: string
  name: string
  summary: EvidenceSummary
  validated_diagnostic: EvidenceFormula[]
  validated_generic: EvidenceFormula[]
  feature_supported: EvidenceFormula[]
  generic_hydrocarbon: EvidenceFormula[]
}

export interface EvidenceSummary {
  total_formulas: number
  val_diag: number
  val_gen: number
  feat_supp: number
  gen_hc: number
  struct_only: number
  formula_evidence: string
  pattern_evidence: string
  pom_pattern_score: number
  background_level: string
  final_evidence: string
}

export interface EvidenceFormula {
  formula: string
  ion_mode: string
  charge: number
  exact_mass: number
  formula_score: number
  generation_types: string
  diagnostic_tag: string
  representative_path: string
}

// API functions
export const api = {
  getDashboard: () => request<DashboardData>('/dashboard'),

  getMaterials: () => request<Material[]>('/materials'),

  getMaterial: (id: string) => request<Material>(`/materials/${id}`),

  getFormulas: (materialId: string, params?: Record<string, string | number | boolean>) => {
    const search = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') search.set(k, String(v))
      })
    }
    const qs = search.toString()
    return request<FormulaListResponse>(`/materials/${materialId}/formulas${qs ? `?${qs}` : ''}`)
  },

  getNetwork: (materialId: string, hideStructOnly = true) =>
    request<NetworkData>(`/materials/${materialId}/network?hide_struct_only=${hideStructOnly}`),

  getEvidence: (materialId: string) =>
    request<EvidenceData>(`/materials/${materialId}/evidence`),

  importData: () => request<{ status: string; details: Record<string, unknown> }>('/import', { method: 'POST' }),

  exportFormulasCsv: (materialId?: string) => {
    const params = materialId ? `?material_id=${materialId}&format=csv` : '?format=csv'
    window.open(`${API_BASE}/export/formulas${params}`, '_blank')
  },

  exportEvidenceMd: () => window.open(`${API_BASE}/export/evidence?format=markdown`, '_blank'),

  exportNetworkJson: (materialId: string) =>
    window.open(`${API_BASE}/export/network?material_id=${materialId}&format=json`, '_blank'),

  generateNetwork: (params: { compound_id: string; smiles: string; formula?: string; version?: string }) =>
    request<{ task_id: string; status: string; message: string }>('/materials/' + encodeURIComponent(params.compound_id) + '/generate', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  getTasks: (status?: string) =>
    request<TaskInfo[]>(`/tasks${status ? `?status=${status}` : ''}`),

  getTask: (taskId: string) => request<TaskInfo>(`/tasks/${taskId}`),
}

export interface TaskInfo {
  task_id: string
  task_type: string
  material_id: string
  version: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  current_step: string
  log_path: string
  error_message: string
  created_at: string | null
  finished_at: string | null
}
