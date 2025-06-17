import React, { useState, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Snackbar,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Grid,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  Help as HelpIcon,
  FormatAlignLeft as FormatIcon,
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import YAMLTaskNode from '../components/YAMLTaskNode';
import YAMLTaskConfigForm from '../components/YAMLTaskConfigForm';
import { useYamlFlowStore } from '../stores/yamlFlowStore';
import 'reactflow/dist/style.css';
import yaml from 'yaml';

const nodeTypes = {
  task: YAMLTaskNode,
};

const exampleYaml = `version: '1.0'
flow:
  id: test1
  description: First test flow.
  tasks:
  - id: 74
    type: s3_copy
    name: New S3CopyOperatorFactory
    description: New S3CopyOperatorFactory
    config:
      verify: true
      aws_conn_id: aws_default
      dest_bucket_key: test
      dest_bucket_name: test
      source_bucket_key: test
      source_bucket_name: test
    sequence: 1
  - id: 75
    type: s3_list
    name: New S3ListOperatorFactory
    description: New S3ListOperatorFactory
    config:
      verify: true
      aws_conn_id: aws_default
      bucket: test
    sequence: 1
  - id: 76
    type: s3_copy
    name: New S3CopyOperatorFactory
    description: New S3CopyOperatorFactory
    config:
      verify: true
      aws_conn_id: aws_default
      dest_bucket_key: test
      dest_bucket_name: test
      source_bucket_key: test
      source_bucket_name: test
    sequence: 2
  dependencies:
  - from: 74
    to: 75
    type: success
    condition: null
  - from: 75
    to: 76
    type: success
    condition: null
metadata:
  created_at: '2025-05-07T18:48:36.647420'
  updated_at: '2025-05-07T18:48:36.647420'
  version: '1.0'
  engine: airflow`;

const YAMLFlowBuilder = () => {
  const [yamlInput, setYamlInput] = useState(exampleYaml);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  const [helpAnchorEl, setHelpAnchorEl] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [editorHeight, setEditorHeight] = useState('600px');

  const { 
    parseYaml, 
    generateYaml, 
    saveFlow, 
    loading, 
    error, 
    clearError,
    flowMetadata 
  } = useYamlFlowStore();

  const handleYAMLChange = (value) => {
    try {
      // Try to parse the YAML to validate it
      const parsed = yaml.parse(value);
      setYamlInput(value);
    } catch (error) {
      // If YAML is invalid, still update the input but show a warning
      setYamlInput(value);
      setNotification({
        open: true,
        message: 'Invalid YAML format: ' + error.message,
        severity: 'warning'
      });
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target.result;
          setYamlInput(content);
          // Automatically build the flow from the uploaded file
          const { nodes: newNodes, edges: newEdges } = parseYaml(content);
          setNodes(newNodes);
          setEdges(newEdges);
        } catch (error) {
          setNotification({
            open: true,
            message: 'Error reading YAML file: ' + error.message,
            severity: 'error'
          });
        }
      };
      reader.readAsText(file);
    }
  };

  const handleDownloadYAML = () => {
    try {
      const yamlConfig = generateYaml();
      const blob = new Blob([yamlConfig], { type: 'text/yaml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${flowMetadata?.id || 'flow'}-${Date.now()}.yaml`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      setNotification({
        open: true,
        message: 'Error downloading YAML: ' + error.message,
        severity: 'error'
      });
    }
  };

  const handleCopyYAML = () => {
    try {
      const yamlConfig = generateYaml();
      navigator.clipboard.writeText(yamlConfig);
      setNotification({
        open: true,
        message: 'YAML copied to clipboard',
        severity: 'success'
      });
    } catch (error) {
      setNotification({
        open: true,
        message: 'Error copying YAML: ' + error.message,
        severity: 'error'
      });
    }
  };

  const handleBuildFlow = () => {
    try {
      const { nodes: newNodes, edges: newEdges } = parseYaml(yamlInput);
      setNodes(newNodes);
      setEdges(newEdges);
      setNotification({
        open: true,
        message: 'Flow built successfully',
        severity: 'success'
      });
    } catch (error) {
      setNotification({
        open: true,
        message: error.message || 'Error building flow',
        severity: 'error'
      });
    }
  };

  const handleSaveFlow = async () => {
    try {
      // Get the flow ID from YAML
      let flowId;
      let parsed;
      try {
        parsed = yaml.parse(yamlInput);
        console.log('Raw YAML input:', yamlInput); // Debug log
        console.log('Parsed YAML:', parsed); // Debug log
        console.log('Flow section:', parsed?.flow); // Debug log
        flowId = parsed?.flow?.id;
        console.log('Extracted flow ID:', flowId); // Debug log
      } catch (error) {
        console.warn('Error parsing YAML for flow ID:', error);
      }

      // Validate flow has at least one task
      if (nodes.length === 0) {
        setNotification({
          open: true,
          message: 'Flow must contain at least one task',
          severity: 'error'
        });
        return;
      }

      // Ensure we have a flow ID
      if (!flowId) {
        console.log('Flow ID is missing. YAML structure:', yaml.parse(yamlInput)); // Debug log
        setNotification({
          open: true,
          message: 'Flow ID is required in the YAML configuration. Please add an id field under the flow section.',
          severity: 'error'
        });
        return;
      }

      await saveFlow({
        flow_id: flowId,
        description: parsed?.flow?.description || 'Flow from YAML'
      });

      setNotification({
        open: true,
        message: 'Flow saved successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error saving flow:', error);
      setNotification({
        open: true,
        message: error.message || 'Error saving flow',
        severity: 'error'
      });
    }
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
    clearError();
  };

  const handleHelpClick = (event) => {
    setHelpAnchorEl(event.currentTarget);
  };

  const handleHelpClose = () => {
    setHelpAnchorEl(null);
  };

  const handleLoadExample = () => {
    setYamlInput(exampleYaml);
    handleHelpClose();
  };

  const onNodeClick = (event, node) => {
    setSelectedTask(node);
  };

  const handleTaskConfigSave = (updatedTask) => {
    setNodes(nodes.map(node => 
      node.id === updatedTask.id ? updatedTask : node
    ));
    setSelectedTask(null);
  };

  const handleFormatYAML = () => {
    try {
      const parsed = yaml.parse(yamlInput);
      const formatted = yaml.stringify(parsed, {
        indent: 2,
        lineWidth: -1,
        noRefs: true,
        sortKeys: false,
        noCompatMode: true,
        quotingType: '"',
        forceQuotes: false,
        flowLevel: -1
      });
      setYamlInput(formatted);
      setNotification({
        open: true,
        message: 'YAML formatted successfully',
        severity: 'success'
      });
    } catch (error) {
      setNotification({
        open: true,
        message: 'Error formatting YAML: ' + error.message,
        severity: 'error'
      });
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            YAML Flow Builder
          </Typography>
          <Tooltip title="Format YAML">
            <IconButton color="inherit" onClick={handleFormatYAML}>
              <FormatIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Copy YAML">
            <IconButton color="inherit" onClick={handleCopyYAML}>
              <CopyIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Download YAML">
            <IconButton color="inherit" onClick={handleDownloadYAML}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Upload YAML">
            <IconButton color="inherit" component="label">
              <UploadIcon />
              <input
                type="file"
                hidden
                accept=".yaml,.yml"
                onChange={handleFileUpload}
              />
            </IconButton>
          </Tooltip>
          <Tooltip title="Help">
            <IconButton color="inherit" onClick={handleHelpClick}>
              <HelpIcon />
            </IconButton>
          </Tooltip>
          <Button 
            color="inherit" 
            startIcon={<SaveIcon />}
            onClick={handleSaveFlow}
            disabled={nodes.length === 0 || loading}
          >
            Save Flow
          </Button>
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={helpAnchorEl}
        open={Boolean(helpAnchorEl)}
        onClose={handleHelpClose}
      >
        <MenuItem onClick={handleLoadExample}>Load Example</MenuItem>
      </Menu>

      <Grid container sx={{ flex: 1, overflow: 'hidden' }}>
        <Grid item xs={6} sx={{ height: '100%', borderRight: 1, borderColor: 'divider' }}>
          <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              YAML Editor
            </Typography>
            <Box sx={{ flex: 1, position: 'relative' }}>
              <Editor
                height={editorHeight}
                defaultLanguage="yaml"
                value={yamlInput}
                onChange={handleYAMLChange}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                  wordWrap: 'on',
                  formatOnPaste: true,
                  formatOnType: true,
                }}
                theme="vs-dark"
              />
            </Box>
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleBuildFlow}
                fullWidth
              >
                Build Flow
              </Button>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={6} sx={{ height: '100%' }}>
          <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Flow Visualization
            </Typography>
            <Box sx={{ flex: 1, position: 'relative' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                nodeTypes={nodeTypes}
                fitView
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            </Box>
          </Box>
        </Grid>
      </Grid>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>

      {selectedTask && (
        <YAMLTaskConfigForm
          open={Boolean(selectedTask)}
          onClose={() => setSelectedTask(null)}
          task={selectedTask}
          onSave={handleTaskConfigSave}
        />
      )}
    </Box>
  );
};

export default YAMLFlowBuilder; 