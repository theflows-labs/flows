import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import {
  Box,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';
import useFlowStore from '../stores/flowStore';
import TaskConfigForm from '../components/TaskConfigForm';
import TaskNode from '../components/TaskNode';
import 'reactflow/dist/style.css';

const nodeTypes = {
  task: TaskNode,
};

const FlowBuilder = () => {
  const { flowId } = useParams();
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isNewFlowDialogOpen, setIsNewFlowDialogOpen] = useState(!flowId);
  const [newFlowData, setNewFlowData] = useState({ flow_id: '', description: '' });
  const [anchorEl, setAnchorEl] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const { saveFlow, updateFlow, selectedFlow, setSelectedFlow } = useFlowStore();
  const [taskTypes, setTaskTypes] = useState({});

  useEffect(() => {
    if (flowId) {
      // Load existing flow
      const loadFlow = async () => {
        try {
          const response = await fetch(`/api/flows/${flowId}`);
          const flowData = await response.json();
          setSelectedFlow(flowData);
          if (flowData.config_details) {
            // Ensure nodes have task IDs
            const nodesWithTaskIds = flowData.config_details.nodes.map(node => ({
              ...node,
              data: {
                ...node.data,
                task_id: node.data.task_id // Preserve task_id if it exists
              }
            }));
            setNodes(nodesWithTaskIds);
            setEdges(flowData.config_details.edges || []);
          }
        } catch (error) {
          showNotification('Error loading flow', 'error');
        }
      };
      loadFlow();
    }

    // Fetch task types when component mounts
    const fetchTaskTypes = async () => {
      try {
        const response = await fetch('/api/task-types');
        if (!response.ok) throw new Error('Failed to fetch task types');
        const types = await response.json();
        
        // Convert array to object format
        const typeMap = types.reduce((acc, type) => ({
          ...acc,
          [type.type_key]: {
            name: type.name,
            description: type.description,
            configSchema: type.config_schema,
            defaultConfig: type.default_config,
            icon: type.icon
          }
        }), {});
        
        setTaskTypes(typeMap);
      } catch (error) {
        console.error('Error fetching task types:', error);
        showNotification('Error loading task types', 'error');
      }
    };

    fetchTaskTypes();
  }, []);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const handleAddTask = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleTaskTypeSelect = (typeKey) => {
    const taskType = taskTypes[typeKey];
    const newNode = {
      id: `task-${Date.now()}`,
      type: 'task',
      position: { x: 100, y: 100 },
      data: {
        label: `New ${taskType.name}`,
        type: typeKey,
        config: taskType.defaultConfig || {},
        task_id: null // Initialize task_id as null for new nodes
      },
    };
    setNodes((nds) => [...nds, newNode]);
    setAnchorEl(null);
  };

  const handleSaveFlow = async () => {
    // Add sequence numbers to nodes based on their position or connections
    const nodesWithSequence = nodes.map((node, index) => ({
      ...node,
      data: {
        ...node.data,
        sequence: calculateNodeSequence(node, edges, index)
      }
    }));

    const flowData = {
      flow_id: newFlowData.flow_id || selectedFlow?.flow_id,
      config_details: {
        nodes: nodesWithSequence,
        edges: edges,
      },
      description: newFlowData.description || selectedFlow?.description,
    };

    try {
      if (flowId) {
        await updateFlow(flowId, flowData);
        showNotification('Flow updated successfully');
      } else {
        const result = await saveFlow(flowData);
        showNotification('Flow created successfully');
        navigate(`/flows/${result.flow_id}`);
      }
    } catch (error) {
      showNotification('Error saving flow', 'error');
    }
  };

  // Helper function to calculate node sequence
  const calculateNodeSequence = (node, edges, defaultIndex) => {
    // This is a simple implementation - you might want to make it more sophisticated
    // based on your specific requirements
    const incomingEdges = edges.filter(edge => edge.target === node.id);
    if (incomingEdges.length === 0) {
      return 1; // Start nodes
    }
    
    // Get max sequence of source nodes and add 1
    const sourceNodes = nodes.filter(n => 
      incomingEdges.some(edge => edge.source === n.id)
    );
    const maxSourceSequence = Math.max(
      ...sourceNodes.map(n => n.data.sequence || 0),
      0
    );
    
    return maxSourceSequence + 1;
  };

  // const handleRunFlow = async () => {
  //   try {
  //     const response = await fetch(`/api/executions/${flowId}`, {
  //       method: 'POST',
  //     });
  //     const result = await response.json();
  //     showNotification('Flow execution started');
  //     // Optionally navigate to execution details page
  //   } catch (error) {
  //     showNotification('Error starting flow execution', 'error');
  //   }
  // };

  const showNotification = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">
          {flowId ? `Edit Flow: ${selectedFlow?.flow_id}` : 'Create New Flow'}
        </Typography>
      </Box>
      
      <Box sx={{ flexGrow: 1, display: 'flex' }}>
        <Box sx={{ flex: 1, position: 'relative' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
          >
            <Background />
            <Controls />
            <Panel position="top-right">
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddTask}
                sx={{ mr: 1 }}
              >
                Add Task
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSaveFlow}
                sx={{ mr: 1 }}
              >
                Save
              </Button>
              {/* {flowId && (
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<RunIcon />}
                  onClick={handleRunFlow}
                >
                  Run
                </Button>
              )} */}
            </Panel>
          </ReactFlow>
        </Box>

        {selectedNode && (
          <Box sx={{ width: 300, p: 2, borderLeft: 1, borderColor: 'divider' }}>
            <TaskConfigForm
              taskConfig={{
                type_key: selectedNode.data.type,
                config: selectedNode.data.config || {}
              }}
              onSave={(updatedConfig) => {
                setNodes((nds) =>
                  nds.map((node) =>
                    node.id === selectedNode.id 
                      ? {
                          ...node,
                          data: {
                            ...node.data,
                            config: updatedConfig.config
                          }
                        }
                      : node
                  )
                );
                setSelectedNode(null);
              }}
              onCancel={() => setSelectedNode(null)}
            />
          </Box>
        )}
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        {Object.entries(taskTypes).map(([typeKey, taskType]) => (
          <MenuItem
            key={typeKey}
            onClick={() => handleTaskTypeSelect(typeKey)}
          >
            <Typography variant="body2">
              {taskType.name}
              <Typography variant="caption" display="block" color="text.secondary">
                {taskType.description}
              </Typography>
            </Typography>
          </MenuItem>
        ))}
      </Menu>

      <Dialog
        open={isNewFlowDialogOpen}
        onClose={() => {
          if (!flowId) {
            navigate('/flows');
          }
          setIsNewFlowDialogOpen(false);
        }}
      >
        <DialogTitle>Create New Flow</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Flow ID"
            fullWidth
            value={newFlowData.flow_id}
            onChange={(e) => setNewFlowData({ ...newFlowData, flow_id: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={4}
            value={newFlowData.description}
            onChange={(e) => setNewFlowData({ ...newFlowData, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => navigate('/flows')}>Cancel</Button>
          <Button
            onClick={() => {
              if (newFlowData.flow_id) {
                setIsNewFlowDialogOpen(false);
              }
            }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FlowBuilder; 