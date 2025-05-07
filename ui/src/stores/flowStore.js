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
    try {
      // Generate YAML content
      const yamlContent = generateFlowYAML(flowData);

      // First, save the flow configuration
      const flowConfigResponse = await fetch('/api/flows', {
        method: 'POST',
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

      if (!flowConfigResponse.ok) {
        throw new Error('Failed to save flow configuration');
      }

      const flowConfig = await flowConfigResponse.json();

      // Save tasks and get ID mapping
      const taskIdMapping = await saveTasks(flowConfig.config_id, flowData.config_details.nodes);

      // Save dependencies using the ID mapping
      await saveDependencies(flowConfig.config_id, flowData.config_details.edges, taskIdMapping);

      // Update nodes with task IDs
      const updatedNodes = flowData.config_details.nodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          task_id: taskIdMapping.get(node.id)
        }
      }));

      // Update flow configuration with task IDs
      const updatedFlowConfig = {
        ...flowConfig,
        config_details: {
          nodes: updatedNodes,
          edges: flowData.config_details.edges,
        },
        config_details_yaml: yamlContent
      };

      // Update the flow configuration with task IDs
      const updateResponse = await fetch(`/api/flows/${flowConfig.flow_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedFlowConfig),
      });

      if (!updateResponse.ok) {
        throw new Error('Failed to update flow configuration');
      }

      return await updateResponse.json();
    } catch (error) {
      console.error('Error saving flow:', error);
      throw error;
    }
  },

  updateFlow: async (flowId, flowData) => {
    try {
      // Generate YAML content
      const yamlContent = generateFlowYAML(flowData);

      // Get existing flow configuration
      const existingFlowResponse = await fetch(`/api/flows/${flowId}`);
      if (!existingFlowResponse.ok) {
        throw new Error('Failed to get existing flow configuration');
      }
      const existingFlow = await existingFlowResponse.json();

      // Save tasks and get ID mapping
      const taskIdMapping = await saveTasks(existingFlow.config_id, flowData.config_details.nodes);

      // Save dependencies using the ID mapping
      await saveDependencies(existingFlow.config_id, flowData.config_details.edges, taskIdMapping);

      // Update nodes with task IDs
      const updatedNodes = flowData.config_details.nodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          task_id: taskIdMapping.get(node.id)
        }
      }));

      // Update flow configuration with task IDs
      const updatedFlowConfig = {
        ...flowData,
        config_details: {
          nodes: updatedNodes,
          edges: flowData.config_details.edges,
        },
        config_details_yaml: yamlContent
      };

      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedFlowConfig),
      });

      if (!response.ok) {
        throw new Error('Failed to update flow');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating flow:', error);
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
      
      // Get the YAML content directly
      const yamlContent = await response.text();
      
      // Create and trigger download
      const blob = new Blob([yamlContent], { type: 'application/x-yaml' });
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

  activateFlow: async (flowId) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/flows/${flowId}/activate`, {
        method: 'POST',
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
      console.error('Error activating flow:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deactivateFlow: async (flowId) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/flows/${flowId}/deactivate`, {
        method: 'POST',
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
      console.error('Error deactivating flow:', error);
      set({ error: error.message, loading: false });
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
      description: node.data.description || node.data.label
    };

    try {
      // If node has a task_id, update existing task
      if (node.data.task_id) {
        const response = await fetch(`/api/tasks/${node.data.task_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(taskData),
        });

        if (!response.ok) {
          throw new Error(`Failed to update task: ${node.id}`);
        }

        const updatedTask = await response.json();
        taskIdMapping.set(node.id, updatedTask.task_id);
      } else {
        // Create new task
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
        taskIdMapping.set(node.id, savedTask.task_id);
      }
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
    version: '1.0',
    flow: {
      id: flowData.flow_id,
      description: flowData.description || '',
      tasks: flowData.config_details.nodes.map(node => ({
        id: node.id,
        type: node.data.type,
        name: node.data.label,
        description: node.data.description || '',
        config: node.data.config || {},
        sequence: node.data.sequence || 0
      })),
      dependencies: flowData.config_details.edges.map(edge => ({
        from: edge.source,
        to: edge.target,
        type: edge.data?.type || 'success',
        condition: edge.data?.condition || null
      }))
    },
    metadata: {
      created_at: new Date().toISOString(),
      version: '1.0',
      engine: 'airflow'
    }
  };

  // Use js-yaml with proper options for formatting
  return yaml.dump(yamlStructure, {
    indent: 2,
    lineWidth: -1, // Disable line wrapping
    noRefs: true,
    sortKeys: false,
    noCompatMode: true,
    quotingType: '"',
    forceQuotes: false,
    flowLevel: -1
  });
}

export default useFlowStore; 