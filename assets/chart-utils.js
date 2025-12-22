// Chart utilities for data visualization
// Simple chart rendering without external dependencies

class SimpleChart {
  constructor(container) {
    this.container = container;
  }

  // Render a simple bar chart
  renderBarChart(data, options = {}) {
    const { 
      title = '', 
      colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444'],
      height = 200,
      horizontal = false
    } = options;

    const maxValue = Math.max(...data.map(d => d.value));
    
    if (horizontal) {
      const html = `
        <div style="height: ${height}px; display: flex; flex-direction: column;">
          ${title ? `<h4 style="margin: 0 0 16px 0; font-size: 14px; color: var(--text-secondary);">${title}</h4>` : ''}
          <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; padding: 16px 0;">
            ${data.map((item, index) => {
              const barWidth = (item.value / maxValue) * 80; // 80% max width
              const color = colors[index % colors.length];
              return `
                <div style="display: flex; align-items: center; gap: 12px; margin: 4px 0;">
                  <div style="min-width: 60px; font-size: 11px; color: var(--text-secondary); text-align: right;">${item.label}</div>
                  <div style="flex: 1; display: flex; align-items: center; gap: 8px;">
                    <div style="
                      width: ${barWidth}%; 
                      height: 24px; 
                      background: linear-gradient(90deg, ${color} 0%, ${color}CC 100%);
                      border-radius: 4px;
                      transition: all 0.3s ease;
                      cursor: pointer;
                      position: relative;
                    " onmouseover="this.style.transform='scaleX(1.05)'" onmouseout="this.style.transform='scaleX(1)'">
                      <div style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 11px; font-weight: 600; color: white;">${item.value}</div>
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
      this.container.innerHTML = html;
      return;
    }
    
    const html = `
      <div style="height: ${height}px; display: flex; flex-direction: column;">
        ${title ? `<h4 style="margin: 0 0 16px 0; font-size: 14px; color: var(--text-secondary);">${title}</h4>` : ''}
        <div style="flex: 1; display: flex; align-items: end; gap: 8px; padding: 16px 0;">
          ${data.map((item, index) => {
            const barHeight = (item.value / maxValue) * (height - 80);
            const color = colors[index % colors.length];
            return `
              <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;">
                <div style="font-size: 12px; font-weight: 600; color: var(--text-main);">${item.value}</div>
                <div style="
                  width: 100%; 
                  height: ${barHeight}px; 
                  background: linear-gradient(180deg, ${color} 0%, ${color}CC 100%);
                  border-radius: 4px 4px 0 0;
                  transition: all 0.3s ease;
                  cursor: pointer;
                " onmouseover="this.style.transform='scaleY(1.05)'" onmouseout="this.style.transform='scaleY(1)'"></div>
                <div style="font-size: 11px; color: var(--text-secondary); text-align: center; word-break: break-all;">${item.label}</div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;

    this.container.innerHTML = html;
  }

  // Render a simple pie chart using CSS
  renderPieChart(data, options = {}) {
    const { 
      title = '', 
      colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444'],
      size = 200 
    } = options;

    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;

    const segments = data.map((item, index) => {
      const percentage = (item.value / total) * 100;
      const angle = (item.value / total) * 360;
      const startAngle = currentAngle;
      currentAngle += angle;
      
      return {
        ...item,
        percentage: percentage.toFixed(1),
        angle,
        startAngle,
        color: colors[index % colors.length]
      };
    });

    const html = `
      <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
        ${title ? `<h4 style="margin: 0; font-size: 14px; color: var(--text-secondary);">${title}</h4>` : ''}
        <div style="position: relative; width: ${size}px; height: ${size}px;">
          <div style="
            width: 100%; 
            height: 100%; 
            border-radius: 50%; 
            background: conic-gradient(${segments.map(s => `${s.color} ${s.startAngle}deg ${s.startAngle + s.angle}deg`).join(', ')});
            box-shadow: var(--shadow-md);
          "></div>
          <div style="
            position: absolute; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%);
            width: 60px; 
            height: 60px; 
            background: var(--bg-surface); 
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 700;
            color: var(--text-main);
            box-shadow: var(--shadow-sm);
          ">${total}</div>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;">
          ${segments.map(segment => `
            <div style="display: flex; align-items: center; gap: 6px;">
              <div style="width: 12px; height: 12px; background: ${segment.color}; border-radius: 2px;"></div>
              <span style="font-size: 12px; color: var(--text-secondary);">${segment.label} (${segment.percentage}%)</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    this.container.innerHTML = html;
  }

