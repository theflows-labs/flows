import React from 'react';
import { 
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Switch,
  FormControlLabel,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { CodeEditor } from './CodeEditor';

const JsonSchemaForm = ({ schema, formData, onChange, disabled = false }) => {
  const handleChange = (path, value) => {
    const newFormData = { ...formData };
    let current = newFormData;
    const parts = path.split('.');
    const lastPart = parts.pop();
    
    parts.forEach(part => {
      if (!current[part]) current[part] = {};
      current = current[part];
    });
    
    current[lastPart] = value;
    onChange(newFormData);
  };

  const renderField = (fieldSchema, path, fieldData) => {
    const fieldType = fieldSchema.type;
    const fieldTitle = fieldSchema.title || path.split('.').pop();
    const fieldDescription = fieldSchema.description;

    switch (fieldType) {
      case 'string':
        if (fieldSchema.enum) {
          return (
            <FormControl fullWidth margin="normal" disabled={disabled}>
              <InputLabel>{fieldTitle}</InputLabel>
              <Select
                value={fieldData || ''}
                onChange={(e) => handleChange(path, e.target.value)}
                label={fieldTitle}
              >
                {fieldSchema.enum.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              {fieldDescription && (
                <FormHelperText>{fieldDescription}</FormHelperText>
              )}
            </FormControl>
          );
        }
        return (
          <TextField
            fullWidth
            margin="normal"
            label={fieldTitle}
            value={fieldData || ''}
            onChange={(e) => handleChange(path, e.target.value)}
            helperText={fieldDescription}
            disabled={disabled}
          />
        );

      case 'number':
      case 'integer':
        return (
          <TextField
            fullWidth
            margin="normal"
            label={fieldTitle}
            type="number"
            value={fieldData || ''}
            onChange={(e) => handleChange(path, Number(e.target.value))}
            helperText={fieldDescription}
            disabled={disabled}
          />
        );

      case 'boolean':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={!!fieldData}
                onChange={(e) => handleChange(path, e.target.checked)}
                disabled={disabled}
              />
            }
            label={
              <Box>
                <Typography variant="body1">{fieldTitle}</Typography>
                {fieldDescription && (
                  <Typography variant="caption" color="textSecondary">
                    {fieldDescription}
                  </Typography>
                )}
              </Box>
            }
          />
        );

      case 'object':
        if (path === 'config_schema') {
          return (
            <Box mt={2} mb={2}>
              <Typography variant="subtitle1" gutterBottom>
                {fieldTitle}
              </Typography>
              {fieldDescription && (
                <Typography variant="caption" color="textSecondary" paragraph>
                  {fieldDescription}
                </Typography>
              )}
              <CodeEditor
                value={fieldData ? JSON.stringify(fieldData, null, 2) : '{}'}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    handleChange(path, parsed);
                  } catch (e) {
                    // Handle JSON parse error
                  }
                }}
                language="json"
                disabled={disabled}
              />
            </Box>
          );
        }
        return (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>{fieldTitle}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {fieldDescription && (
                <Typography variant="caption" color="textSecondary" paragraph>
                  {fieldDescription}
                </Typography>
              )}
              <Box pl={2}>
                {Object.entries(fieldSchema.properties || {}).map(([key, propSchema]) => (
                  <Box key={key}>
                    {renderField(
                      propSchema,
                      `${path}.${key}`,
                      fieldData?.[key]
                    )}
                  </Box>
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>
        );

      case 'array':
        // For now, we'll handle arrays of strings only
        return (
          <TextField
            fullWidth
            margin="normal"
            label={fieldTitle}
            value={(fieldData || []).join(', ')}
            onChange={(e) => handleChange(path, e.target.value.split(',').map(s => s.trim()))}
            helperText={`${fieldDescription} (comma-separated values)`}
            disabled={disabled}
          />
        );

      default:
        return null;
    }
  };

  return (
    <Box>
      {Object.entries(schema.properties).map(([key, fieldSchema]) => (
        <Box key={key}>
          {renderField(fieldSchema, key, formData?.[key])}
        </Box>
      ))}
    </Box>
  );
};

export default JsonSchemaForm; 