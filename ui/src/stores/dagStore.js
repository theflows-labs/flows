import { create } from 'zustand';
import axios from 'axios';
import YAML from 'yaml';
import { saveFileLocally } from '../utils/fileUtils';

const useDAGStore = create((set) => ({
  dags: [],
  selectedDAG: null,
  loading: false,
  error: null,

  fetchDAGs: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/dags');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      set({ dags: data, loading: false });
    } catch (error) {
      console.error('Error fetching DAGs:', error);
      set({ error: error.message, loading: false });
    }
  },

  saveDAG: async (dagData) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/dags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dagData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const savedDAG = await response.json();
      set((state) => ({
        dags: [...state.dags, savedDAG],
        loading: false,
      }));
      return savedDAG;
    } catch (error) {
      console.error('Error saving DAG:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateDAG: async (dagId, dagData) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/dags/${dagId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dagData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const updatedDAG = await response.json();
      set((state) => ({
        dags: state.dags.map((dag) =>
          dag.id === dagId ? updatedDAG : dag
        ),
        loading: false,
      }));
      return updatedDAG;
    } catch (error) {
      console.error('Error updating DAG:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deleteDAG: async (dagId) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/dags/${dagId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      set((state) => ({
        dags: state.dags.filter((dag) => dag.id !== dagId),
        loading: false,
      }));
    } catch (error) {
      console.error('Error deleting DAG:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  setSelectedDAG: (dag) => set({ selectedDAG: dag }),
}));

export default useDAGStore; 