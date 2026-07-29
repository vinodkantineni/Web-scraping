import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function BiasChart({ original, debiased }) {
  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#f3f4f6',
          font: {
            family: 'Outfit',
            size: 13
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#9ca3af',
          font: {
            family: 'Outfit',
            size: 12
          }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#9ca3af',
          font: {
            family: 'Outfit',
            size: 12
          }
        }
      }
    }
  };

  const data = {
    labels: ['Left Wing', 'Center', 'Right Wing'],
    datasets: [
      {
        label: 'Original Article',
        data: [
          original.left * 100,
          original.center * 100,
          original.right * 100
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.65)',  // Red
          'rgba(16, 185, 129, 0.65)', // Green
          'rgba(59, 130, 246, 0.65)'  // Blue
        ],
        borderColor: [
          '#ef4444',
          '#10b981',
          '#3b82f6'
        ],
        borderWidth: 1,
        borderRadius: 6
      },
      {
        label: 'Debiased (Neutral) Article',
        data: [
          debiased.left * 100,
          debiased.center * 100,
          debiased.right * 100
        ],
        backgroundColor: 'rgba(168, 85, 247, 0.5)', // Purple
        borderColor: '#a855f7',
        borderWidth: 1,
        borderRadius: 6
      }
    ]
  };

  return (
    <div style={{ height: '300px', width: '100%', position: 'relative' }}>
      <Bar options={options} data={data} />
    </div>
  );
}
