import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  TextField,
  IconButton,
  Grid,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  InputAdornment,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as RunIcon,
  History as HistoryIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import useFlowStore from '../stores/flowStore';

const FlowsList = () => {
  const navigate = useNavigate();
  const { flows, fetchFlows, deleteFlow, downloadFlowYAML } = useFlowStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
  });
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState(null);

  useEffect(() => {
    fetchFlows();
  }, [fetchFlows]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleDeleteClick = (flow) => {
    setSelectedFlow(flow);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteFlow(selectedFlow.flow_id);
      setDeleteConfirmOpen(false);
      setSelectedFlow(null);
    } catch (error) {
      console.error('Error deleting flow:', error);
    }
  };

  // const handleRunFlow = async (flowId) => {
  //   try {
  //     const response = await fetch(`/api/executions/${flowId}`, {
  //       method: 'POST',
  //     });
  //     if (!response.ok) throw new Error('Failed to start flow execution');
  //     // Optionally show success message or redirect to execution page
  //   } catch (error) {
  //     console.error('Error running flow:', error);
  //   }
  // };

  const filteredFlows = flows.filter(flow => {
    const matchesSearch = flow.flow_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         flow.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Add more filter conditions as needed
    return matchesSearch;
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Flows
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/flows/new')}
        >
          Create New Flow
        </Button>
      </Box>

      {/* Search and Filter Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search flows..."
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={() => setFilterDialogOpen(true)}
              >
                Filters
              </Button>
              {Object.entries(filters).map(([key, value]) => (
                value !== 'all' && (
                  <Chip
                    key={key}
                    label={`${key}: ${value}`}
                    onDelete={() => handleFilterChange(key, 'all')}
                  />
                )
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Flows Grid */}
      <Grid container spacing={3}>
        {filteredFlows.map((flow) => (
          <Grid item xs={12} sm={6} md={4} key={flow.flow_id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" noWrap>
                  {flow.flow_id}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Created: {new Date(flow.created_dt).toLocaleDateString()}
                </Typography>
                <Typography variant="body2" sx={{ 
                  height: '3em',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {flow.description || 'No description'}
                </Typography>
                <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    size="small"
                    label={flow.is_active ? 'Active' : 'Inactive'}
                    color={flow.is_active ? 'success' : 'default'}
                  />
                  <Chip
                    size="small"
                    label={`Tasks: ${flow.config_details?.nodes?.length || 0}`}
                  />
                </Box>
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end' }}>
                {/* <Tooltip title="View Execution History">
                  <IconButton 
                    size="small"
                    onClick={() => navigate(`/flows/${flow.flow_id}/executions`)}
                  >
                    <HistoryIcon />
                  </IconButton>
                </Tooltip> */}
                {/* <Tooltip title="Run Flow">
                  <IconButton 
                    size="small"
                    onClick={() => handleRunFlow(flow.flow_id)}
                  >
                    <RunIcon />
                  </IconButton>
                </Tooltip> */}
                <Tooltip title="Edit Flow">
                  <IconButton 
                    size="small"
                    onClick={() => navigate(`/flows/${flow.flow_id}`)}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete Flow">
                  <IconButton 
                    size="small"
                    onClick={() => handleDeleteClick(flow)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Download YAML">
                  <IconButton 
                    size="small"
                    onClick={() => downloadFlowYAML(flow.flow_id)}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filter Dialog */}
      <Dialog
        open={filterDialogOpen}
        onClose={() => setFilterDialogOpen(false)}
      >
        <DialogTitle>Filter Flows</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              select
              fullWidth
              label="Status"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </TextField>
            <TextField
              select
              fullWidth
              label="Date Range"
              value={filters.dateRange}
              onChange={(e) => handleFilterChange('dateRange', e.target.value)}
            >
              <MenuItem value="all">All Time</MenuItem>
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="week">This Week</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFilterDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained"
            onClick={() => {
              setFilterDialogOpen(false);
              // Apply filters
            }}
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the flow "{selectedFlow?.flow_id}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button 
            color="error"
            onClick={handleDeleteConfirm}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FlowsList; 