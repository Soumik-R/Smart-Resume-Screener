import React from 'react';
import { Link } from 'react-router-dom';
import { Layout, Switch, Space } from 'antd';
import { 
  BulbOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Navbar.css';

const { Header } = Layout;

const Navbar = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <Header className={`navbar-header ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/upload" className="navbar-logo">
          <ThunderboltOutlined className="logo-icon" />
          <span className="logo-text">Smart Screener</span>
        </Link>

        {/* Center Branding */}
        <div className="navbar-center-brand">
          <span className="center-brand-text">Unthinkable</span>
        </div>

        {/* Right Section */}
        <Space size="large" className="navbar-actions">
          <Space align="center" className="theme-toggle">
            <BulbOutlined style={{ fontSize: '18px', color: isDarkMode ? '#ffd700' : '#000080' }} />
            <Switch
              checked={isDarkMode}
              onChange={toggleTheme}
              checkedChildren="Dark"
              unCheckedChildren="Light"
              style={{
                backgroundColor: isDarkMode ? '#1890ff' : '#000080'
              }}
            />
          </Space>
        </Space>
      </div>
    </Header>
  );
};

export default Navbar;
