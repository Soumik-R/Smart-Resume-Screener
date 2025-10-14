import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Switch, Space } from 'antd';
import { 
  UploadOutlined, 
  DashboardOutlined, 
  BulbOutlined,
  ThunderboltOutlined,
  HomeOutlined
} from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Navbar.css';

const { Header } = Layout;

const Navbar = () => {
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();

  const menuItems = [
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: <Link to="/upload">Upload</Link>,
    },
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      disabled: true,
    }
  ];

  return (
    <Header className={`navbar-header ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/upload" className="navbar-logo">
          <ThunderboltOutlined className="logo-icon" />
          <span className="logo-text">Smart Screener</span>
        </Link>

        {/* Desktop Menu */}
        <div className="navbar-menu-desktop">
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            className="navbar-menu"
            style={{ 
              backgroundColor: 'transparent',
              borderBottom: 'none',
              minWidth: '200px'
            }}
          />
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

        {/* Mobile Menu */}
        <div className="navbar-menu-mobile">
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={[
              {
                key: 'home',
                icon: <HomeOutlined />,
                label: <Link to="/upload">Home</Link>,
              }
            ]}
            className="navbar-menu-mobile-items"
            style={{ 
              backgroundColor: 'transparent',
              borderBottom: 'none'
            }}
          />
        </div>
      </div>
    </Header>
  );
};

export default Navbar;
