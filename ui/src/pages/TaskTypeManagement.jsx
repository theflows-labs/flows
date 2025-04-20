import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  Typography, 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useTaskTypeStore } from '../stores/taskTypeStore';
import JsonSchemaForm from '../components/JsonSchemaForm';

// Define the schema for task type configuration
const taskTypeSchema = {
  type: 'object',
  properties: {
    name: { 
      type: 'string', 
      title: 'Name',
      description: 'Display name for the task type'
    },
    type_key: { 
      type: 'string', 
      title: 'Type Key',
      description: 'Unique identifier for the task type (e.g., python_operator)'
    },
    description: { 
      type: 'string', 
      title: 'Description',
      description: 'Detailed description of what this task type does'
    },
    plugin_source: { 
      type: 'string', 
      title: 'Plugin Source',
      enum: ['airflow', 'custom'],
      description: 'Source of the task type implementation'
    },
    config_schema: { 
      type: 'object', 
      title: 'Configuration Schema',
      description: 'JSON Schema defining the configuration options',
      properties: {
        type: { type: 'string', enum: ['object'] },
        properties: { type: 'object' },
        required: { 
          type: 'array',
          items: { type: 'string' }
        }
      }
    },
    default_config: { 
      type: 'object', 
      title: 'Default Configuration',
      description: 'Default values for configuration options'
    },
    icon: { 
      type: 'string', 
      title: 'Icon',
      description: 'Icon identifier for the UI'
    }
  },
  required: ['name', 'type_key', 'config_schema']
};

const TaskTypeManagement = () => {
  const { 
    taskTypes, 
    loading,
    error,
    fetchTaskTypes, 
    createTaskType, 
    updateTaskType, 
    deactivateTaskType,
    refreshTaskTypes 
  } = useTaskTypeStore();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTaskType, setSelectedTaskType] = useState(null);
  const [formError, setFormError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    console.log('Fetching task types...');
    fetchTaskTypes().catch(err => {
      console.error('Error fetching task types:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load task types: ' + err.message,
        severity: 'error'
      });
    });
  }, [fetchTaskTypes]);

  const handleCreate = () => {
    setSelectedTaskType(null);
    setFormError(null);
    setOpenDialog(true);
  };

  const handleEdit = (taskType) => {
    setSelectedTaskType(taskType);
    setFormError(null);
    setOpenDialog(true);
  };

  const handleSave = async (formData) => {
    try {
      if (selectedTaskType) {
        await updateTaskType(selectedTaskType.type_key, formData);
      } else {
        await createTaskType(formData);
      }
      setOpenDialog(false);
      fetchTaskTypes();
    } catch (error) {
      setFormError(error.message);
    }
  };

  const handleDeactivate = async (typeKey) => {
    if (window.confirm('Are you sure you want to deactivate this task type?')) {
      try {
        await deactivateTaskType(typeKey);
        fetchTaskTypes();
      } catch (error) {
        console.error('Error deactivating task type:', error);
      }
    }
  };

  const handleRefresh = async () => {
    try {
      await refreshTaskTypes();
    } catch (error) {
      console.error('Error refreshing task types:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Task Type Management</Typography>
        <Box>
          <Button 
            startIcon={<RefreshIcon />} 
            onClick={handleRefresh}
            sx={{ mr: 1 }}
          >
            Refresh Task Types
          </Button>
          <Button 
            startIcon={<AddIcon />} 
            variant="contained" 
            onClick={handleCreate}
          >
            Add Task Type
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : (
        <Card>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type Key</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {taskTypes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No task types found. Click "Add Task Type" to create one.
                  </TableCell>
                </TableRow>
              ) : (
                taskTypes.map((taskType) => (
                  <TableRow key={taskType.type_key}>
                    <TableCell>{taskType.name}</TableCell>
                    <TableCell>{taskType.type_key}</TableCell>
                    <TableCell>{taskType.plugin_source}</TableCell>
                    <TableCell>
                      <Chip 
                        label={taskType.is_active ? 'Active' : 'Inactive'}
                        color={taskType.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEdit(taskType)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDeactivate(taskType.type_key)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTaskType ? 'Edit Task Type' : 'Add New Task Type'}
        </DialogTitle>
        <DialogContent>
          {formError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formError}
            </Alert>
          )}
          <JsonSchemaForm
            schema={taskTypeSchema}
            formData={selectedTaskType}
            onChange={handleSave}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>
            {selectedTaskType ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskTypeManagement; 