import { Box, Typography } from '@mui/material';

function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1">
        Welcome to Flows UI. Use the navigation to create and manage your DAGs.
      </Typography>
    </Box>
  );
}

export default Dashboard; 