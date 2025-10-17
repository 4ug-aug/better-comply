import { create } from 'zustand';

interface DocumentStoreState {
  selectedDocId: number | null;
  selectedVersionId: number | null;
  setSelectedDoc: (docId: number) => void;
  setSelectedVersion: (versionId: number) => void;
  reset: () => void;
}

export const useDocumentStore = create<DocumentStoreState>((set) => ({
  selectedDocId: null,
  selectedVersionId: null,
  setSelectedDoc: (docId: number) => set({ selectedDocId: docId }),
  setSelectedVersion: (versionId: number) => set({ selectedVersionId: versionId }),
  reset: () => set({ selectedDocId: null, selectedVersionId: null }),
}));
