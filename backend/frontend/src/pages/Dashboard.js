import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Table, 
  Button, 
  Select, 
  Input, 
  Space, 
  Typography, 
  Tooltip, 
  Tag,
  Spin,
  message,
  Modal,
  InputNumber,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  DownloadOutlined, 
  SearchOutlined, 
  ReloadOutlined,
  ExperimentOutlined,
  TrophyOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { getShortlist, exportCSV } from '../services/api';
import ScoreRadar from '../components/ScoreRadar';
import '../styles/Dashboard.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const Dashboard = () => {
  const { jdId } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [candidates, setCandidates] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [threshold, setThreshold] = useState(7);
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [sortConfig] = useState({
    sortBy: 'overall_score',
    sortOrder: 'desc'
  });
  
  // What-If Simulator state
  const [whatIfModal, setWhatIfModal] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [simulatedScores, setSimulatedScores] = useState(null);
  
  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    avgScore: 0,
    topScore: 0,
    aboveThreshold: 0
  });

  // Fetch shortlist data
  const fetchShortlist = async (page = 1, pageSize = 10) => {
    if (!jdId) {
      message.error('No Job Description ID provided');
      navigate('/upload');
      return;
    }
    
    setLoading(true);
    try {
      const response = await getShortlist(
        jdId, 
        threshold, 
        page, 
        pageSize, 
        sortConfig.sortBy, 
        sortConfig.sortOrder
      );
      
      setCandidates(response.candidates || []);
      setFilteredCandidates(response.candidates || []);
      
      setPagination({
        current: response.page || page,
        pageSize: response.page_size || pageSize,
        total: response.total || 0
      });
      
      // Calculate statistics
      if (response.candidates && response.candidates.length > 0) {
        const scores = response.candidates.map(c => c.overall_score);
        const total = response.total || 0;
        const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
        const topScore = Math.max(...scores);
        const aboveThreshold = response.candidates.filter(c => c.overall_score >= threshold).length;
        
        setStats({ total, avgScore, topScore, aboveThreshold });
      }
      
      setLoading(false);
    } catch (error) {
      setLoading(false);
      console.error('Failed to fetch shortlist:', error);
    }
  };

  // Initial load
  useEffect(() => {
    fetchShortlist();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jdId, threshold, sortConfig]);

  // Search filter
  useEffect(() => {
    if (searchText.trim() === '') {
      setFilteredCandidates(candidates);
    } else {
      const filtered = candidates.filter(candidate =>
        candidate.candidate_id.toLowerCase().includes(searchText.toLowerCase()) ||
        candidate.resume_id.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredCandidates(filtered);
    }
  }, [searchText, candidates]);

  // Handle pagination change
  const handleTableChange = (newPagination, filters, sorter) => {
    fetchShortlist(newPagination.current, newPagination.pageSize);
  };

  // Handle export
  const handleExport = async () => {
    try {
      await exportCSV(jdId, threshold);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Open What-If Simulator
  const openWhatIfSimulator = (candidate) => {
    setSelectedCandidate(candidate);
    setSimulatedScores({
      skills_score: candidate.sub_scores.skills_score,
      experience_score: candidate.sub_scores.experience_score,
      education_score: candidate.sub_scores.education_score,
      cultural_fit_score: candidate.sub_scores.cultural_fit_score,
      achievements_score: candidate.sub_scores.achievements_score
    });
    setWhatIfModal(true);
  };

  // Calculate simulated overall score
  const calculateSimulatedOverall = (scores) => {
    const values = Object.values(scores);
    return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
  };

  // Reset What-If Simulator
  const resetSimulator = () => {
    if (selectedCandidate) {
      setSimulatedScores({
        skills_score: selectedCandidate.sub_scores.skills_score,
        experience_score: selectedCandidate.sub_scores.experience_score,
        education_score: selectedCandidate.sub_scores.education_score,
        cultural_fit_score: selectedCandidate.sub_scores.cultural_fit_score,
        achievements_score: selectedCandidate.sub_scores.achievements_score
      });
    }
  };

  // Table columns configuration
  const columns = [
    {
      title: 'Rank',
      key: 'rank',
      width: 70,
      render: (text, record, index) => (
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
        >
          <Tag color={index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : 'blue'}>
            #{(pagination.current - 1) * pagination.pageSize + index + 1}
          </Tag>
        </motion.div>
      )
    },
    {
      title: 'Candidate ID',
      dataIndex: 'candidate_id',
      key: 'candidate_id',
      width: 150,
      render: (text) => (
        <Text strong style={{ color: '#000080' }}>{text}</Text>
      )
    },
    {
      title: 'Overall Score',
      dataIndex: 'overall_score',
      key: 'overall_score',
      width: 150,
      sorter: true,
      render: (score) => (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Tag 
            color={score >= 8 ? 'green' : score >= 6 ? 'blue' : 'orange'}
            style={{ fontSize: '16px', fontWeight: 'bold', padding: '4px 12px' }}
          >
            {score.toFixed(2)} / 10
          </Tag>
        </motion.div>
      )
    },
    {
      title: 'Sub-Scores',
      key: 'sub_scores',
      render: (text, record) => (
        <Space direction="vertical" size="small">
          <Tooltip title={`Skills: ${record.sub_scores.skills_score}/10`}>
            <Tag color="blue">Skills: {record.sub_scores.skills_score}</Tag>
          </Tooltip>
          <Tooltip title={`Experience: ${record.sub_scores.experience_score}/10`}>
            <Tag color="green">Experience: {record.sub_scores.experience_score}</Tag>
          </Tooltip>
          <Tooltip title={`Education: ${record.sub_scores.education_score}/10`}>
            <Tag color="purple">Education: {record.sub_scores.education_score}</Tag>
          </Tooltip>
          <Tooltip title={`Cultural Fit: ${record.sub_scores.cultural_fit_score}/10`}>
            <Tag color="orange">Cultural Fit: {record.sub_scores.cultural_fit_score}</Tag>
          </Tooltip>
          <Tooltip title={`Achievements: ${record.sub_scores.achievements_score}/10`}>
            <Tag color="cyan">Achievements: {record.sub_scores.achievements_score}</Tag>
          </Tooltip>
        </Space>
      )
    },
    {
      title: 'Justification',
      dataIndex: 'justification',
      key: 'justification',
      width: 200,
      render: (text) => (
        <Tooltip title={text}>
          <Paragraph 
            ellipsis={{ rows: 2, expandable: false }} 
            style={{ margin: 0, maxWidth: '200px' }}
          >
            {text}
          </Paragraph>
        </Tooltip>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (text, record) => (
        <Space>
          <Button 
            type="primary" 
            size="small"
            icon={<ExperimentOutlined />}
            onClick={() => openWhatIfSimulator(record)}
          >
            What-If
          </Button>
        </Space>
      )
    }
  ];

  // Expanded row render - show radar chart and feedback
  const expandedRowRender = (record) => {
    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.3 }}
        className="expanded-row"
      >
        <Row gutter={24}>
          <Col span={12}>
            <Card title="Score Breakdown" size="small" className="radar-card">
              <ScoreRadar 
                subScores={record.sub_scores}
                candidateId={record.candidate_id}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Detailed Feedback" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong style={{ color: '#000080' }}>Strengths:</Text>
                  <Paragraph>{record.feedback || 'Excellent match for the position with strong technical skills and relevant experience.'}</Paragraph>
                </div>
                <div>
                  <Text strong style={{ color: '#000080' }}>Justification:</Text>
                  <Paragraph>{record.justification}</Paragraph>
                </div>
                <div>
                  <Text strong style={{ color: '#000080' }}>Resume ID:</Text>
                  <Text code>{record.resume_id}</Text>
                </div>
                <div>
                  <Text strong style={{ color: '#000080' }}>Match ID:</Text>
                  <Text code>{record.match_id}</Text>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </motion.div>
    );
  };

  return (
    <div className="dashboard-container">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Title level={2} style={{ color: '#000080', textAlign: 'center', marginBottom: '30px' }}>
          <TrophyOutlined /> Candidate Shortlist Dashboard
        </Title>
      </motion.div>

      {/* Statistics Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card className="stat-card">
              <Statistic 
                title="Total Candidates" 
                value={stats.total} 
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#000080' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card className="stat-card">
              <Statistic 
                title="Average Score" 
                value={stats.avgScore.toFixed(2)} 
                suffix="/ 10"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card className="stat-card">
              <Statistic 
                title="Top Score" 
                value={stats.topScore.toFixed(2)} 
                suffix="/ 10"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card className="stat-card">
              <Statistic 
                title="Above Threshold" 
                value={stats.aboveThreshold} 
                suffix={`/ ${stats.total}`}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Filters and Actions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Card className="filter-card">
          <Space size="large" wrap>
            <div>
              <Text strong style={{ color: '#000080', marginRight: '8px' }}>Threshold:</Text>
              <Select
                value={threshold}
                onChange={setThreshold}
                style={{ width: 120 }}
              >
                <Option value={0}>All (0+)</Option>
                <Option value={5}>Good (5+)</Option>
                <Option value={6}>Very Good (6+)</Option>
                <Option value={7}>Excellent (7+)</Option>
                <Option value={8}>Outstanding (8+)</Option>
                <Option value={9}>Exceptional (9+)</Option>
              </Select>
            </div>
            
            <Input
              placeholder="Search Candidate ID..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 250 }}
              allowClear
            />
            
            <Button 
              icon={<ReloadOutlined />}
              onClick={() => fetchShortlist(pagination.current, pagination.pageSize)}
            >
              Refresh
            </Button>
            
            <Button 
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              Export CSV
            </Button>
            
            <Button onClick={() => navigate('/upload')}>
              Upload More
            </Button>
          </Space>
        </Card>
      </motion.div>

      {/* Shortlist Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card className="table-card">
          <Spin spinning={loading} size="large">
            <Table
              columns={columns}
              dataSource={filteredCandidates}
              rowKey="candidate_id"
              pagination={pagination}
              onChange={handleTableChange}
              expandable={{
                expandedRowRender,
                expandRowByClick: false
              }}
              scroll={{ x: 1200 }}
              className="shortlist-table"
            />
          </Spin>
        </Card>
      </motion.div>

      {/* What-If Simulator Modal */}
      <Modal
        title={
          <Space>
            <ExperimentOutlined style={{ color: '#000080' }} />
            <Text strong style={{ color: '#000080' }}>What-If Simulator</Text>
          </Space>
        }
        open={whatIfModal}
        onCancel={() => setWhatIfModal(false)}
        width={800}
        footer={[
          <Button key="reset" onClick={resetSimulator}>
            Reset
          </Button>,
          <Button key="close" type="primary" onClick={() => setWhatIfModal(false)}>
            Close
          </Button>
        ]}
      >
        {selectedCandidate && simulatedScores && (
          <div className="simulator-content">
            <Paragraph style={{ marginBottom: '20px' }}>
              Adjust the sub-scores to see how they affect the overall score. This is a simulation and won't affect the actual candidate data.
            </Paragraph>
            
            <Row gutter={16}>
              <Col span={12}>
                <Card title="Adjust Scores" size="small">
                  <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div>
                      <Text strong>Skills Score:</Text>
                      <InputNumber
                        min={0}
                        max={10}
                        step={0.1}
                        value={simulatedScores.skills_score}
                        onChange={(val) => setSimulatedScores({...simulatedScores, skills_score: val})}
                        style={{ width: '100%', marginTop: '8px' }}
                      />
                    </div>
                    <div>
                      <Text strong>Experience Score:</Text>
                      <InputNumber
                        min={0}
                        max={10}
                        step={0.1}
                        value={simulatedScores.experience_score}
                        onChange={(val) => setSimulatedScores({...simulatedScores, experience_score: val})}
                        style={{ width: '100%', marginTop: '8px' }}
                      />
                    </div>
                    <div>
                      <Text strong>Education Score:</Text>
                      <InputNumber
                        min={0}
                        max={10}
                        step={0.1}
                        value={simulatedScores.education_score}
                        onChange={(val) => setSimulatedScores({...simulatedScores, education_score: val})}
                        style={{ width: '100%', marginTop: '8px' }}
                      />
                    </div>
                    <div>
                      <Text strong>Cultural Fit Score:</Text>
                      <InputNumber
                        min={0}
                        max={10}
                        step={0.1}
                        value={simulatedScores.cultural_fit_score}
                        onChange={(val) => setSimulatedScores({...simulatedScores, cultural_fit_score: val})}
                        style={{ width: '100%', marginTop: '8px' }}
                      />
                    </div>
                    <div>
                      <Text strong>Achievements Score:</Text>
                      <InputNumber
                        min={0}
                        max={10}
                        step={0.1}
                        value={simulatedScores.achievements_score}
                        onChange={(val) => setSimulatedScores({...simulatedScores, achievements_score: val})}
                        style={{ width: '100%', marginTop: '8px' }}
                      />
                    </div>
                    
                    <Card style={{ backgroundColor: '#f0f8ff', marginTop: '16px' }}>
                      <Statistic
                        title="Simulated Overall Score"
                        value={calculateSimulatedOverall(simulatedScores)}
                        suffix="/ 10"
                        valueStyle={{ color: '#000080', fontSize: '32px' }}
                      />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Original: {selectedCandidate.overall_score.toFixed(2)} / 10
                      </Text>
                    </Card>
                  </Space>
                </Card>
              </Col>
              
              <Col span={12}>
                <Card title="Simulated Radar Chart" size="small">
                  <ScoreRadar 
                    subScores={{
                      skills_score: simulatedScores.skills_score,
                      experience_score: simulatedScores.experience_score,
                      education_score: simulatedScores.education_score,
                      cultural_fit_score: simulatedScores.cultural_fit_score,
                      achievements_score: simulatedScores.achievements_score
                    }}
                    candidateId={`${selectedCandidate.candidate_id} (Simulated)`}
                  />
                </Card>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Dashboard;
