import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography, IconButton, Tooltip } from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import { useTaskTypeStore } from '../stores/taskTypeStore';

const checkNodeValidity = (node, taskTypes) => {
  // If no task types are loaded yet, consider the node valid
  if (!taskTypes || taskTypes.length === 0) return true;

  const taskType = taskTypes.find(type => type.type_key === node.data.type);
  
  // If no matching task type found, consider the node valid
  if (!taskType) return true;

  // If no config schema defined, consider the node valid
  if (!taskType.config_schema) return true;

  const requiredFields = taskType.config_schema.required || [];
  const configDetails = node.data.config || {};

  // If no required fields, consider the node valid
  if (requiredFields.length === 0) return true;

  // Check if all required fields have valid values
  return requiredFields.every(field => {
    const value = configDetails[field];
    // Consider boolean false as valid
    if (typeof value === 'boolean') return true;
    // Check for other types
    return value !== undefined && value !== null && value !== '';
  });
};

const YAMLTaskNode = memo(({ data }) => {
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
        position: 'relative',
        '&:hover': {
          boxShadow: 1,
          borderColor: 'primary.main'
        }
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Typography variant="subtitle2" noWrap sx={{ flex: 1 }}>
          {data.label || data.name || 'Unnamed Task'}
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
        {data.type}
      </Typography>
      {data.description && (
        <Typography 
          variant="caption" 
          color="text.secondary" 
          display="block"
          sx={{
            mt: 0.5,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {data.description}
        </Typography>
      )}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </Box>
  );
});

YAMLTaskNode.displayName = 'YAMLTaskNode';

export default YAMLTaskNode; 