import { ChartJSNodeCanvas } from 'chartjs-node-canvas';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function renderCharts(dataPath, outDir) {
  console.log('Starting chart rendering...');
  console.log('Data path:', dataPath);
  console.log('Output directory:', outDir);
  
  try {
    const width = 600;
    const height = 400;
    console.log('Creating ChartJSNodeCanvas...');
    const canvas = new ChartJSNodeCanvas({
      width,
      height,
      chartCallback: (Chart) => {
        Chart.defaults.font.size = 14;
        Chart.defaults.font.family = 'NanumSquareRound Regular, NanumSquareRound Bold, Arial, sans-serif';
        Chart.register(ChartDataLabels);
      }
    });
    console.log('ChartJSNodeCanvas created successfully');
    
    console.log('Reading data file...');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log('Data loaded successfully');
    console.log('Data keys:', Object.keys(data));
    
    const name = data.name || 'Your';
    console.log('Creating output directory...');
    fs.mkdirSync(outDir, { recursive: true });
    console.log('Output directory created/verified');

    console.log('Rendering big5 chart...');
    const big5Codes = ['E','A','C','N','O'];
    const big5Labels = ['외향성','친화성','성실성','신경성','개방성'];
    const big5Scores = big5Codes.map(k => data.big5[k]);
    const big5Norm = big5Codes.map(k => (data.big5_norm || {})[k]);
    console.log('Big5 scores:', big5Scores);
    console.log('Big5 norms:', big5Norm);
    
    let config = {
      type: 'radar',
      data: {
        labels: big5Labels,
        datasets: [
          {
            label: `${name}님의 점수`,
            data: big5Scores,
            backgroundColor: 'rgba(54, 162, 235, 0.3)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 2
          },
          {
            label: '평균값',
            data: big5Norm,
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 2
          }
        ]
      },
      options: { scales: { r: { beginAtZero: true, max: 100 } } }
    };
    console.log('Rendering big5 to buffer...');
    let buffer = await canvas.renderToBuffer(config);
    console.log('Big5 buffer created, size:', buffer.length);
    const big5Path = path.join(outDir, 'big5.png');
    fs.writeFileSync(big5Path, buffer);
    console.log('Big5 chart saved to:', big5Path);

    console.log('Rendering riasec chart...');
    const riasecCodes = ['R','I','A','S','E','C'];
    const riasecLabels = ['현실형','탐구형','예술형','사회형','기업형','관습형'];
    const riasecScores = riasecCodes.map(k => data.riasec[k]);
    const riasecNorm = riasecCodes.map(k => (data.riasec_norm || {})[k]);
    console.log('RIASEC scores:', riasecScores);
    console.log('RIASEC norms:', riasecNorm);
    
    config = {
      type: 'bar',
      data: {
        labels: riasecLabels,
        datasets: [
          {
            label: `${name}님의 점수`,
            data: riasecScores,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 1,
            borderRadius: 10
          },
          {
            label: '평균값',
            data: riasecNorm,
            backgroundColor: 'rgba(255, 99, 132, 0.4)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 1,
            borderRadius: 10
          }
        ]
      },
      options: { scales: { y: { beginAtZero: true, max: 100 } } }
    };
    console.log('Rendering riasec to buffer...');
    buffer = await canvas.renderToBuffer(config);
    console.log('RIASEC buffer created, size:', buffer.length);
    const riasecPath = path.join(outDir, 'riasec.png');
    fs.writeFileSync(riasecPath, buffer);
    console.log('RIASEC chart saved to:', riasecPath);

    console.log('Rendering values chart...');
    const valuesCodes = ['A','I','Rec','Rel','S','W'];
    const valuesLabels = ['능력발휘','자율성','보상','안정성','사회적 인정','워라밸'];
    const valuesScores = valuesCodes.map(k => data.values[k]);
    const valuesNorm = valuesCodes.map(k => (data.values_norm || {})[k]);
    console.log('Values scores:', valuesScores);
    console.log('Values norms:', valuesNorm);
    
    config = {
      type: 'radar',
      data: {
        labels: valuesLabels,
        datasets: [
          {
            label: `${name}님의 점수`,
            data: valuesScores,
            backgroundColor: 'rgba(54, 162, 235, 0.3)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 2
          },
          {
            label: '평균값',
            data: valuesNorm,
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 2
          }
        ]
      },
      options: { scales: { r: { beginAtZero: true, max: 100 } } }
    };
    console.log('Rendering values to buffer...');
    buffer = await canvas.renderToBuffer(config);
    console.log('Values buffer created, size:', buffer.length);
    const valuesPath = path.join(outDir, 'values.png');
    fs.writeFileSync(valuesPath, buffer);
    console.log('Values chart saved to:', valuesPath);

    console.log('Rendering AI chart...');
    const aiCodes = ['EU','TS','CE','AO','SE','CB','ER'];
    const aiLabels = ['AI 이해','프롬프트','검증','도구 적용','학습','협업','윤리'];
    const aiScores = aiCodes.map(k => data.ai[k]);
    const aiColors = [
      'rgba(255, 99, 132, 0.6)',  // EU
      'rgba(255, 159, 64, 0.6)',  // TS
      'rgba(255, 205, 86, 0.6)',  // CE
      'rgba(75, 192, 192, 0.6)',  // AO
      'rgba(54, 162, 235, 0.6)',  // SE
      'rgba(153, 102, 255, 0.6)', // CB
      'rgba(201, 203, 207, 0.6)'  // ER
    ];
    console.log('AI scores:', aiScores);
    
    config = {
      type: 'polarArea',
      data: {
        labels: aiLabels,
        datasets: [{ data: aiScores, backgroundColor: aiColors }]
      },
      options: {
        scales: { r: { beginAtZero: true, max: 100 } },
        plugins: {
          datalabels: { color: '#000', anchor: 'center', align: 'center' }
        }
      }
    };
    console.log('Rendering AI to buffer...');
    buffer = await canvas.renderToBuffer(config);
    console.log('AI buffer created, size:', buffer.length);
    const aiPath = path.join(outDir, 'ai.png');
    fs.writeFileSync(aiPath, buffer);
    console.log('AI chart saved to:', aiPath);

    console.log('Rendering soft chart...');
    const softLabels = data.soft.map(t => t.name);
    const softScores = data.soft.map(t => t.score);
    console.log('Soft labels:', softLabels);
    console.log('Soft scores:', softScores);
    
    config = {
      type: 'radar',
      data: {
        labels: softLabels,
        datasets: [{ label: 'Score', data: softScores, backgroundColor: 'rgba(54, 162, 235, 0.3)', borderColor: 'rgb(54, 162, 235)', borderWidth: 2 }]
      },
      options: { scales: { r: { beginAtZero: true, max: 100 } } }
    };
    console.log('Rendering soft to buffer...');
    buffer = await canvas.renderToBuffer(config);
    console.log('Soft buffer created, size:', buffer.length);
    const softPath = path.join(outDir, 'soft.png');
    fs.writeFileSync(softPath, buffer);
    console.log('Soft chart saved to:', softPath);
    
    console.log('All charts rendered successfully!');
  } catch (error) {
    console.error('Error in renderCharts:', error);
    throw error;
  }
}

if (process.argv.length >= 4) {
  const [dataPath, outDir] = process.argv.slice(2);
  console.log('Script started with arguments:', { dataPath, outDir });
  renderCharts(dataPath, outDir)
    .then(() => { console.log('Chart rendering complete'); })
    .catch(err => { console.error('Chart rendering error:', err); process.exit(1); });
}
