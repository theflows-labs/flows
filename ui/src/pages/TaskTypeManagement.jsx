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
  Snackbar,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TablePagination,
  InputAdornment
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon
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
      description: 'Source of the task type implementation (e.g., airflow, aws, custom)'
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
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');

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

  // Filter and paginate task types
  const filteredTaskTypes = React.useMemo(() => {
    console.log('Filtering task types with:', {
      searchTerm,
      typeFilter,
      sourceFilter,
      totalTaskTypes: taskTypes.length
    });

    return taskTypes.filter(taskType => {
      const matchesSearch = searchTerm === '' || 
        taskType.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        taskType.type_key?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = typeFilter === 'all' || 
        taskType.type_key === typeFilter;
      
      const matchesSource = sourceFilter === 'all' || 
        taskType.plugin_source === sourceFilter;

      const isMatch = matchesSearch && matchesType && matchesSource;
      
      if (isMatch) {
        console.log('Matched task type:', {
          name: taskType.name,
          type_key: taskType.type_key,
          plugin_source: taskType.plugin_source
        });
      }

      return isMatch;
    });
  }, [taskTypes, searchTerm, typeFilter, sourceFilter]);

  const paginatedTaskTypes = React.useMemo(() => {
    return filteredTaskTypes.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );
  }, [filteredTaskTypes, page, rowsPerPage]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

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
          {/* <Button 
            startIcon={<AddIcon />} 
            variant="contained" 
            onClick={handleCreate}
          >
            Add Task Type
          </Button> */}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search and Filter Controls */}
      <Box display="flex" gap={2} mb={3}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by name or type key..."
          value={searchTerm}
          onChange={(e) => {
            console.log('Search term changed:', e.target.value);
            setSearchTerm(e.target.value);
            setPage(0); // Reset to first page when search changes
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={typeFilter}
            label="Type"
            onChange={(e) => {
              console.log('Type filter changed:', e.target.value);
              setTypeFilter(e.target.value);
              setPage(0); // Reset to first page when filter changes
            }}
          >
            <MenuItem value="all">All Types</MenuItem>
            {[...new Set(taskTypes.map(tt => tt.type_key).filter(Boolean))].map(type => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Source</InputLabel>
          <Select
            value={sourceFilter}
            label="Source"
            onChange={(e) => {
              console.log('Source filter changed:', e.target.value);
              setSourceFilter(e.target.value);
              setPage(0); // Reset to first page when filter changes
            }}
          >
            <MenuItem value="all">All Sources</MenuItem>
            {[...new Set(taskTypes.map(tt => tt.plugin_source).filter(Boolean))].map(source => (
              <MenuItem key={source} value={source}>{source}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

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
              {paginatedTaskTypes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No task types found matching your criteria.
                  </TableCell>
                </TableRow>
              ) : (
                paginatedTaskTypes.map((taskType) => (
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
          <TablePagination
            component="div"
            count={filteredTaskTypes.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
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