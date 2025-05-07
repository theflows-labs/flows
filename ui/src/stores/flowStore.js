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
    console.log('=== Starting saveFlow ===');
    console.log('Flow data:', {
      flow_id: flowData.flow_id,
      node_count: flowData.config_details.nodes.length,
      edge_count: flowData.config_details.edges.length
    });

    try {
      // Generate YAML content
      const yamlContent = generateFlowYAML(flowData);
      console.log('Generated YAML content');

      // First, save the flow configuration
      console.log('Creating flow configuration...');
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
      console.log('Created flow configuration:', flowConfig);

      // Save tasks and get ID mapping
      console.log('Saving tasks...');
      const taskIdMapping = await saveTasks(flowConfig.config_id, flowData.config_details.nodes, flowConfig);

      // Save dependencies using the ID mapping
      console.log('Saving dependencies...');
      await saveDependencies(flowConfig.config_id, flowData.config_details.edges, taskIdMapping);

      // Update nodes with task IDs
      console.log('Updating nodes with task IDs...');
      const updatedNodes = flowData.config_details.nodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          task_id: taskIdMapping.get(node.id)
        }
      }));

      // Update flow configuration with task IDs
      console.log('Updating flow configuration with task IDs...');
      const updatedFlowConfig = {
        ...flowConfig,
        config_details: {
          nodes: updatedNodes,
          edges: flowData.config_details.edges,
        },
        config_details_yaml: yamlContent
      };

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

      const result = await updateResponse.json();
      console.log('Flow saved successfully:', result);
      console.log('=== Completed saveFlow ===\n');
      return result;
    } catch (error) {
      console.error('Error in saveFlow:', error);
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
      const taskIdMapping = await saveTasks(existingFlow.config_id, flowData.config_details.nodes, existingFlow);

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
async function saveTasks(flowConfigId, nodes, existingFlowConfig = null) {
  console.log('=== Starting saveTasks ===');
  console.log('Flow Config ID:', flowConfigId);
  console.log('Nodes to process:', nodes.map(n => ({ id: n.id, type: n.data.type, task_id: n.data.task_id })));

  const taskIdMapping = new Map();

  // First, get all existing tasks for this flow configuration
  console.log('Fetching existing tasks for flow config:', flowConfigId);
  const existingTasksResponse = await fetch(`/api/tasks/flow/${flowConfigId}`);
  if (!existingTasksResponse.ok) {
    throw new Error('Failed to fetch existing tasks');
  }
  const existingTasks = await existingTasksResponse.json();
  console.log('Existing tasks:', existingTasks.map(t => ({ id: t.task_id, type: t.task_type })));
  
  // Create map for quick lookup by task_id
  const existingTaskMap = new Map(existingTasks.map(task => [task.task_id, task]));
  console.log('Existing task IDs:', Array.from(existingTaskMap.keys()));

  // Create a map of node IDs to task IDs from the flow configuration
  const nodeToTaskMap = new Map();
  if (existingFlowConfig && existingFlowConfig.config_details && existingFlowConfig.config_details.nodes) {
    existingFlowConfig.config_details.nodes.forEach(node => {
      if (node.data && node.data.task_id) {
        nodeToTaskMap.set(node.id, node.data.task_id);
        console.log(`Mapped node ${node.id} to task ${node.data.task_id} from flow config`);
      }
    });
  }
  console.log('Node to Task mapping from flow config:', Object.fromEntries(nodeToTaskMap));

  for (const node of nodes) {
    console.log(`\nProcessing node ${node.id}:`, {
      type: node.data.type,
      existing_task_id: node.data.task_id,
      mapped_task_id: nodeToTaskMap.get(node.id)
    });

    const taskData = {
      flow_config_id: flowConfigId,
      task_type: node.data.type,
      task_sequence: node.data.sequence || 0,
      config_details: node.data.config,
      description: node.data.description || node.data.label
    };

    try {
      // First check if the node has a task_id in the flow configuration
      const existingTaskId = nodeToTaskMap.get(node.id);
      console.log(`Node ${node.id} task ID from flow config:`, existingTaskId);
      
      if (existingTaskId && existingTaskMap.has(existingTaskId)) {
        console.log(`Updating existing task ${existingTaskId} for node ${node.id}`);
        // Update existing task
        const response = await fetch(`/api/tasks/${existingTaskId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(taskData),
        });

        if (!response.ok) {
          throw new Error(`Failed to update task: ${node.id}`);
        }

        taskIdMapping.set(node.id, existingTaskId);
        console.log(`Updated task ${existingTaskId} for node ${node.id}`);
      } else {
        console.log(`Creating new task for node ${node.id}`);
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
        console.log(`Created new task ${savedTask.task_id} for node ${node.id}`);
      }
    } catch (error) {
      console.error(`Error processing node ${node.id}:`, error);
      throw error;
    }
  }

  console.log('\nFinal task ID mapping:', Object.fromEntries(taskIdMapping));
  console.log('=== Completed saveTasks ===\n');
  return taskIdMapping;
}

// Helper function to save dependencies using the ID mapping
async function saveDependencies(flowConfigId, edges, taskIdMapping) {
  console.log('=== Starting saveDependencies ===');
  console.log('Flow Config ID:', flowConfigId);
  console.log('Edges to process:', edges.map(e => ({ id: e.id, source: e.source, target: e.target })));
  console.log('Task ID mapping:', Object.fromEntries(taskIdMapping));

  // First, get all existing dependencies for this flow
  console.log('Fetching existing dependencies for flow:', flowConfigId);
  const existingDepsResponse = await fetch(`/api/tasks/dependencies/flow/${flowConfigId}`);
  if (!existingDepsResponse.ok) {
    throw new Error('Failed to fetch existing dependencies');
  }
  const existingDeps = await existingDepsResponse.json();
  console.log('Existing dependencies:', existingDeps);

  // Create a map of existing dependencies using task_id and depends_on_task_id as key
  const existingDepsMap = new Map(
    existingDeps.map(dep => [
      `${dep.task_id}-${dep.depends_on_task_id}`,
      dep
    ])
  );
  console.log('Existing dependencies map:', Object.fromEntries(existingDepsMap));

  // Process each edge
  const dependencyPromises = edges.map(async (edge) => {
    const sourceTaskId = taskIdMapping.get(edge.source);
    const targetTaskId = taskIdMapping.get(edge.target);

    console.log(`Processing edge ${edge.id}:`, {
      source: edge.source,
      target: edge.target,
      sourceTaskId,
      targetTaskId
    });

    if (!sourceTaskId || !targetTaskId) {
      throw new Error(`Missing task mapping for edge: ${edge.id}`);
    }

    const dependencyKey = `${sourceTaskId}-${targetTaskId}`;
    const existingDep = existingDepsMap.get(dependencyKey);

    const dependencyData = {
      flow_config_id: flowConfigId,
      task_id: sourceTaskId,
      depends_on_task_id: targetTaskId,
      dependency_type: edge.data?.type || 'success'
    };

    try {
      if (existingDep) {
        // Update existing dependency if type has changed
        if (existingDep.dependency_type !== dependencyData.dependency_type) {
          console.log(`Updating existing dependency for edge ${edge.id}:`, dependencyData);
          const response = await fetch(`/api/tasks/dependencies/${existingDep.dependency_id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(dependencyData),
          });

          if (!response.ok) {
            throw new Error(`Failed to update dependency: ${edge.id}`);
          }

          const result = await response.json();
          console.log(`Updated dependency for edge ${edge.id}:`, result);
          return result;
        } else {
          console.log(`Dependency already exists for edge ${edge.id}, no update needed`);
          return existingDep;
        }
      } else {
        // Create new dependency
        console.log(`Creating new dependency for edge ${edge.id}:`, dependencyData);
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

        const result = await response.json();
        console.log(`Created new dependency for edge ${edge.id}:`, result);
        return result;
      }
    } catch (error) {
      console.error(`Error processing dependency for edge ${edge.id}:`, error);
      throw error;
    }
  });

  // Get all dependencies after processing
  const results = await Promise.all(dependencyPromises);
  console.log('=== Completed saveDependencies ===\n');
  return results;
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