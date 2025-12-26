// 报告 DOCX 导出模块
// 使用 docx 库生成真正的 DOCX 文件，保持原有样式

(function(window) {
  'use strict';
  
  // 颜色定义（与原样式保持一致）
  const COLORS = {
    primary: '4F46E5',
    textMain: '0F172A',
    textSecondary: '64748B',
    textMuted: '94A3B8',
    bgSurface: 'FFFFFF',
    bgSubtle: 'F8FAFC',
    bgElement: 'F1F5F9',
    border: 'E2E8F0',
    success: '27AE60',
    warning: 'F39C12',
    danger: 'EF4444',
    info: '3B82F6'
  };
  
  // 字体定义
  const FONT_FAMILY = 'Microsoft YaHei';
  
  /**
   * 创建 KPI 单元格
   */
  function createKpiCell(value, label) {
    const { TableCell, Paragraph, TextRun, AlignmentType, BorderStyle, WidthType } = docx;
    
    return new TableCell({
      children: [
        new Paragraph({
          children: [
            new TextRun({
              text: value,
              font: FONT_FAMILY,
              size: 48,
              bold: true,
              color: COLORS.primary
            })
          ],
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 }
        }),
        new Paragraph({
          children: [
            new TextRun({
              text: label,
              font: FONT_FAMILY,
              size: 22,
              color: COLORS.textSecondary
            })
          ],
          alignment: AlignmentType.CENTER
        })
      ],
      shading: { fill: 'F8F9FA' },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 2, color: 'BDC3C7' },
        bottom: { style: BorderStyle.SINGLE, size: 2, color: 'BDC3C7' },
        left: { style: BorderStyle.SINGLE, size: 2, color: 'BDC3C7' },
        right: { style: BorderStyle.SINGLE, size: 2, color: 'BDC3C7' }
      },
      width: { size: 25, type: WidthType.PERCENTAGE }
    });
  }
  
  /**
   * 导出报告为 DOCX 格式
   * @param {Object} reportData - 报告数据
   * @param {Object} helpers - 辅助函数集合
   */
  async function exportReportToDocx(reportData, helpers) {
    const { formatDateRange, numberToChinese, numberToCircle, getStatusText, calculateTaskProgress, formatDate } = helpers;
    const { Document, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, HeadingLevel, convertInchesToTwip, Packer } = docx;
    
    const reportTypeNames = { weekly: '周报', monthly: '月报', yearly: '年报' };
    const completionRate = reportData.summary.totalTasks > 0 
      ? Math.round(reportData.summary.completedTasks / reportData.summary.totalTasks * 100) 
      : 0;
    
    const children = [];
    
    // ========== 标题部分 ==========
    children.push(
      new Paragraph({
        text: reportTypeNames[reportData.reportType],
        heading: HeadingLevel.HEADING_1,
        alignment: AlignmentType.CENTER,
        spacing: { after: 200, before: 0 }
      })
    );
    
    // 日期范围
    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: formatDateRange(reportData.startDate, reportData.endDate),
            font: FONT_FAMILY,
            size: 28,
            color: COLORS.textSecondary
          })
        ],
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 }
      })
    );
    
    // ========== 项目概览标题 ==========
    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: '项目概览',
            font: FONT_FAMILY,
            size: 32,
            bold: true,
            color: COLORS.textMain
          })
        ],
        spacing: { before: 200, after: 200 }
      })
    );
    
    // ========== KPI 表格 ==========
    const kpiTable = new Table({
      width: { size: 70, type: WidthType.PERCENTAGE },
      alignment: AlignmentType.CENTER,
      rows: [
        new TableRow({
          children: [
            createKpiCell(reportData.summary.totalProjects.toString(), '涉及项目'),
            createKpiCell(reportData.summary.totalTasks.toString(), '总任务数'),
            createKpiCell(reportData.summary.completedTasks.toString(), '已完成任务'),
            createKpiCell(`${completionRate}%`, '完成率')
          ]
        })
      ]
    });
    
    children.push(kpiTable);
    children.push(new Paragraph({ text: '', spacing: { after: 400 } }));
    
    // ========== 项目详情 ==========
    let projectIndex = 1;
    for (const pg of Object.values(reportData.projectGroups)) {
      // 项目标题
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `${numberToChinese(projectIndex)}、${pg.projectName}`,
              font: FONT_FAMILY,
              size: 32,
              bold: true,
              color: COLORS.textMain
            })
          ],
          spacing: { before: 300, after: 200 },
          shading: { fill: COLORS.bgSubtle }
        })
      );
      
      let firstLevelIndex = 1;
      
      // 对标签进行排序
      const sortedFirstLevels = Object.values(pg.labelHierarchy).sort((a, b) => {
        if (a.isOther && !b.isOther) return 1;
        if (!a.isOther && b.isOther) return -1;
        return 0;
      });
      
      // 第一级标签
      for (const firstLevel of sortedFirstLevels) {
        children.push(
          new Paragraph({
            children: [
              new TextRun({
                text: `  ${firstLevelIndex}. ${firstLevel.name}`,
                font: FONT_FAMILY,
                size: 28,
                bold: true,
                color: COLORS.textMain
              })
            ],
            spacing: { before: 200, after: 150 },
            shading: { fill: COLORS.bgSubtle },
            indent: { left: convertInchesToTwip(0.3) }
          })
        );
        
        let lastLevelIndex = 1;
        
        // 最后一级标签
        for (const lastLevel of Object.values(firstLevel.children)) {
          children.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `    (${lastLevelIndex}) ${lastLevel.name}`,
                  font: FONT_FAMILY,
                  size: 26,
                  bold: true,
                  color: COLORS.textMain
                })
              ],
              spacing: { before: 150, after: 100 },
              shading: { fill: COLORS.bgSubtle },
              indent: { left: convertInchesToTwip(0.6) }
            })
          );
          
          // 任务列表 - 使用表格实现对齐
          if (lastLevel.tasks.length > 0) {
            const taskRows = lastLevel.tasks.map((task, idx) => {
              const statusText = getStatusText(task.aggregatedStatus || task.status);
              const taskProgress = calculateTaskProgress(task);
              const progressColor = taskProgress >= 100 ? COLORS.success : (taskProgress >= 50 ? COLORS.warning : COLORS.textMuted);
              const statusColor = statusText === '已完成' ? COLORS.success : (statusText === '进行中' ? COLORS.warning : COLORS.textMuted);
              
              return new TableRow({
                children: [
                  // 序号列
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: numberToCircle(idx + 1),
                            font: FONT_FAMILY,
                            size: 22,
                            color: COLORS.textSecondary
                          })
                        ],
                        alignment: AlignmentType.CENTER
                      })
                    ],
                    width: { size: 5, type: WidthType.PERCENTAGE },
                    borders: {
                      top: { style: BorderStyle.NIL },
                      bottom: { style: BorderStyle.NIL },
                      left: { style: BorderStyle.NIL },
                      right: { style: BorderStyle.NIL }
                    }
                  }),
                  // 任务名称列
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: task.title || task.name || task.code || '未命名任务',
                            font: FONT_FAMILY,
                            size: 24,
                            color: COLORS.textMain
                          })
                        ]
                      })
                    ],
                    width: { size: 65, type: WidthType.PERCENTAGE },
                    borders: {
                      top: { style: BorderStyle.NIL },
                      bottom: { style: BorderStyle.NIL },
                      left: { style: BorderStyle.NIL },
                      right: { style: BorderStyle.NIL }
                    }
                  }),
                  // 进度列
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: `${taskProgress}%`,
                            font: FONT_FAMILY,
                            size: 22,
                            bold: true,
                            color: progressColor
                          })
                        ],
                        alignment: AlignmentType.RIGHT
                      })
                    ],
                    width: { size: 15, type: WidthType.PERCENTAGE },
                    borders: {
                      top: { style: BorderStyle.NIL },
                      bottom: { style: BorderStyle.NIL },
                      left: { style: BorderStyle.NIL },
                      right: { style: BorderStyle.NIL }
                    }
                  }),
                  // 状态列
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: statusText,
                            font: FONT_FAMILY,
                            size: 20,
                            color: statusColor
                          })
                        ],
                        alignment: AlignmentType.RIGHT
                      })
                    ],
                    width: { size: 15, type: WidthType.PERCENTAGE },
                    borders: {
                      top: { style: BorderStyle.NIL },
                      bottom: { style: BorderStyle.NIL },
                      left: { style: BorderStyle.NIL },
                      right: { style: BorderStyle.NIL }
                    }
                  })
                ]
              });
            });
            
            const taskTable = new Table({
              width: { size: 65, type: WidthType.PERCENTAGE },
              rows: taskRows,
              indent: { size: convertInchesToTwip(0.9), type: WidthType.DXA },
              borders: {
                top: { style: BorderStyle.NIL, size: 0 },
                bottom: { style: BorderStyle.NIL, size: 0 },
                left: { style: BorderStyle.NIL, size: 0 },
                right: { style: BorderStyle.NIL, size: 0 },
                insideHorizontal: { style: BorderStyle.NIL, size: 0 },
                insideVertical: { style: BorderStyle.NIL, size: 0 }
              }
            });
            
            children.push(taskTable);
            children.push(new Paragraph({ text: '', spacing: { after: 100 } }));
          }
          
          lastLevelIndex++;
        }
        
        firstLevelIndex++;
      }
      
      // ========== 非开发工作说明 ==========
      if (pg.nonDevWorks && pg.nonDevWorks.length > 0) {
        const otherWorks = pg.nonDevWorks.filter(w => w.work_type === 'other_work');
        const nextWeekPlans = pg.nonDevWorks.filter(w => w.work_type === 'next_week_plan');
        
        // 其他工作说明
        if (otherWorks.length > 0) {
          children.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `  ${firstLevelIndex}. 其他工作说明`,
                  font: FONT_FAMILY,
                  size: 28,
                  bold: true,
                  color: COLORS.textMain
                })
              ],
              spacing: { before: 200, after: 150 },
              shading: { fill: COLORS.bgSubtle },
              indent: { left: convertInchesToTwip(0.3) }
            })
          );
          
          otherWorks.forEach((work, idx) => {
            children.push(
              new Paragraph({
                children: [
                  new TextRun({
                    text: `    (${idx + 1}) ${work.title || '未命名工作'}`,
                    font: FONT_FAMILY,
                    size: 26,
                    bold: true,
                    color: COLORS.textMain
                  })
                ],
                spacing: { before: 150, after: 100 },
                indent: { left: convertInchesToTwip(0.6) }
              })
            );
            
            if (work.description) {
              children.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `      ${work.description}`,
                      font: FONT_FAMILY,
                      size: 24,
                      italics: true,
                      color: COLORS.textSecondary
                    })
                  ],
                  spacing: { after: 100 },
                  indent: { left: convertInchesToTwip(0.9) }
                })
              );
            }
          });
          
          firstLevelIndex++;
        }
        
        // 下周工作计划
        if (nextWeekPlans.length > 0) {
          children.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `  ${firstLevelIndex}. 下周工作计划`,
                  font: FONT_FAMILY,
                  size: 28,
                  bold: true,
                  color: COLORS.textMain
                })
              ],
              spacing: { before: 200, after: 150 },
              shading: { fill: COLORS.bgSubtle },
              indent: { left: convertInchesToTwip(0.3) }
            })
          );
          
          nextWeekPlans.forEach((work, idx) => {
            children.push(
              new Paragraph({
                children: [
                  new TextRun({
                    text: `    (${idx + 1}) ${work.title || '未命名计划'}`,
                    font: FONT_FAMILY,
                    size: 26,
                    bold: true,
                    color: COLORS.textMain
                  })
                ],
                spacing: { before: 150, after: 100 },
                indent: { left: convertInchesToTwip(0.6) }
              })
            );
            
            if (work.description) {
              children.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `      ${work.description}`,
                      font: FONT_FAMILY,
                      size: 24,
                      italics: true,
                      color: COLORS.textSecondary
                    })
                  ],
                  spacing: { after: 100 },
                  indent: { left: convertInchesToTwip(0.9) }
                })
              );
            }
          });
        }
      }
      
      projectIndex++;
    }
    
    // ========== 创建文档 ==========
    const doc = new Document({
      sections: [{
        properties: {
          page: {
            margin: {
              top: convertInchesToTwip(0.79),
              right: convertInchesToTwip(0.98),
              bottom: convertInchesToTwip(0.79),
              left: convertInchesToTwip(0.98)
            }
          }
        },
        children: children
      }],
      styles: {
        paragraphStyles: [
          {
            id: 'Heading1',
            name: 'Heading 1',
            basedOn: 'Normal',
            next: 'Normal',
            run: {
              font: FONT_FAMILY,
              size: 48,
              bold: true,
              color: COLORS.textMain
            },
            paragraph: {
              spacing: { after: 200, before: 0 }
            }
          }
        ]
      }
    });
    
    // 生成并下载
    const blob = await Packer.toBlob(doc);
    const fileName = `工作报告_${formatDate(new Date())}.docx`;
    saveAs(blob, fileName);
    
    return true;
  }
  
  // 导出到全局
  window.ReportDocxExporter = {
    exportReportToDocx: exportReportToDocx
  };
  
})(window);
