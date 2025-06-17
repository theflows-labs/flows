import { create } from 'zustand';
import yaml from 'js-yaml';

export const useYamlFlowStore = create((set, get) => ({
  // State
  yamlContent: '',
  nodes: [],
  edges: [],
  loading: false,
  error: null,
  flowMetadata: null,

  // Actions
  setYamlContent: (content) => set({ yamlContent: content }),

  // Parse YAML and update nodes/edges
  parseYaml: (yamlContent) => {
    try {
      const flowConfig = yaml.load(yamlContent);
      if (!flowConfig || !flowConfig.flow || !flowConfig.flow.tasks) {
        throw new Error('Invalid YAML: Missing flow or tasks configuration');
      }

      // Convert tasks to ReactFlow nodes
      const flowNodes = flowConfig.flow.tasks.map(task => ({
        id: task.id.toString(),
        type: 'task',
        position: { x: 0, y: 0 }, // Will be calculated based on sequence
        data: {
          label: task.name,
          type: task.type,
          config: task.config || {},
          task_id: task.id,
          sequence: task.sequence,
          description: task.description
        }
      }));

      // Calculate node positions based on sequence
      const sequenceGroups = {};
      flowNodes.forEach(node => {
        if (!sequenceGroups[node.data.sequence]) {
          sequenceGroups[node.data.sequence] = [];
        }
        sequenceGroups[node.data.sequence].push(node);
      });

      // Position nodes in a grid layout
      Object.entries(sequenceGroups).forEach(([sequence, nodes]) => {
        const yOffset = (parseInt(sequence) - 1) * 200; // Vertical spacing between sequences
        nodes.forEach((node, index) => {
          const xOffset = (index - (nodes.length - 1) / 2) * 250; // Horizontal spacing between nodes
          node.position = { x: xOffset, y: yOffset };
        });
      });

      // Convert dependencies to ReactFlow edges
      const flowEdges = (flowConfig.flow.dependencies || []).map(dep => ({
        id: `edge-${dep.from}-${dep.to}`,
        source: dep.from.toString(),
        target: dep.to.toString(),
        type: 'smoothstep',
        data: {
          type: dep.type,
          condition: dep.condition
        }
      }));

      set({ 
        nodes: flowNodes, 
        edges: flowEdges, 
        error: null,
        flowMetadata: {
          id: flowConfig.flow.id,
          description: flowConfig.flow.description,
          metadata: flowConfig.metadata
        }
      });
      return { nodes: flowNodes, edges: flowEdges };
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  // Generate YAML from current nodes and edges
  generateYaml: () => {
    try {
      const flowConfig = {
        version: '1.0',
        flow: {
          id: get().flowMetadata?.id || `flow-${Date.now()}`,
          description: get().flowMetadata?.description || 'Flow from YAML Builder',
          tasks: get().nodes.map(node => ({
            id: parseInt(node.data.task_id),
            type: node.data.type,
            name: node.data.label,
            description: node.data.description,
            config: node.data.config,
            sequence: node.data.sequence
          })),
          dependencies: get().edges.map(edge => ({
            from: parseInt(edge.source),
            to: parseInt(edge.target),
            type: edge.data?.type || 'success',
            condition: edge.data?.condition || null
          }))
        },
        metadata: {
          ...get().flowMetadata?.metadata,
          created_at: get().flowMetadata?.metadata?.created_at || new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: '1.0',
          engine: 'airflow'
        }
      };

      return yaml.dump(flowConfig, { 
        indent: 2,
        lineWidth: -1,
        noRefs: true,
        sortKeys: false,
        noCompatMode: true,
        quotingType: '"',
        forceQuotes: false,
        flowLevel: -1
      });
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  // Save flow to backend
  saveFlow: async (flowData) => {
    console.log('=== Starting saveFlow ===');
    console.log('Flow data:', {
      flow_id: flowData.flow_id,
      node_count: get().nodes.length,
      edge_count: get().edges.length
    });

    set({ loading: true, error: null });
    try {
      // Generate YAML content
      const yamlContent = get().generateYaml();
      console.log('Generated YAML content');

      // Check if flow exists
      let flowConfig;
      try {
        const checkResponse = await fetch(`/api/flows/${flowData.flow_id}`);
        if (checkResponse.ok) {
          // Flow exists, get its config
          flowConfig = await checkResponse.json();
          console.log('Found existing flow:', flowConfig);
        }
      } catch (error) {
        console.log('Flow does not exist, will create new one');
      }

      if (flowConfig) {
        // Update existing flow
        console.log('Updating existing flow configuration...');
        const updateResponse = await fetch(`/api/flows/${flowData.flow_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            flow_id: flowData.flow_id,
            description: flowData.description,
            config_details: {
              nodes: get().nodes,
              edges: get().edges
            },
            config_details_yaml: yamlContent
          }),
        });

        if (!updateResponse.ok) {
          throw new Error('Failed to update flow configuration');
        }

        flowConfig = await updateResponse.json();
      } else {
        // Create new flow
        console.log('Creating new flow configuration...');
        const createResponse = await fetch('/api/flows', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            flow_id: flowData.flow_id,
            description: flowData.description,
            config_details: {
              nodes: get().nodes,
              edges: get().edges
            },
            config_details_yaml: yamlContent
          }),
        });

        if (!createResponse.ok) {
          throw new Error('Failed to create flow configuration');
        }

        flowConfig = await createResponse.json();
      }

      // Save tasks and get ID mapping
      console.log('Saving tasks...');
      const taskIdMapping = await saveTasks(flowConfig.config_id, get().nodes, flowConfig);

      // Save dependencies using the ID mapping
      console.log('Saving dependencies...');
      await saveDependencies(flowConfig.config_id, get().edges, taskIdMapping);

      // Update nodes with task IDs
      console.log('Updating nodes with task IDs...');
      const updatedNodes = get().nodes.map(node => ({
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
          edges: get().edges,
        },
        config_details_yaml: yamlContent
      };

      const finalUpdateResponse = await fetch(`/api/flows/${flowConfig.flow_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedFlowConfig),
      });

      if (!finalUpdateResponse.ok) {
        throw new Error('Failed to update flow configuration with task IDs');
      }

      const result = await finalUpdateResponse.json();
      console.log('Flow saved successfully:', result);
      console.log('=== Completed saveFlow ===\n');

      set({ 
        loading: false,
        flowMetadata: {
          ...get().flowMetadata,
          id: result.flow_id,
          description: result.description
        }
      });
      return result;
    } catch (error) {
      console.error('Error in saveFlow:', error);
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Update nodes and edges
  updateFlow: (nodes, edges) => {
    set({ nodes, edges });
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },

  // Reset store
  reset: () => {
    set({
      yamlContent: '',
      nodes: [],
      edges: [],
      loading: false,
      error: null,
      flowMetadata: null
    });
  }
}));

// Helper function to save tasks
async function saveTasks(configId, nodes, flowConfig) {
  const taskIdMapping = new Map();
  
  for (const node of nodes) {
    console.log('Processing node:', node.id);
    try {
      // Extract task data from node
      const taskData = {
        flow_config_id: configId,
        task_type: node.data.type,
        name: node.data.label,
        description: node.data.description || '',
        config_details: node.data.config || {},
        task_sequence: node.data.sequence || 0  // Changed from sequence to task_sequence
      };

      console.log('Task data to save:', taskData);

      // Check if task already exists by task_id
      const existingTask = flowConfig.config_details.tasks?.find(
        t => t.id === node.data.task_id
      );

      let response;
      if (existingTask) {
        // Update existing task
        console.log('Updating existing task:', existingTask.id);
        response = await fetch(`/api/tasks/${existingTask.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...taskData,
            task_id: existingTask.id // Ensure we use the existing task ID
          }),
        });
      } else {
        // Create new task
        console.log('Creating new task with data:', taskData);
        response = await fetch('/api/tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(taskData),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Failed to save task: ${errorData.message || response.statusText}`);
      }

      const savedTask = await response.json();
      console.log('Saved task:', savedTask);
      
      // Map both the node ID and task ID to the saved task ID
      taskIdMapping.set(node.id, savedTask.id);
      if (node.data.task_id) {
        taskIdMapping.set(node.data.task_id.toString(), savedTask.id);
      }
    } catch (error) {
      console.error('Error saving task:', error);
      throw error;
    }
  }
  
  return taskIdMapping;
}

// Helper function to save dependencies
async function saveDependencies(configId, edges, taskIdMapping) {
  for (const edge of edges) {
    try {
      // Get the correct task IDs from the mapping
      const fromTaskId = taskIdMapping.get(edge.source) || taskIdMapping.get(edge.source.toString());
      const toTaskId = taskIdMapping.get(edge.target) || taskIdMapping.get(edge.target.toString());

      if (!fromTaskId || !toTaskId) {
        console.error('Missing task IDs for dependency:', { edge, fromTaskId, toTaskId });
        continue;
      }

      const depData = {
        flow_config_id: configId,
        from_task_id: fromTaskId,
        to_task_id: toTaskId,
        type: edge.data?.type || 'success',
        condition: edge.data?.condition || null
      };

      console.log('Saving dependency:', depData);

      const response = await fetch('/api/dependencies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(depData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Failed to save dependency: ${errorData.message || response.statusText}`);
      }

      const savedDep = await response.json();
      console.log('Saved dependency:', savedDep);
    } catch (error) {
      console.error('Error saving dependency:', error);
      throw error;
    }
  }
} 