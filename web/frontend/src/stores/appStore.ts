import { create } from 'zustand'

interface AppState {
  selectedMaterial: string | null
  sidebarOpen: boolean
  setSelectedMaterial: (id: string | null) => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  selectedMaterial: null,
  sidebarOpen: true,
  setSelectedMaterial: (id) => set({ selectedMaterial: id }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}))
