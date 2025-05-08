import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Tooltip,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { Info as InfoIcon } from '@mui/icons-material';
import { useTaskTypeStore } from '../stores/taskTypeStore';

const TaskConfigForm = ({ taskConfig, onSave, onCancel }) => {
  const { taskTypes, loading, error, fetchTaskTypes } = useTaskTypeStore();
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [taskType, setTaskType] = useState(null);

  useEffect(() => {
    // Fetch task types when component mounts
    fetchTaskTypes().catch(err => {
      console.error('Error fetching task types:', err);
    });
  }, [fetchTaskTypes]);

  useEffect(() => {
    console.log('TaskConfig:', taskConfig);
    console.log('TaskTypes:', taskTypes);
    
    if (taskConfig && taskTypes) {
      const foundTaskType = taskTypes.find(t => t.type_key === taskConfig.type_key);
      console.log('Found TaskType:', foundTaskType);
      
      setFormData(taskConfig.config || {});
      setTaskType(foundTaskType);
    }
  }, [taskConfig, taskTypes]);

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    validateField(field, value);
  };

  const validateField = (field, value) => {
    if (!taskType?.config_schema) return;

    const schema = taskType.config_schema;
    const fieldSchema = schema.properties[field];
    const isRequired = schema.required?.includes(field);

    let error = '';
    if (isRequired && !value) {
      error = 'This field is required';
    } else if (fieldSchema) {
      if (fieldSchema.type === 'string' && fieldSchema.minLength && value.length < fieldSchema.minLength) {
        error = `Minimum length is ${fieldSchema.minLength}`;
      } else if (fieldSchema.type === 'number' && fieldSchema.minimum && value < fieldSchema.minimum) {
        error = `Minimum value is ${fieldSchema.minimum}`;
      } else if (fieldSchema.type === 'number' && fieldSchema.maximum && value > fieldSchema.maximum) {
        error = `Maximum value is ${fieldSchema.maximum}`;
      }
    }

    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  };

  const validateForm = () => {
    if (!taskType?.config_schema) return true;

    const schema = taskType.config_schema;
    const newErrors = {};

    // Check required fields
    schema.required?.forEach(field => {
      if (!formData[field]) {
        newErrors[field] = 'This field is required';
      }
    });

    // Validate each field
    Object.keys(schema.properties || {}).forEach(field => {
      validateField(field, formData[field]);
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave({
        type_key: taskConfig.type_key,
        config: formData
      });
    }
  };

  const renderField = (fieldName, schema) => {
    const value = formData[fieldName] || '';
    const error = errors[fieldName];
    const isRequired = taskType.config_schema.required?.includes(fieldName);

    return (
      <Grid item xs={12} key={fieldName}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
          <TextField
            fullWidth
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {schema.title || fieldName}
                {isRequired && (
                  <Typography component="span" sx={{ color: 'error.main' }}>
                    *
                  </Typography>
                )}
              </Box>
            }
            value={value}
            onChange={handleChange(fieldName)}
            error={!!error}
            helperText={error || schema.description}
            required={isRequired}
            multiline={schema.type === 'string' && schema.format === 'multiline'}
            rows={schema.type === 'string' && schema.format === 'multiline' ? 4 : 1}
            type={schema.type === 'number' ? 'number' : 'text'}
          />
          {schema.description && (
            <Tooltip title={schema.description} arrow placement="top">
              <IconButton size="small" sx={{ mt: 1 }}>
                <InfoIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Grid>
    );
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">Error loading task types: {error}</Typography>
      </Paper>
    );
  }

  if (!taskTypes || taskTypes.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>No task types available</Typography>
      </Paper>
    );
  }

  if (!taskConfig) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>No task selected</Typography>
      </Paper>
    );
  }

  if (!taskType) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Loading task configuration...</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              {taskType.name} Configuration
            </Typography>
            {taskType.description && (
              <Typography variant="body2" color="text.secondary" paragraph>
                {taskType.description}
              </Typography>
            )}
          </Grid>

          {taskType.config_schema?.properties && 
            Object.entries(taskType.config_schema.properties).map(([field, schema]) => 
              renderField(field, schema)
            )
          }

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button onClick={onCancel}>Cancel</Button>
              <Button 
                type="submit" 
                variant="contained" 
                color="primary"
              >
                Save
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default TaskConfigForm; 