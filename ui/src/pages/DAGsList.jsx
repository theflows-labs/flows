import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Box,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Skeleton,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Search as SearchIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useDAGStore } from '../store/dagStore';

const DAGsList = () => {
  const navigate = useNavigate();
  const [dags, setDags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [scheduleFilter, setScheduleFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [dagToDelete, setDagToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const { fetchDAGs, deleteDAG, downloadDAGYAML } = useDAGStore();

  useEffect(() => {
    const loadDAGs = async () => {
      try {
        const data = await fetchDAGs();
        setDags(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load DAGs');
        setLoading(false);
        console.error('Error loading DAGs:', err);
      }
    };

    loadDAGs();
  }, [fetchDAGs]);

  const handleDelete = async () => {
    try {
      await deleteDAG(dagToDelete.id);
      setDags(dags.filter(dag => dag.id !== dagToDelete.id));
      setDeleteDialogOpen(false);
      setSnackbar({
        open: true,
        message: 'DAG deleted successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to delete DAG',
        severity: 'error',
      });
    }
  };

  const handleDownloadYAML = async (dagId) => {
    try {
      await downloadDAGYAML(dagId);
      setSnackbar({
        open: true,
        message: 'YAML downloaded successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to download YAML',
        severity: 'error',
      });
    }
  };

  const filteredDags = dags
    .filter(dag => {
      const matchesSearch = dag.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (dag.description && dag.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesSchedule = scheduleFilter === 'all' || dag.schedule === scheduleFilter;
      return matchesSearch && matchesSchedule;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'schedule':
          return (a.schedule || '').localeCompare(b.schedule || '');
        case 'created':
          return new Date(b.created_at) - new Date(a.created_at);
        default:
          return 0;
      }
    });

  const LoadingSkeleton = () => (
    <Grid container spacing={3}>
      {[1, 2, 3].map((i) => (
        <Grid item xs={12} sm={6} md={4} key={i}>
          <Card>
            <CardContent>
              <Skeleton variant="text" width="60%" height={40} />
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="text" width="40%" />
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Skeleton variant="rectangular" width={80} height={36} />
                <Skeleton variant="rectangular" width={80} height={36} />
                <Skeleton variant="rectangular" width={80} height={36} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          DAGs
        </Typography>
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to="/dags/new"
        >
          Create New DAG
        </Button>
      </Box>

      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search DAGs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 200 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Schedule</InputLabel>
          <Select
            value={scheduleFilter}
            label="Schedule"
            onChange={(e) => setScheduleFilter(e.target.value)}
          >
            <MenuItem value="all">All Schedules</MenuItem>
            <MenuItem value="daily">Daily</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="none">None</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            label="Sort By"
            onChange={(e) => setSortBy(e.target.value)}
          >
            <MenuItem value="name">Name</MenuItem>
            <MenuItem value="schedule">Schedule</MenuItem>
            <MenuItem value="created">Created Date</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {loading ? (
        <LoadingSkeleton />
      ) : (
        <Grid container spacing={3}>
          {filteredDags.map((dag) => (
            <Grid item xs={12} sm={6} md={4} key={dag.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {dag.name}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    {dag.description || 'No description'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Schedule: {dag.schedule || 'None'}
                  </Typography>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <IconButton
                      component={Link}
                      to={`/dags/${dag.id}`}
                      color="primary"
                      size="small"
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      component={Link}
                      to={`/dags/${dag.id}/edit`}
                      color="primary"
                      size="small"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDownloadYAML(dag.id)}
                      color="primary"
                      size="small"
                    >
                      <DownloadIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => {
                        setDagToDelete(dag);
                        setDeleteDialogOpen(true);
                      }}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete DAG</DialogTitle>
        <DialogContent>
          Are you sure you want to delete "{dagToDelete?.name}"?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">
            Delete
          </Button>
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
};

export default DAGsList; 