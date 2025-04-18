import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Paper, Typography } from '@mui/material';

const TaskNode = memo(({ data }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        padding: 2,
        minWidth: 150,
        backgroundColor: '#fff',
        border: '1px solid #ddd',
        borderRadius: 1,
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        {data.type}
      </Typography>
      <Typography variant="body2">{data.label}</Typography>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </Paper>
  );
});

TaskNode.displayName = 'TaskNode';

export default TaskNode; 