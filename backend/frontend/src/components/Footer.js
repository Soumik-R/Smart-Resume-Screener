import React from 'react';
import { Layout, Typography, Space, Divider } from 'antd';
import { 
  GithubOutlined, 
  CopyrightOutlined,
  ThunderboltOutlined 
} from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Footer.css';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

const Footer = () => {
  const { isDarkMode } = useTheme();
  const currentYear = new Date().getFullYear();

  return (
    <AntFooter className={`app-footer ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="footer-container">
        <div className="footer-content">
          {/* Branding Section */}
          <div className="footer-brand">
            <Space align="center">
              <ThunderboltOutlined className="footer-icon" />
              <div>
                <Text strong className="footer-title">Smart Resume Screener</Text>
              </div>
            </Space>
          </div>

          <Divider type="vertical" className="footer-divider" />

          {/* Developer Section */}
          <div className="footer-version">
            <Space direction="vertical" size={0}>
              <Text strong className="footer-developer">Developed by Soumik Roy</Text>
            </Space>
          </div>

          <Divider type="vertical" className="footer-divider" />

          {/* Links Section */}
          <div className="footer-links">
            <Space direction="vertical" size="small">
              <Link 
                href="https://github.com/Soumik-R/Smart-Resume-Screener" 
                target="_blank"
                className="footer-link"
              >
                <GithubOutlined /> GitHub Repository
              </Link>
              <Text type="secondary" className="footer-copyright">
                <CopyrightOutlined /> {currentYear} All Rights Reserved
              </Text>
            </Space>
          </div>
        </div>

        {/* Mobile Footer */}
        <div className="footer-mobile">
          <Space direction="vertical" align="center" size="small" style={{ width: '100%' }}>
            <Text strong className="footer-title">Smart Resume Screener</Text>
            <Text strong className="footer-developer">Developed by Soumik Roy</Text>
            <Link 
              href="https://github.com/Soumik-R/Smart-Resume-Screener" 
              target="_blank"
              className="footer-link"
            >
              <GithubOutlined /> GitHub
            </Link>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              <CopyrightOutlined /> {currentYear} All Rights Reserved
            </Text>
          </Space>
        </div>
      </div>
    </AntFooter>
  );
};

export default Footer;