  // Render a simple line chart
  renderLineChart(data, options = {}) {
    const { 
      title = '', 
      color = '#4f46e5',
      height = 200,
      showPoints = true,
      padding = { top: 16, right: 16, bottom: 16, left: 16 }
    } = options;

    const maxValue = Math.max(...data.map(d => d.value));
    const minValue = Math.min(...data.map(d => d.value));
    const range = maxValue - minValue || 1;

    const points = data.map((item, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 100 - ((item.value - minValue) / range) * 100;
      return { x, y, ...item };
    });

    const pathData = points.map((point, index) => 
      `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
    ).join(' ');

    const html = `
      <div style="height: ${height}px; display: flex; flex-direction: column; overflow: hidden;">
        ${title ? `<h4 style="margin: 0 0 12px 0; font-size: 14px; color: var(--text-secondary);">${title}</h4>` : ''}
        <div style="flex: 1; position: relative; padding: ${padding.top}px ${padding.right}px 0px ${padding.left}px; overflow: hidden;">
          <svg width="100%" height="100%" viewBox="0 0 100 100" style="overflow: hidden;">
            <defs>
              <linearGradient id="lineGradient-${Date.now()}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:${color};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:${color};stop-opacity:0" />
              </linearGradient>
            </defs>
            <path d="${pathData} L 100 85 L 0 85 Z" fill="url(#lineGradient-${Date.now()})" />
            <path d="${pathData}" stroke="${color}" stroke-width="2" fill="none" />
            ${showPoints ? points.map(point => `
              <circle cx="${point.x}" cy="${point.y}" r="3" fill="${color}" stroke="white" stroke-width="2" />
            `).join('') : ''}
          </svg>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 8px ${padding.left}px 0 ${padding.right}px; font-size: 11px; color: var(--text-secondary); min-height: 20px;">
          ${data.map(item => `<span style="white-space: nowrap; text-align: center; flex: 1;">${item.label}</span>`).join('')}
        </div>
      </div>
    `;

    this.container.innerHTML = html;
  }

  // Render a progress ring
  renderProgressRing(percentage, options = {}) {
    const { 
      size = 120, 
      strokeWidth = 8, 
      color = '#4f46e5',
      backgroundColor = '#e5e7eb',
      label = '',
      showPercentage = true 
    } = options;

    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    const html = `
      <div style="display: flex; flex-direction: column; align-items: center; gap: 12px;">
        <div style="position: relative; width: ${size}px; height: ${size}px;">
          <svg width="${size}" height="${size}" style="transform: rotate(-90deg);">
            <circle
              cx="${size / 2}"
              cy="${size / 2}"
              r="${radius}"
              stroke="${backgroundColor}"
              stroke-width="${strokeWidth}"
              fill="transparent"
            />
            <circle
              cx="${size / 2}"
              cy="${size / 2}"
              r="${radius}"
              stroke="${color}"
              stroke-width="${strokeWidth}"
              fill="transparent"
              stroke-dasharray="${strokeDasharray}"
              stroke-dashoffset="${strokeDashoffset}"
              stroke-linecap="round"
              style="transition: stroke-dashoffset 0.8s ease;"
            />
          </svg>
          ${showPercentage ? `
            <div style="
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              font-size: 18px;
              font-weight: 700;
              color: var(--text-main);
            ">${Math.round(percentage)}%</div>
          ` : ''}
        </div>
        ${label ? `<div style="font-size: 14px; color: var(--text-secondary); text-align: center;">${label}</div>` : ''}
      </div>
    `;

    this.container.innerHTML = html;
  }
}

// Export for use in other scripts
window.SimpleChart = SimpleChart;