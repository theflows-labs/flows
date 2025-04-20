import { create } from 'zustand';

export const useTaskTypeStore = create((set, get) => ({
  taskTypes: [],
  loading: false,
  error: null,

  fetchTaskTypes: async () => {
    set({ loading: true });
    try {
      const response = await fetch('/api/task-types');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      set({ taskTypes: data, loading: false });
    } catch (error) {
      console.error('Error fetching task types:', error);
      set({ error: error.message, loading: false });
    }
  },

  createTaskType: async (taskTypeData) => {
    try {
      const response = await fetch('/api/task-types', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskTypeData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const newTaskType = await response.json();
      set((state) => ({
        taskTypes: [...state.taskTypes, newTaskType]
      }));
      return newTaskType;
    } catch (error) {
      console.error('Error creating task type:', error);
      throw error;
    }
  },

  updateTaskType: async (typeKey, taskTypeData) => {
    try {
      const response = await fetch(`/api/task-types/${typeKey}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskTypeData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const updatedTaskType = await response.json();
      set((state) => ({
        taskTypes: state.taskTypes.map(tt => 
          tt.type_key === typeKey ? updatedTaskType : tt
        )
      }));
      return updatedTaskType;
    } catch (error) {
      console.error('Error updating task type:', error);
      throw error;
    }
  },

  deactivateTaskType: async (typeKey) => {
    try {
      const response = await fetch(`/api/task-types/${typeKey}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      set((state) => ({
        taskTypes: state.taskTypes.map(tt =>
          tt.type_key === typeKey ? { ...tt, is_active: false } : tt
        )
      }));
    } catch (error) {
      console.error('Error deactivating task type:', error);
      throw error;
    }
  },

  refreshTaskTypes: async () => {
    try {
      const response = await fetch('/api/task-types/refresh', {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const refreshedTypes = await response.json();
      set({ taskTypes: refreshedTypes });
      return refreshedTypes;
    } catch (error) {
      console.error('Error refreshing task types:', error);
      throw error;
    }
  }
})); 