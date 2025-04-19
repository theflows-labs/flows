import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import FlowsList from './pages/FlowsList';
import FlowBuilder from './pages/FlowBuilder';

// Create a theme instance
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/flows" element={<FlowsList />} />
            <Route path="/flows/new" element={<FlowBuilder />} />
            <Route path="/flows/:flowId" element={<FlowBuilder />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App; 