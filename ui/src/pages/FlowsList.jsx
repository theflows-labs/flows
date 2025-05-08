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
  Switch,
  CircularProgress,
  Alert,
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
  PowerSettingsNew as PowerIcon,
  Analytics as AnalyticsIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import useFlowStore from '../stores/flowStore';

const FlowsList = () => {
  const navigate = useNavigate();
  const { flows, fetchFlows, deleteFlow, downloadFlowYAML, activateFlow, deactivateFlow } = useFlowStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
  });
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState(null);
  const [toggleConfirmOpen, setToggleConfirmOpen] = useState(false);
  const [toggleAction, setToggleAction] = useState(null);
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [selectedFlowForAnalysis, setSelectedFlowForAnalysis] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

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

  const handleToggleActive = async (flow) => {
    setSelectedFlow(flow);
    setToggleAction(flow.is_active ? 'deactivate' : 'activate');
    setToggleConfirmOpen(true);
  };

  const handleToggleConfirm = async () => {
    try {
      if (toggleAction === 'activate') {
        await activateFlow(selectedFlow.flow_id);
      } else {
        await deactivateFlow(selectedFlow.flow_id);
      }
      setToggleConfirmOpen(false);
      setSelectedFlow(null);
      setToggleAction(null);
    } catch (error) {
      console.error('Error toggling flow status:', error);
    }
  };

  const handleAnalyzeClick = async (flow) => {
    setSelectedFlowForAnalysis(flow);
    setAnalysisDialogOpen(true);
    setAnalysisLoading(true);
    setAnalysisResults(null); // Reset previous results
    
    try {
      const response = await fetch(`/api/flows/${flow.flow_id}/analyze`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze flow');
      }
      const results = await response.json();
      console.log('Analysis results:', results); // Debug log
      setAnalysisResults(results);
    } catch (error) {
      console.error('Error analyzing flow:', error);
      setAnalysisResults({ 
        error: error.message,
        logs: 'Error occurred during analysis',
        yaml: '',
        status: 'error'
      });
    } finally {
      setAnalysisLoading(false);
    }
  };

  const filteredFlows = flows.filter(flow => {
    // Search term filter
    const matchesSearch = flow.flow_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         flow.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    const matchesStatus = filters.status === 'all' || 
                         (filters.status === 'active' && flow.is_active) ||
                         (filters.status === 'inactive' && !flow.is_active);
    
    // Date range filter
    const createdDate = new Date(flow.created_dt);
    const now = new Date();
    const matchesDateRange = filters.dateRange === 'all' ||
                            (filters.dateRange === 'today' && 
                             createdDate.toDateString() === now.toDateString()) ||
                            (filters.dateRange === 'week' && 
                             (now - createdDate) <= 7 * 24 * 60 * 60 * 1000) ||
                            (filters.dateRange === 'month' && 
                             (now - createdDate) <= 30 * 24 * 60 * 60 * 1000);
    
    return matchesSearch && matchesStatus && matchesDateRange;
  });

  const AnalysisDialog = ({ open, onClose, flow, analysis, loading, error }) => {
    if (!open) return null;

    return (
      <Dialog 
        open={open} 
        onClose={onClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Flow Analysis: {flow?.name || flow?.flow_id}
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          ) : analysis ? (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Analysis Logs
              </Typography>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  mb: 3,
                  backgroundColor: '#f5f5f5',
                  maxHeight: '300px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}
              >
                {analysis.logs ? (
                  <pre style={{ margin: 0 }}>{analysis.logs}</pre>
                ) : (
                  'No logs available'
                )}
              </Paper>

              <Typography variant="h6" gutterBottom>
                Generated YAML
              </Typography>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2,
                  backgroundColor: '#f5f5f5',
                  maxHeight: '400px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}
              >
                {analysis.yaml ? (
                  <pre style={{ margin: 0 }}>{analysis.yaml}</pre>
                ) : (
                  'No YAML available'
                )}
              </Paper>

              {analysis.status === 'error' && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {analysis.error}
                </Alert>
              )}
            </Box>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

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
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
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
                <Tooltip title="Analyze Flow">
                  <IconButton 
                    size="small"
                    onClick={() => handleAnalyzeClick(flow)}
                  >
                    <AnalyticsIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title={flow.is_active ? "Deactivate Flow" : "Activate Flow"}>
                  <IconButton 
                    size="small"
                    onClick={() => handleToggleActive(flow)}
                    color={flow.is_active ? "success" : "default"}
                  >
                    <PowerIcon />
                  </IconButton>
                </Tooltip>
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
            onClick={() => setFilterDialogOpen(false)}
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

      {/* Toggle Confirmation Dialog */}
      <Dialog
        open={toggleConfirmOpen}
        onClose={() => {
          setToggleConfirmOpen(false);
          setSelectedFlow(null);
          setToggleAction(null);
        }}
      >
        <DialogTitle>
          {toggleAction === 'activate' ? 'Activate Flow' : 'Deactivate Flow'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {toggleAction} the flow "{selectedFlow?.flow_id}"?
            {/* {toggleAction === 'deactivate' && ' This will stop any running executions.'} */}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setToggleConfirmOpen(false);
              setSelectedFlow(null);
              setToggleAction(null);
            }}
          >
            Cancel
          </Button>
          <Button 
            color={toggleAction === 'activate' ? 'success' : 'warning'}
            onClick={handleToggleConfirm}
          >
            {toggleAction === 'activate' ? 'Activate' : 'Deactivate'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Analysis Results Dialog */}
      <AnalysisDialog
        open={analysisDialogOpen}
        onClose={() => {
          setAnalysisDialogOpen(false);
          setSelectedFlowForAnalysis(null);
          setAnalysisResults(null);
        }}
        flow={selectedFlowForAnalysis}
        analysis={analysisResults}
        loading={analysisLoading}
        error={analysisResults?.error}
      />
    </Box>
  );
};

export default FlowsList; 