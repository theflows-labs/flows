import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const useDAGStore = create((set) => ({
  dags: [],
  currentDAG: null,
  loading: false,
  error: null,

  fetchDAGs: async () => {
    try {
      set({ loading: true, error: null });
      const response = await axios.get(`${API_URL}/dags`);
      set({ dags: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  fetchDAG: async (id) => {
    try {
      set({ loading: true, error: null });
      const response = await axios.get(`${API_URL}/dags/${id}`);
      set({ currentDAG: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  createDAG: async (dagData) => {
    try {
      set({ loading: true, error: null });
      const response = await axios.post(`${API_URL}/dags`, dagData);
      set((state) => ({
        dags: [...state.dags, response.data],
        currentDAG: response.data,
        loading: false,
      }));
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateDAG: async (id, dagData) => {
    try {
      set({ loading: true, error: null });
      const response = await axios.put(`${API_URL}/dags/${id}`, dagData);
      set((state) => ({
        dags: state.dags.map((dag) =>
          dag.id === id ? response.data : dag
        ),
        currentDAG: response.data,
        loading: false,
      }));
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deleteDAG: async (id) => {
    try {
      set({ loading: true, error: null });
      await axios.delete(`${API_URL}/dags/${id}`);
      set((state) => ({
        dags: state.dags.filter((dag) => dag.id !== id),
        currentDAG: null,
        loading: false,
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  downloadDAGYAML: async (id) => {
    try {
      set({ loading: true, error: null });
      const response = await axios.get(`${API_URL}/dags/${id}/yaml`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dag_${id}.yaml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      set({ loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
})); 