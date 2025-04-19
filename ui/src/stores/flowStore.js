import { create } from 'zustand';
import axios from 'axios';
import YAML from 'yaml';
import { saveFileLocally } from '../utils/fileUtils';
import yaml from 'js-yaml';

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
      // Convert flow configuration to YAML
      const yamlContent = generateFlowYAML(flowData);
      
      // Prepare the request body
      const requestBody = {
        flow_id: flowData.flow_id,
        description: flowData.description,
        config_details: flowData.config_details,
        config_details_yaml: yamlContent
      };

      // Save flow configuration
      const response = await fetch('/api/flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const savedFlow = await response.json();

      // Save tasks and get ID mapping
      let taskIdMapping;
      if (flowData.config_details?.nodes) {
        taskIdMapping = await saveTasks(savedFlow.config_id, flowData.config_details.nodes);
      }

      // Save dependencies using the ID mapping
      if (flowData.config_details?.edges && taskIdMapping) {
        await saveDependencies(savedFlow.config_id, flowData.config_details.edges, taskIdMapping);
      }

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
      // First, fetch existing tasks to get current task IDs
      const tasksResponse = await fetch(`/api/tasks/flow/${flowId}`);
      const existingTasks = await tasksResponse.json();
      
      // Create a mapping of existing task positions/names to their IDs
      const existingTaskMapping = new Map(
        existingTasks.map(task => [
          // You might need to adjust this mapping logic based on how you identify tasks
          `${task.task_type}-${task.task_sequence}`,
          task.task_id
        ])
      );

      // Convert flow configuration to YAML
      const yamlContent = generateFlowYAML(flowData);

      // Update flow configuration
      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flow_id: flowData.flow_id,
          description: flowData.description,
          config_details: flowData.config_details,
          config_details_yaml: yamlContent
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const updatedFlow = await response.json();

      // Save/update tasks and get new ID mapping
      let taskIdMapping;
      if (flowData.config_details?.nodes) {
        taskIdMapping = await saveTasks(updatedFlow.config_id, flowData.config_details.nodes);
      }

      // Save/update dependencies using the ID mapping
      if (flowData.config_details?.edges && taskIdMapping) {
        await saveDependencies(updatedFlow.config_id, flowData.config_details.edges, taskIdMapping);
      }

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

  downloadFlowYAML: async (flowId) => {
    try {
      const response = await fetch(`/api/flows/${flowId}/yaml`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const yamlContent = await response.text();
      
      // Create and trigger download
      const blob = new Blob([yamlContent], { type: 'text/yaml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `flow-${flowId}.yaml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading YAML:', error);
      throw error;
    }
  },
}));

// Helper function to save tasks and return ID mapping
async function saveTasks(flowConfigId, nodes) {
  const taskIdMapping = new Map();

  for (const node of nodes) {
    const taskData = {
      flow_config_id: flowConfigId,
      task_type: node.data.type,
      task_sequence: node.data.sequence || 0,
      config_details: node.data.config,
      config_details_yaml: yaml.dump(node.data.config),
      description: node.data.description || node.data.label
    };

    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        throw new Error(`Failed to save task: ${node.id}`);
      }

      const savedTask = await response.json();
      // Store the mapping between React Flow node ID and actual task ID
      taskIdMapping.set(node.id, savedTask.task_id);
    } catch (error) {
      console.error('Error saving task:', error);
      throw error;
    }
  }

  return taskIdMapping;
}

// Helper function to save dependencies using the ID mapping
async function saveDependencies(flowConfigId, edges, taskIdMapping) {
  const dependencyPromises = edges.map(async (edge) => {
    // Use the mapped task IDs instead of React Flow node IDs
    const sourceTaskId = taskIdMapping.get(edge.source);
    const targetTaskId = taskIdMapping.get(edge.target);

    if (!sourceTaskId || !targetTaskId) {
      throw new Error(`Missing task mapping for edge: ${edge.id}`);
    }

    const dependencyData = {
      flow_config_id: flowConfigId,
      task_id: sourceTaskId,
      depends_on_task_id: targetTaskId,
      dependency_type: edge.data?.type || 'success'
    };

    const response = await fetch('/api/tasks/dependencies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dependencyData),
    });

    if (!response.ok) {
      throw new Error(`Failed to save dependency: ${edge.id}`);
    }

    return response.json();
  });

  return Promise.all(dependencyPromises);
}

// Helper function to generate YAML
function generateFlowYAML(flowData) {
  const yamlStructure = {
    flow_id: flowData.flow_id,
    description: flowData.description,
    tasks: flowData.config_details.nodes.map(node => ({
      id: node.id,
      type: node.data.type,
      label: node.data.label,
      config: node.data.config,
      sequence: node.data.sequence || 0
    })),
    dependencies: flowData.config_details.edges.map(edge => ({
      source_task_id: edge.source,
      target_task_id: edge.target,
      type: edge.data?.type || 'success'
    }))
  };

  return yaml.dump(yamlStructure);
}

export default useFlowStore; 