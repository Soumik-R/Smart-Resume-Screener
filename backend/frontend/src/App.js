import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Layout, theme } from 'antd';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import UploadPage from './pages/Upload';
import Dashboard from './pages/Dashboard';
import './App.css';

const { Content } = Layout;

function AppContent() {
  const { isDarkMode } = useTheme();

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: isDarkMode ? '#1890ff' : '#000080',
          colorLink: isDarkMode ? '#40a9ff' : '#000080',
          colorLinkHover: isDarkMode ? '#69c0ff' : '#0000cd',
          borderRadius: 8,
          colorBgBase: isDarkMode ? '#1a1a2e' : '#ffffff',
          colorTextBase: isDarkMode ? '#ffffff' : '#000000',
        },
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <Layout className={`app-layout ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
        <Navbar />
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/dashboard/:jdId" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/upload" replace />} />
          </Routes>
        </Content>
        <Footer />
      </Layout>
    </ConfigProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
}

export default App;
