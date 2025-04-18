import { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  Paper,
  Grid,
  IconButton,
  Tooltip,
  Divider,
  Snackbar,
  Alert
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import AddIcon from '@mui/icons-material/Add';
import SettingsIcon from '@mui/icons-material/Settings';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import DataObjectIcon from '@mui/icons-material/DataObject';
import DownloadIcon from '@mui/icons-material/Download';
import TaskNode from '../components/TaskNode';
import TaskConfigForm from '../components/TaskConfigForm';
import useDAGStore from '../stores/dagStore';

const nodeTypes = {
  task: TaskNode,
};

const taskTypes = [
  { type: 'python', label: 'Python Task', icon: <CodeIcon /> },
  { type: 'data', label: 'Data Task', icon: <DataObjectIcon /> },
  { type: 'storage', label: 'Storage Task', icon: <StorageIcon /> },
];

function DAGBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { saveDAG } = useDAGStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isDAGConfigOpen, setIsDAGConfigOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [dagConfig, setDagConfig] = useState({
    name: '',
    description: '',
    schedule: '',
    startDate: '',
  });

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
    setIsConfigOpen(true);
  }, []);

  const handleSave = async () => {
    try {
      if (!dagConfig.name) {
        setSnackbar({ open: true, message: 'Please provide a DAG name', severity: 'error' });
        return;
      }

      const dagData = {
        ...dagConfig,
        nodes: nodes.map(node => ({
          id: node.id,
          data: node.data,
          position: node.position
        })),
        edges: edges.map(edge => ({
          source: edge.source,
          target: edge.target
        }))
      };

      const savedDAG = await saveDAG(dagData);
      setSnackbar({ open: true, message: 'DAG saved successfully', severity: 'success' });
      navigate(`/dags/${savedDAG.id}`);
    } catch (error) {
      console.error('Error saving DAG:', error);
      setSnackbar({ open: true, message: error.message || 'Failed to save DAG', severity: 'error' });
    }
  };

  const handleDownloadYAML = async () => {
    try {
      if (!dagConfig.name) {
        setSnackbar({ open: true, message: 'Please provide a DAG name first', severity: 'error' });
        return;
      }

      // First save the DAG to get its ID
      const dagData = {
        ...dagConfig,
        nodes: nodes.map(node => ({
          id: node.id,
          data: node.data,
          position: node.position
        })),
        edges: edges.map(edge => ({
          source: edge.source,
          target: edge.target
        }))
      };

      const savedDAG = await saveDAG(dagData);
      
      // Then download the YAML
      const response = await fetch(`/api/dags/${savedDAG.id}/yaml`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dag_${savedDAG.id}.yaml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setSnackbar({ open: true, message: 'YAML downloaded successfully', severity: 'success' });
    } catch (error) {
      console.error('Error downloading YAML:', error);
      setSnackbar({ open: true, message: error.message || 'Failed to download YAML', severity: 'error' });
    }
  };

  const addTask = (type) => {
    const newNode = {
      id: `task-${nodes.length + 1}`,
      type: 'task',
      position: { x: 100, y: 100 },
      data: { type, label: `Task ${nodes.length + 1}` },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">
          {id ? 'Edit DAG' : 'Create New DAG'}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setIsDAGConfigOpen(true)}
            sx={{ mr: 2 }}
          >
            DAG Settings
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
          >
            Save DAG
          </Button>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        <Grid item xs={2}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Task Types
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {taskTypes.map((task) => (
              <Tooltip key={task.type} title={task.label} placement="right">
                <IconButton
                  onClick={() => addTask(task.type)}
                  sx={{ mb: 1, width: '100%', justifyContent: 'flex-start' }}
                >
                  {task.icon}
                  <Typography sx={{ ml: 1 }}>{task.label}</Typography>
                </IconButton>
              </Tooltip>
            ))}
          </Paper>
        </Grid>
        <Grid item xs={10}>
          <Paper sx={{ height: 'calc(100vh - 200px)' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background />
              <Controls />
              <MiniMap />
              <Panel position="top-right">
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadYAML}
                  disabled={!selectedNode}
                >
                  Download YAML
                </Button>
              </Panel>
            </ReactFlow>
          </Paper>
        </Grid>
      </Grid>

      <Dialog
        open={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Configure Task</DialogTitle>
        <DialogContent>
          {selectedNode && (
            <TaskConfigForm
              node={selectedNode}
              onUpdate={(data) => {
                setNodes((nds) =>
                  nds.map((node) =>
                    node.id === selectedNode.id
                      ? { ...node, data: { ...node.data, ...data } }
                      : node
                  )
                );
              }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsConfigOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={isDAGConfigOpen}
        onClose={() => setIsDAGConfigOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>DAG Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="DAG Name"
              value={dagConfig.name}
              onChange={(e) => setDagConfig({ ...dagConfig, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={dagConfig.description}
              onChange={(e) => setDagConfig({ ...dagConfig, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Schedule (Cron Expression)"
              value={dagConfig.schedule}
              onChange={(e) => setDagConfig({ ...dagConfig, schedule: e.target.value })}
              placeholder="e.g., 0 0 * * *"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              value={dagConfig.startDate}
              onChange={(e) => setDagConfig({ ...dagConfig, startDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDAGConfigOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default DAGBuilder; 