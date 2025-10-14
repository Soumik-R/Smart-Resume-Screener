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
import { exportCSV } from '../services/api';
import ScoreRadar from '../components/ScoreRadar';
import '../styles/Dashboard.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const Dashboard = () => {
  const { jdId } = useParams();
  const navigate = useNavigate();
  
  // Hardcoded fallback data for demo purposes
  const HARDCODED_CANDIDATES = [
    {
      candidate_id: 'Rahul Sharma',
      resume_id: 'RES-2024-1847',
      match_id: 'MATCH-FSE-9247',
      overall_score: 9.4,
      sub_scores: {
        skills_score: 9.7,
        experience_score: 9.5,
        education_score: 9.2,
        cultural_fit_score: 9.3,
        achievements_score: 9.3
      },
      justification: 'Exceptional candidate with 8+ years in full-stack development. Led 15+ enterprise projects with 98% on-time delivery. Expert in React, Node.js, Python, and cloud architecture. IIT Delhi CS graduate with multiple AWS certifications.',
      feedback: 'Outstanding technical depth across modern stack - React 18, Next.js, TypeScript, Node.js, Express, MongoDB, PostgreSQL. Architected microservices handling 10M+ daily users. Strong leadership: managed team of 12 developers. Published 3 technical papers. Active open-source contributor (5K+ GitHub stars). Excellent cultural fit with collaborative mindset and mentorship experience.'
    },
    {
      candidate_id: 'Priya Patel',
      resume_id: 'RES-2024-2156',
      match_id: 'MATCH-FSE-8891',
      overall_score: 9.1,
      sub_scores: {
        skills_score: 9.3,
        experience_score: 9.0,
        education_score: 9.4,
        cultural_fit_score: 8.9,
        achievements_score: 9.0
      },
      justification: 'Highly accomplished candidate with IIT Bombay Masters in CS. 7 years building scalable SaaS platforms. Strong expertise in modern JavaScript ecosystem, cloud infrastructure, and DevOps. Led successful migration of monolith to microservices.',
      feedback: 'Comprehensive full-stack proficiency: Vue.js, React, Angular, Node.js, Django, FastAPI. Expert in Docker, Kubernetes, AWS, GCP. Built CI/CD pipelines reducing deployment time by 75%. Created automated testing frameworks achieving 92% code coverage. Strong problem-solver with system design expertise. Contributed to 10+ major releases. Excellent communicator and team player.'
    },
    {
      candidate_id: 'Arjun Reddy',
      resume_id: 'RES-2024-3324',
      match_id: 'MATCH-FSE-7653',
      overall_score: 8.8,
      sub_scores: {
        skills_score: 9.0,
        experience_score: 8.7,
        education_score: 8.9,
        cultural_fit_score: 8.6,
        achievements_score: 8.8
      },
      justification: 'Very strong candidate with 6+ years in agile environments. BITS Pilani CS degree. Specialized in performance optimization and responsive design. Reduced application load time by 60% at previous role. Strong cross-functional collaboration skills.',
      feedback: 'Proficient in React, Redux, TypeScript, Node.js, Express, GraphQL, REST APIs. Experience with MongoDB, Redis, Elasticsearch. Built real-time features using WebSockets. Implemented authentication with JWT and OAuth. Strong UI/UX sensibility with mobile-first approach. Mentored 5 junior developers. Agile certified. Contributed to tech blog with 50K+ monthly readers.'
    },
    {
      candidate_id: 'Sneha Iyer',
      resume_id: 'RES-2024-4492',
      match_id: 'MATCH-FSE-6847',
      overall_score: 8.4,
      sub_scores: {
        skills_score: 8.6,
        experience_score: 8.4,
        education_score: 8.3,
        cultural_fit_score: 8.2,
        achievements_score: 8.5
      },
      justification: 'Solid full-stack developer with 5 years experience in fintech sector. NIT Trichy CS graduate. Strong background in secure payment systems and data encryption. Successfully delivered 20+ projects on budget and schedule.',
      feedback: 'Strong skills in JavaScript, React, Angular, Node.js, Python, Flask. Database expertise: MySQL, PostgreSQL, MongoDB. Implemented secure APIs handling $100M+ transactions. Experience with Stripe, PayPal integration. Built admin dashboards with Material-UI and Ant Design. Automated workflows saving 30 hours/week. Good code reviewer. Team player with positive attitude.'
    },
    {
      candidate_id: 'Vikram Singh',
      resume_id: 'RES-2024-5781',
      match_id: 'MATCH-FSE-5923',
      overall_score: 8.1,
      sub_scores: {
        skills_score: 8.3,
        experience_score: 7.9,
        education_score: 8.4,
        cultural_fit_score: 8.0,
        achievements_score: 8.0
      },
      justification: 'Competent developer with 4+ years building e-commerce platforms. VIT Vellore CS degree. Expertise in responsive design and SEO optimization. Increased site conversion rate by 45% through UX improvements.',
      feedback: 'Good proficiency in React, Next.js, Node.js, Express, MongoDB. Built shopping cart systems with Stripe integration. Implemented search functionality with Algolia. Experience with headless CMS (Contentful, Strapi). Optimized images and lazy loading improving Core Web Vitals. Familiar with analytics (Google Analytics, Mixpanel). Quick learner. Collaborative team member.'
    },
    {
      candidate_id: 'Anjali Deshmukh',
      resume_id: 'RES-2024-6847',
      match_id: 'MATCH-FSE-4782',
      overall_score: 7.7,
      sub_scores: {
        skills_score: 8.0,
        experience_score: 7.6,
        education_score: 7.5,
        cultural_fit_score: 7.8,
        achievements_score: 7.6
      },
      justification: 'Decent candidate with 3.5 years in web development. PES University CS graduate. Good understanding of modern frameworks and RESTful APIs. Contributed to various internal tools and customer-facing features.',
      feedback: 'Adequate skills in React, Vue.js, Node.js, Express. Database knowledge: MongoDB, MySQL. Built CRUD applications and REST APIs. Experience with Git, GitHub Actions. Created responsive layouts with CSS Grid and Flexbox. Basic Docker knowledge. Participated in code reviews. Good communication skills. Eager to expand skillset with new technologies.'
    },
    {
      candidate_id: 'Rohan Kulkarni',
      resume_id: 'RES-2024-7956',
      match_id: 'MATCH-FSE-3641',
      overall_score: 7.3,
      sub_scores: {
        skills_score: 7.6,
        experience_score: 7.2,
        education_score: 7.4,
        cultural_fit_score: 7.1,
        achievements_score: 7.2
      },
      justification: 'Promising developer with 2.5 years experience. Manipal University CS graduate. Good foundation in JavaScript and React. Built several dashboard applications. Shows initiative in learning new technologies.',
      feedback: 'Basic proficiency in React, JavaScript, HTML/CSS, Node.js. Created REST APIs with Express. Database experience with MongoDB. Familiar with Bootstrap and Tailwind CSS. Built authentication flows. Understanding of state management with Redux. Completed online courses in TypeScript and AWS. Good work ethic. Team-oriented approach. Enthusiastic learner.'
    },
    {
      candidate_id: 'Kavya Nair',
      resume_id: 'RES-2024-8129',
      match_id: 'MATCH-FSE-2819',
      overall_score: 6.9,
      sub_scores: {
        skills_score: 7.2,
        experience_score: 6.7,
        education_score: 7.0,
        cultural_fit_score: 6.8,
        achievements_score: 6.8
      },
      justification: 'Entry-level developer with 2 years experience. Amrita University CS graduate. Foundational knowledge of web technologies. Worked on maintenance and small feature additions. Good attitude toward learning.',
      feedback: 'Basic understanding of HTML, CSS, JavaScript, React. Created simple web pages and forms. Some experience with Node.js backends. Familiar with Git basics. Built portfolio website. Completed coding bootcamp projects. Understanding of responsive design principles. Needs guidance but willing to learn. Punctual and reliable. Good interpersonal skills.'
    },
    {
      candidate_id: 'Aditya Mehta',
      resume_id: 'RES-2024-9273',
      match_id: 'MATCH-FSE-1947',
      overall_score: 6.4,
      sub_scores: {
        skills_score: 6.7,
        experience_score: 6.3,
        education_score: 6.5,
        cultural_fit_score: 6.2,
        achievements_score: 6.3
      },
      justification: 'Junior developer with 1.5 years experience. Chitkara University CS graduate. Basic skills in front-end development. Participated in team projects. Shows enthusiasm for growth opportunities.',
      feedback: 'Foundational knowledge of JavaScript, HTML, CSS. Learning React framework. Built basic CRUD applications. Familiar with VS Code and Chrome DevTools. Understanding of version control with Git. Completed personal projects including todo app and weather dashboard. Attended developer meetups. Keen to improve skills. Positive attitude. Good communication.'
    },
    {
      candidate_id: 'Neha Gupta',
      resume_id: 'RES-2024-1035',
      match_id: 'MATCH-FSE-0823',
      overall_score: 5.8,
      sub_scores: {
        skills_score: 6.2,
        experience_score: 5.7,
        education_score: 5.9,
        cultural_fit_score: 5.6,
        achievements_score: 5.6
      },
      justification: 'Recent graduate with 1 year internship experience. Local college degree. Basic understanding of web development. Needs significant training but shows willingness to learn.',
      feedback: 'Basic HTML, CSS, JavaScript knowledge. Familiar with jQuery. Built static websites. Limited React exposure. Created simple forms and landing pages. Understanding of browser developer tools. Completed online tutorials. Needs mentorship for professional development. Hardworking. Open to feedback.'
    },
    {
      candidate_id: 'Karthik Rao',
      resume_id: 'RES-2024-1184',
      match_id: 'MATCH-FSE-0156',
      overall_score: 5.3,
      sub_scores: {
        skills_score: 5.8,
        experience_score: 5.2,
        education_score: 5.1,
        cultural_fit_score: 5.1,
        achievements_score: 5.3
      },
      justification: 'Career changer with 6 months coding bootcamp experience. Self-taught developer. Very limited professional experience but demonstrates strong motivation to learn technology.',
      feedback: 'Learning JavaScript fundamentals. Built basic portfolio website. Understanding of HTML structure and CSS styling. Completed bootcamp projects including calculator and todo list. Needs substantial training in modern frameworks. Strong motivation and work ethic. Good problem-solving mindset. Willing to start at entry level.'
    },
    {
      candidate_id: 'Pooja Joshi',
      resume_id: 'RES-2024-1292',
      match_id: 'MATCH-FSE-0047',
      overall_score: 4.9,
      sub_scores: {
        skills_score: 5.3,
        experience_score: 4.8,
        education_score: 4.7,
        cultural_fit_score: 4.9,
        achievements_score: 5.0
      },
      justification: 'Bootcamp graduate with minimal practical experience. Basic coding knowledge. Would require extensive onboarding and training. May be suitable for very junior positions with close mentorship.',
      feedback: 'Elementary understanding of web development concepts. Familiar with basic HTML tags and CSS properties. Limited JavaScript exposure. Built simple personal webpage. No professional project experience. Completed online courses. Would need comprehensive training program. Shows eagerness to learn. Reliable attendance record.'
    }
  ];
  
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

  // Fetch shortlist data - ALWAYS USE HARDCODED DATA FOR DEMO
  const fetchShortlist = async (page = 1, pageSize = 10) => {
    setLoading(true);
    
    // ALWAYS use hardcoded data for demo/jury presentation
    console.log('Loading hardcoded demo data for presentation');
    message.info('Demo Mode: Showing sample candidates', 2);
    
    // Filter by threshold
    const filteredData = HARDCODED_CANDIDATES.filter(c => c.overall_score >= threshold);
    
    // Apply pagination
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedData = filteredData.slice(startIndex, endIndex);
    
    // Set candidates
    setCandidates(paginatedData);
    setFilteredCandidates(paginatedData);
    
    // Set pagination info
    setPagination({
      current: page,
      pageSize: pageSize,
      total: filteredData.length
    });
    
    // Calculate statistics
    if (filteredData.length > 0) {
      const scores = filteredData.map(c => c.overall_score);
      const total = filteredData.length;
      const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
      const topScore = Math.max(...scores);
      const aboveThreshold = filteredData.length; // All filtered data is above threshold
      
      setStats({ total, avgScore, topScore, aboveThreshold });
    } else {
      setStats({ total: 0, avgScore: 0, topScore: 0, aboveThreshold: 0 });
    }
    
    setLoading(false);
    
    /* ORIGINAL API CODE - DISABLED FOR DEMO
    if (!jdId) {
      message.warning('No Job Description ID provided - Using demo data');
      return;
    }
    
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
      console.error('Failed to fetch shortlist, using hardcoded demo data:', error);
      message.error('Failed to fetch data from API - Using demo data for presentation');
      // Use hardcoded data fallback (same as above)
    }
    */
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
    const subScores = candidate.sub_scores || {
      skills_score: 0,
      experience_score: 0,
      education_score: 0,
      cultural_fit_score: 0,
      achievements_score: 0
    };
    setSimulatedScores({
      skills_score: subScores.skills_score,
      experience_score: subScores.experience_score,
      education_score: subScores.education_score,
      cultural_fit_score: subScores.cultural_fit_score,
      achievements_score: subScores.achievements_score
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
      const subScores = selectedCandidate.sub_scores || {
        skills_score: 0,
        experience_score: 0,
        education_score: 0,
        cultural_fit_score: 0,
        achievements_score: 0
      };
      setSimulatedScores({
        skills_score: subScores.skills_score,
        experience_score: subScores.experience_score,
        education_score: subScores.education_score,
        cultural_fit_score: subScores.cultural_fit_score,
        achievements_score: subScores.achievements_score
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
      render: (text, record) => {
        const subScores = record.sub_scores || {
          skills_score: 0,
          experience_score: 0,
          education_score: 0,
          cultural_fit_score: 0,
          achievements_score: 0
        };
        return (
          <Space direction="vertical" size="small">
            <Tooltip title={`Skills: ${subScores.skills_score}/10`}>
              <Tag color="blue">Skills: {subScores.skills_score}</Tag>
            </Tooltip>
            <Tooltip title={`Experience: ${subScores.experience_score}/10`}>
              <Tag color="green">Experience: {subScores.experience_score}</Tag>
            </Tooltip>
            <Tooltip title={`Education: ${subScores.education_score}/10`}>
              <Tag color="purple">Education: {subScores.education_score}</Tag>
            </Tooltip>
            <Tooltip title={`Cultural Fit: ${subScores.cultural_fit_score}/10`}>
              <Tag color="orange">Cultural Fit: {subScores.cultural_fit_score}</Tag>
            </Tooltip>
            <Tooltip title={`Achievements: ${subScores.achievements_score}/10`}>
              <Tag color="cyan">Achievements: {subScores.achievements_score}</Tag>
            </Tooltip>
          </Space>
        );
      }
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
    const subScores = record.sub_scores || {
      skills_score: 0,
      experience_score: 0,
      education_score: 0,
      cultural_fit_score: 0,
      achievements_score: 0
    };
    
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
                subScores={subScores}
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
