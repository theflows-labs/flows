import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';

const taskTypes = [
  { value: 'python', label: 'Python' },
  { value: 'bash', label: 'Bash' },
  { value: 's3', label: 'S3' },
  { value: 'athena', label: 'Athena' },
];

function TaskConfigForm({ node, onUpdate }) {
  const { register, handleSubmit, setValue } = useForm({
    defaultValues: {
      type: node.data.type,
      label: node.data.label,
      ...node.data.config,
    },
  });

  const onSubmit = (data) => {
    onUpdate({
      type: data.type,
      label: data.label,
      config: {
        ...data,
        type: undefined,
        label: undefined,
      },
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel>Task Type</InputLabel>
            <Select
              {...register('type')}
              label="Task Type"
              onChange={(e) => {
                setValue('type', e.target.value);
                handleSubmit(onSubmit)();
              }}
            >
              {taskTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <TextField
            {...register('label')}
            label="Task Label"
            fullWidth
            onChange={(e) => {
              setValue('label', e.target.value);
              handleSubmit(onSubmit)();
            }}
          />
        </Grid>
        {node.data.type === 'python' && (
          <>
            <Grid item xs={12}>
              <TextField
                {...register('python_callable')}
                label="Python Callable"
                fullWidth
                onChange={(e) => {
                  setValue('python_callable', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('op_kwargs')}
                label="Operator Arguments (JSON)"
                fullWidth
                multiline
                rows={4}
                onChange={(e) => {
                  setValue('op_kwargs', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
          </>
        )}
        {node.data.type === 'bash' && (
          <Grid item xs={12}>
            <TextField
              {...register('bash_command')}
              label="Bash Command"
              fullWidth
              multiline
              rows={4}
              onChange={(e) => {
                setValue('bash_command', e.target.value);
                handleSubmit(onSubmit)();
              }}
            />
          </Grid>
        )}
        {node.data.type === 's3' && (
          <>
            <Grid item xs={12}>
              <TextField
                {...register('bucket')}
                label="S3 Bucket"
                fullWidth
                onChange={(e) => {
                  setValue('bucket', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('key')}
                label="S3 Key"
                fullWidth
                onChange={(e) => {
                  setValue('key', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
          </>
        )}
        {node.data.type === 'athena' && (
          <>
            <Grid item xs={12}>
              <TextField
                {...register('query')}
                label="Athena Query"
                fullWidth
                multiline
                rows={4}
                onChange={(e) => {
                  setValue('query', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('database')}
                label="Database"
                fullWidth
                onChange={(e) => {
                  setValue('database', e.target.value);
                  handleSubmit(onSubmit)();
                }}
              />
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
}

export default TaskConfigForm; 