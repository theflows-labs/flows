import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  FormControl,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  InputLabel,
  Tooltip,
  IconButton,
  Grid,
  Divider,
} from '@mui/material';
import { Info as InfoIcon } from '@mui/icons-material';

const YAMLTaskConfigForm = ({ open, onClose, task, onSave }) => {
  const [formData, setFormData] = useState({
    id: '',
    type: '',
    name: '',
    description: '',
    config: {},
    sequence: 1
  });

  useEffect(() => {
    if (task) {
      setFormData({
        id: task.data.task_id || '',
        type: task.data.type || '',
        name: task.data.label || '',
        description: task.data.description || '',
        config: task.data.config || {},
        sequence: task.data.sequence || 1
      });
    }
  }, [task]);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleConfigChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [field]: value
      }
    }));
  };

  const handleSave = () => {
    onSave({
      ...task,
      data: {
        ...task.data,
        task_id: formData.id,
        type: formData.type,
        label: formData.name,
        description: formData.description,
        config: formData.config,
        sequence: formData.sequence
      }
    });
    onClose();
  };

  const renderConfigField = (key, value) => {
    if (typeof value === 'boolean') {
      return (
        <FormControlLabel
          key={key}
          control={
            <Switch
              checked={formData.config[key] || false}
              onChange={(e) => handleConfigChange(key, e.target.checked)}
            />
          }
          label={key}
        />
      );
    }

    if (typeof value === 'number') {
      return (
        <TextField
          key={key}
          label={key}
          type="number"
          value={formData.config[key] || ''}
          onChange={(e) => handleConfigChange(key, parseFloat(e.target.value))}
          fullWidth
          margin="normal"
        />
      );
    }

    if (Array.isArray(value)) {
      return (
        <FormControl key={key} fullWidth margin="normal">
          <InputLabel>{key}</InputLabel>
          <Select
            value={formData.config[key] || ''}
            onChange={(e) => handleConfigChange(key, e.target.value)}
            label={key}
          >
            {value.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      );
    }

    return (
      <TextField
        key={key}
        label={key}
        value={formData.config[key] || ''}
        onChange={(e) => handleConfigChange(key, e.target.value)}
        fullWidth
        margin="normal"
      />
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Task Configuration</Typography>
          <Typography variant="caption" color="textSecondary">
            ID: {formData.id}
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Task ID"
                value={formData.id}
                onChange={(e) => handleChange('id', e.target.value)}
                fullWidth
                margin="normal"
                disabled
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Task Type"
                value={formData.type}
                onChange={(e) => handleChange('type', e.target.value)}
                fullWidth
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Task Name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                fullWidth
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                fullWidth
                multiline
                rows={2}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Sequence"
                type="number"
                value={formData.sequence}
                onChange={(e) => handleChange('sequence', parseInt(e.target.value))}
                fullWidth
                margin="normal"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Configuration
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(formData.config).map(([key, value]) => (
              <Grid item xs={12} md={6} key={key}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {renderConfigField(key, value)}
                  <Tooltip title={`Configure ${key}`}>
                    <IconButton size="small">
                      <InfoIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default YAMLTaskConfigForm; 