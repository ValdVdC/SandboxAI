import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Loading from './components/Loading';
import Login from './pages/Login';
import Register from './pages/Register';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import PromptList from './pages/PromptList';
import CreatePrompt from './pages/CreatePrompt';
import PromptDetail from './pages/PromptDetail';
import TestExecution from './pages/TestExecution';
import VersionComparison from './pages/VersionComparison';
import './styles/global.css';

const AppRoutes: React.FC = () => {
  const { isLoading, user } = useAuth();

  if (isLoading) {
    return <Loading message="Iniciando aplicação..." />;
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/prompts"
        element={
          <PrivateRoute>
            <PromptList />
          </PrivateRoute>
        }
      />
      <Route
        path="/create-prompt"
        element={
          <PrivateRoute>
            <CreatePrompt />
          </PrivateRoute>
        }
      />
      <Route
        path="/prompts/:id"
        element={
          <PrivateRoute>
            <PromptDetail />
          </PrivateRoute>
        }
      />
      <Route
        path="/test/:promptId"
        element={
          <PrivateRoute>
            <TestExecution />
          </PrivateRoute>
        }
      />
      <Route
        path="/prompts/:id/compare"
        element={
          <PrivateRoute>
            <VersionComparison />
          </PrivateRoute>
        }
      />

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
