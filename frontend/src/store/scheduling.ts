import { create } from 'zustand'

type SchedulingState = {
  subsStatus?: string
  outboxStatus?: string
  subsLimit: number
  subsOffset: number
  runsLimit: number
  runsOffset: number
  outboxLimit: number
  outboxOffset: number
  isCreateOpen: boolean
  setSubsStatus: (s?: string) => void
  setOutboxStatus: (s?: string) => void
  setSubsPage: (offset: number) => void
  setRunsPage: (offset: number) => void
  setOutboxPage: (offset: number) => void
  setCreateOpen: (open: boolean) => void
}

export const useSchedulingStore = create<SchedulingState>((set) => ({
  subsStatus: undefined,
  outboxStatus: undefined,
  subsLimit: 50,
  subsOffset: 0,
  runsLimit: 50,
  runsOffset: 0,
  outboxLimit: 50,
  outboxOffset: 0,
  isCreateOpen: false,
  setSubsStatus: (s) => set({ subsStatus: s, subsOffset: 0 }),
  setOutboxStatus: (s) => set({ outboxStatus: s, outboxOffset: 0 }),
  setSubsPage: (offset) => set({ subsOffset: offset }),
  setRunsPage: (offset) => set({ runsOffset: offset }),
  setOutboxPage: (offset) => set({ outboxOffset: offset }),
  setCreateOpen: (open) => set({ isCreateOpen: open }),
}))


