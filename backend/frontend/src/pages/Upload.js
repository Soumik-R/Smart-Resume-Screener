import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  Input, 
  Button, 
  Space, 
  Spin, 
  Typography, 
  message,
  Divider,
  List,
  Tag
} from 'antd';
import { 
  UploadOutlined, 
  InboxOutlined, 
  CheckCircleOutlined,
  LoadingOutlined 
} from '@ant-design/icons';
import { useDropzone } from 'react-dropzone';
import { uploadJD, uploadResume, matchResumes } from '../services/api';
import '../styles/Upload.css';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const UploadPage = () => {
  const navigate = useNavigate();
  // const { isDarkMode } = useTheme(); // Removed - handled by ConfigProvider
  
  // State management
  const [jdText, setJdText] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [successData, setSuccessData] = useState(null);
  const [jdId, setJdId] = useState(null);

  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    onDrop: (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        rejectedFiles.forEach(file => {
          if (file.file.size > 5 * 1024 * 1024) {
            message.error(`${file.file.name}: File size exceeds 5MB limit`);
          } else {
            message.error(`${file.file.name}: Invalid file type. Only PDF and TXT allowed.`);
          }
        });
      }
      
      if (acceptedFiles.length > 0) {
        const newFiles = acceptedFiles.map(file => ({
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          id: Math.random().toString(36).substr(2, 9)
        }));
        setFiles(prev => [...prev, ...newFiles]);
        message.success(`Added ${acceptedFiles.length} file(s)`);
      }
    }
  });

  // Remove file from list
  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Validate form
  const validateForm = () => {
    if (!jdText.trim()) {
      message.error('Please enter a job description');
      return false;
    }
    
    if (jdText.trim().length < 20) {
      message.error('Job description must be at least 20 characters');
      return false;
    }
    
    if (files.length === 0) {
      message.error('Please upload at least one resume');
      return false;
    }
    
    return true;
  };

  // Handle upload only
  const handleUpload = async () => {
    console.log('handleUpload started');
    if (!validateForm()) {
      console.log('handleUpload ended (validation failed)');
      return;
    }
    
    setLoading(true);
    setUploadProgress('Uploading job description...');
    
    try {
      // Step 1: Upload Job Description
      console.log('📤 Starting JD upload...');
      console.log('JD Text length:', jdText.length);
      console.log('JD Text preview:', jdText.substring(0, 100));
      const jdResponse = await uploadJD(jdText);
      console.log('✅ JD Upload response:', jdResponse);
      const uploadedJdId = jdResponse.jd_id;
      setJdId(uploadedJdId);
      // Step 2: Upload all resumes
      setUploadProgress(`Uploading resumes (0/${files.length})...`);
      const resumeIds = [];
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i].file);
        setUploadProgress(`Uploading resumes (${i + 1}/${files.length})...`);
        const resumeResponse = await uploadResume(formData);
        console.log(`📄 Resume ${i + 1} uploaded:`, resumeResponse);
        // Backend returns 'candidate_id' not 'resume_id'
        const candidateId = resumeResponse.candidate_id;
        console.log(`  ✓ Candidate ID: ${candidateId}`);
        resumeIds.push(candidateId);
      }
      console.log('📊 All resume IDs collected:', resumeIds);
      setUploadProgress('Upload complete. Ready to match.');
      message.success('Upload complete. Now click Match to proceed.');
      setLoading(false);
      // Store resumeIds for matching
      window._uploadedResumeIds = resumeIds;
      window._uploadedJdId = uploadedJdId;
    } catch (error) {
      setUploadProgress('');
      setLoading(false);
      console.error('Upload error:', error);
    }
    console.log('handleUpload ended');
  };

  // Handle match only
  const handleMatch = async () => {
    console.log('handleMatch started');
    setLoading(true);
    setUploadProgress('Matching resumes with job description...');
    try {
      // Use stored IDs if available
      const uploadedJdId = window._uploadedJdId || jdId;
      const resumeIds = window._uploadedResumeIds || [];
      if (!uploadedJdId || !resumeIds.length) {
        message.error('Please upload job description and resumes first.');
        setLoading(false);
        setUploadProgress('');
        console.log('handleMatch ended (missing data)');
        return;
      }
      console.log('🎯 Starting matching with JD:', uploadedJdId);
      const matchResponse = await matchResumes(uploadedJdId, resumeIds);
      console.log('✅ Matching complete:', matchResponse);
      setSuccessData({
        jdId: uploadedJdId,
        totalResumes: resumeIds.length,
        matchedCount: matchResponse.results?.length || resumeIds.length
      });
      setUploadProgress('');
      message.success('All resumes matched successfully!');
    } catch (error) {
      setUploadProgress('');
      setLoading(false);
      console.error('Match error:', error);
    }
    setLoading(false);
    console.log('handleMatch ended');
  };

  // Reset form
  const handleReset = () => {
    setJdText('');
    setFiles([]);
    setLoading(false);
    setUploadProgress('');
    setSuccessData(null);
    setJdId(null);
  };

  // Navigate to dashboard with correct JD ID
  const handleViewShortlist = () => {
    // Prefer successData.jdId, fallback to window._uploadedJdId, then jdId
    const targetJdId = (successData && successData.jdId) || window._uploadedJdId || jdId;
    if (!targetJdId) {
      message.error('No Job Description ID found. Please upload and match again.');
      return;
    }
    navigate(`/dashboard/${targetJdId}`);
  };

  // If successful, show success view
  if (successData) {
    return (
      <div className="upload-container">
        <Card className="upload-card success-card">
          <div className="success-content">
            <CheckCircleOutlined className="success-icon" />
            <Title level={2} className="success-title">Upload Successful!</Title>
            <Paragraph className="success-text">
              Successfully processed {successData.totalResumes} resume(s) and matched them 
              against your job description.
            </Paragraph>
            
            <div className="success-stats">
              <div className="stat-item">
                <Text strong>Job Description ID:</Text>
                <Text code>{successData.jdId}</Text>
              </div>
              <div className="stat-item">
                <Text strong>Resumes Uploaded:</Text>
                <Text>{successData.totalResumes}</Text>
              </div>
              <div className="stat-item">
                <Text strong>Matches Generated:</Text>
                <Text>{successData.matchedCount}</Text>
              </div>
            </div>
            
            <Space size="large" className="success-actions">
              <Button 
                type="primary" 
                size="large"
                onClick={handleViewShortlist}
                style={{ 
                  height: '45px',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
              >
                View Shortlist
              </Button>
              <Button 
                size="large"
                onClick={handleReset}
                style={{ 
                  height: '45px',
                  fontSize: '16px'
                }}
              >
                Upload More
              </Button>
            </Space>
          </div>
        </Card>
      </div>
    );
  }

  // Main upload form
  return (
    <div className="upload-container">
      <Card className="upload-card">
        <Title level={2} className="upload-title" style={{ textAlign: 'center', marginBottom: '30px' }}>
          Upload Job Description & Resumes
        </Title>
        
        {/* Job Description Section */}
        <div className="form-section">
          <Title level={4} className="section-title">
            1. Enter Job Description
          </Title>
          <TextArea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste your job description here (50-50,000 characters)..."
            rows={8}
            disabled={loading}
            showCount
            maxLength={50000}
            className="jd-textarea"
          />
          <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
            Include job title, requirements, responsibilities, and qualifications.
          </Text>
        </div>

        <Divider className="section-divider" />

        {/* Resume Upload Section */}
        <div className="form-section">
          <Title level={4} className="section-title">
            2. Upload Resumes (1-50 files)
          </Title>
          
          <div 
            {...getRootProps()} 
            className={`dropzone ${isDragActive ? 'active' : ''} ${loading ? 'disabled' : ''}`}
          >
            <input {...getInputProps()} disabled={loading} />
            <InboxOutlined className="dropzone-icon" />
            {isDragActive ? (
              <Text className="dropzone-text">Drop the files here...</Text>
            ) : (
              <>
                <Text className="dropzone-text">
                  Drag & drop resume files here, or click to select
                </Text>
                <Text type="secondary" className="dropzone-hint">
                  Supports: PDF, TXT | Max size: 5MB per file | Max files: 50
                </Text>
              </>
            )}
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="file-list">
              <Text strong className="file-list-title">
                Selected Files ({files.length}):
              </Text>
              <List
                dataSource={files}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="text" 
                        danger 
                        size="small"
                        onClick={() => removeFile(item.id)}
                        disabled={loading}
                      >
                        Remove
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      title={<Text className="file-name">{item.name}</Text>}
                      description={
                        <Space>
                          <Tag color="blue">{item.type.includes('pdf') ? 'PDF' : 'TXT'}</Tag>
                          <Text type="secondary">{formatFileSize(item.size)}</Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
                style={{ marginTop: '16px' }}
              />
            </div>
          )}
        </div>

        <Divider className="section-divider" />

        {/* Submit Section */}
        <div className="submit-section">
          {loading && (
            <div className="progress-container">
              <Spin 
                indicator={<LoadingOutlined style={{ fontSize: 32 }} spin />}
                size="large"
              />
              <Text strong className="progress-text" style={{ marginTop: '16px' }}>
                {uploadProgress}
              </Text>
            </div>
          )}
          
          {!loading && (
            <Space size="large">
              <Button
                type="primary"
                size="large"
                icon={<UploadOutlined />}
                onClick={handleUpload}
                disabled={!jdText.trim() || files.length === 0}
                style={{
                  height: '50px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  paddingLeft: '40px',
                  paddingRight: '40px'
                }}
              >
                Upload
              </Button>
              <Button
                type="primary"
                size="large"
                onClick={handleMatch}
                disabled={(!window._uploadedResumeIds || !window._uploadedResumeIds.length) && (!jdId || !files.length)}
                style={{
                  height: '50px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  paddingLeft: '40px',
                  paddingRight: '40px',
                  background: '#0015ff',
                  borderColor: '#0015ff'
                }}
              >
                Match
              </Button>
              <Button
                size="large"
                onClick={handleReset}
                style={{
                  height: '50px',
                  fontSize: '16px'
                }}
              >
                Clear All
              </Button>
            </Space>
          )}
        </div>
      </Card>
    </div>
  );
};

export default UploadPage;
