import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import UploadPage from './pages/Upload';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#000080',
          colorLink: '#000080',
          colorLinkHover: '#0000cd',
          borderRadius: 8,
        },
      }}
    >
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/dashboard/:jdId" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/upload" replace />} />
          </Routes>
        </div>
      </Router>
    </ConfigProvider>
  );
}

export default App;
