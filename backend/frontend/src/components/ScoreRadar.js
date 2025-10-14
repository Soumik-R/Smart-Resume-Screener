import React, { useRef } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const ScoreRadar = ({ subScores, candidateId }) => {
  const chartRef = useRef(null);

  // Ensure subScores is defined with fallback values
  const safeSubScores = subScores || {
    skills_score: 0,
    experience_score: 0,
    education_score: 0,
    cultural_fit_score: 0,
    achievements_score: 0
  };

  // Prepare chart data
  const data = {
    labels: [
      'Skills',
      'Experience',
      'Education',
      'Cultural Fit',
      'Achievements'
    ],
    datasets: [
      {
        label: candidateId || 'Candidate Score',
        data: [
          safeSubScores.skills_score || 0,
          safeSubScores.experience_score || 0,
          safeSubScores.education_score || 0,
          safeSubScores.cultural_fit_score || 0,
          safeSubScores.achievements_score || 0
        ],
        backgroundColor: 'rgba(0, 0, 128, 0.2)', // Navy tint
        borderColor: 'rgba(0, 0, 128, 0.8)', // Navy border
        borderWidth: 2,
        pointBackgroundColor: 'rgba(0, 0, 128, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(0, 0, 128, 1)',
        pointRadius: 5,
        pointHoverRadius: 7
      }
    ]
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 10,
        ticks: {
          stepSize: 2,
          font: {
            size: 12
          },
          color: '#000080'
        },
        grid: {
          color: 'rgba(0, 0, 128, 0.1)'
        },
        angleLines: {
          color: 'rgba(0, 0, 128, 0.2)'
        },
        pointLabels: {
          font: {
            size: 13,
            weight: 'bold'
          },
          color: '#000080'
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          font: {
            size: 13,
            weight: 'bold'
          },
          color: '#000080',
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 128, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.r.toFixed(2)} / 10`;
          }
        }
      }
    },
    interaction: {
      mode: 'point',
      intersect: true
    },
    onClick: (event, activeElements) => {
      if (activeElements.length > 0) {
        const index = activeElements[0].index;
        const label = data.labels[index];
        const value = data.datasets[0].data[index];
        console.log(`Clicked on ${label}: ${value}`);
        
        // Highlight effect (optional - can add visual feedback)
        const chart = chartRef.current;
        if (chart) {
          chart.setActiveElements([{ datasetIndex: 0, index }]);
          chart.tooltip.setActiveElements([{ datasetIndex: 0, index }], { x: 0, y: 0 });
          chart.update();
        }
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart'
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', padding: '10px' }}>
      <Radar ref={chartRef} data={data} options={options} />
    </div>
  );
};

export default ScoreRadar;
