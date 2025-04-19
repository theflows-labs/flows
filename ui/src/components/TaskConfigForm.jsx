import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

const TaskConfigForm = ({ node, taskTypes, onUpdate, onClose }) => {
  const [taskData, setTaskData] = useState({
    label: node.data.label,
    type: node.data.type,
    config: node.data.config,
  });

  const handleChange = (field, value) => {
    setTaskData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleConfigChange = (field, value) => {
    setTaskData((prev) => ({
      ...prev,
      config: {
        ...prev.config,
        [field]: value,
      },
    }));
  };

  const handleSubmit = () => {
    onUpdate({
      ...node,
      data: {
        ...node.data,
        ...taskData,
      },
    });
  };

  const renderConfigFields = () => {
    const taskType = taskTypes[taskData.type];
    if (!taskType) return null;

    const configFields = Object.entries(taskType.defaultConfig);
    
    return configFields.map(([field, defaultValue]) => {
      if (Array.isArray(defaultValue)) {
        return (
          <TextField
            key={field}
            fullWidth
            label={field}
            value={taskData.config[field]?.join(', ') || ''}
            onChange={(e) => handleConfigChange(field, e.target.value.split(',').map(s => s.trim()))}
            margin="normal"
            helperText={`Enter ${field} separated by commas`}
          />
        );
      }
      
      if (typeof defaultValue === 'object') {
        return (
          <TextField
            key={field}
            fullWidth
            label={field}
            value={JSON.stringify(taskData.config[field] || defaultValue)}
            onChange={(e) => {
              try {
                handleConfigChange(field, JSON.parse(e.target.value));
              } catch (error) {
                // Handle invalid JSON
              }
            }}
            margin="normal"
            multiline
            rows={4}
            helperText={`Enter ${field} as JSON`}
          />
        );
      }

      return (
        <TextField
          key={field}
          fullWidth
          label={field}
          value={taskData.config[field] || ''}
          onChange={(e) => handleConfigChange(field, e.target.value)}
          margin="normal"
        />
      );
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Task Configuration</Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      <TextField
        fullWidth
        label="Task Label"
        value={taskData.label}
        onChange={(e) => handleChange('label', e.target.value)}
        margin="normal"
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Task Type</InputLabel>
        <Select
          value={taskData.type}
          label="Task Type"
          onChange={(e) => handleChange('type', e.target.value)}
        >
          {Object.entries(taskTypes).map(([type, config]) => (
            <MenuItem key={type} value={type}>
              {config.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {renderConfigFields()}

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          onClick={handleSubmit}
          sx={{ mr: 1 }}
        >
          Update
        </Button>
        <Button
          variant="outlined"
          onClick={onClose}
        >
          Cancel
        </Button>
      </Box>
    </Paper>
  );
};

export default TaskConfigForm; 