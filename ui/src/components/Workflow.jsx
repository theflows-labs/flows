import React from 'react';
import { Box, Typography, Tooltip, IconButton } from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import { useTaskTypeStore } from '../stores/taskTypeStore';

const checkNodeValidity = (node, taskTypes) => {
  const taskType = taskTypes.find(type => type.type_key === node.data.type_key);
  if (!taskType || !taskType.config_schema) return false;

  const requiredFields = taskType.config_schema.required || [];
  const configDetails = node.data.config || {};

  return requiredFields.every(field => {
    const value = configDetails[field];
    return value !== undefined && value !== null && value !== '';
  });
};

const nodeTypes = {
  task: ({ data }) => {
    const { taskTypes } = useTaskTypeStore();
    const isValid = checkNodeValidity({ data }, taskTypes);
    
    return (
      <Box
        sx={{
          padding: 2,
          borderRadius: 1,
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          minWidth: 150,
          position: 'relative'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Typography variant="subtitle2" noWrap sx={{ flex: 1 }}>
            {data.label}
          </Typography>
          <Tooltip title={isValid ? "All required fields are filled" : "Some required fields are missing"}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: isValid ? 'success.main' : 'error.main',
                flexShrink: 0
              }}
            />
          </Tooltip>
          <Tooltip title="Configure Task">
            <IconButton 
              size="small" 
              onClick={(e) => {
                e.stopPropagation();
                data.onConfigClick?.(data);
              }}
              sx={{ 
                ml: 1,
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
            >
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Typography variant="caption" color="text.secondary" display="block">
          {data.type_key}
        </Typography>
      </Box>
    );
  }
};

export { nodeTypes, checkNodeValidity }; 