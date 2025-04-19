import { create } from 'zustand';
import axios from 'axios';
import YAML from 'yaml';
import { saveFileLocally } from '../utils/fileUtils';

const useFlowStore = create((set) => ({
  flows: [],
  selectedFlow: null,
  loading: false,
  error: null,

  fetchFlows: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/flows');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      set({ flows: data, loading: false });
    } catch (error) {
      console.error('Error fetching flows:', error);
      set({ error: error.message, loading: false });
    }
  },

  saveFlow: async (flowData) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(flowData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const savedFlow = await response.json();
      set((state) => ({
        flows: [...state.flows, savedFlow],
        loading: false,
      }));
      return savedFlow;
    } catch (error) {
      console.error('Error saving flow:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateFlow: async (flowId, flowData) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(flowData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const updatedFlow = await response.json();
      set((state) => ({
        flows: state.flows.map((flow) =>
          flow.flow_id === flowId ? updatedFlow : flow
        ),
        loading: false,
      }));
      return updatedFlow;
    } catch (error) {
      console.error('Error updating flow:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deleteFlow: async (flowId) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      set((state) => ({
        flows: state.flows.filter((flow) => flow.flow_id !== flowId),
        loading: false,
      }));
    } catch (error) {
      console.error('Error deleting flow:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  setSelectedFlow: (flow) => set({ selectedFlow: flow }),
}));

export default useFlowStore; 