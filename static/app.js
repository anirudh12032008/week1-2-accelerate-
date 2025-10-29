        

let bgc = "#ffffff"
let threadc = "#000000"
let ball1c = "#ff0000"
let ball2c = "#0000ff"
let trailc = 0.1;
// let trailc = 0.1;





async function reset() {
    await fetch('/reset', { method: 'POST' });
}
async function start() {
    await fetch('/resume', { method: 'POST' });
}
async function stop() {
    await fetch('/pause', { method: 'POST' });
}




            document.getElementById('upt').addEventListener('click', async () => {
                const params = {
        length_rod_1: parseFloat(document.getElementById('length_rod_1').value),
        length_rod_2: parseFloat(document.getElementById('length_rod_2').value),
        mass_bob_1: parseFloat(document.getElementById('mass_1').value),    
        mass_bob_2: parseFloat(document.getElementById('mass_2').value),
        gravity: parseFloat(document.getElementById('gravity').value),
        theta_1: parseFloat(document.getElementById('theta_1').value),
        theta_2: parseFloat(document.getElementById('theta_2').value)
    };

    fetch('/update_params', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    });
});


const anglec = document.getElementById('angle').getContext('2d');
const velocityc = document.getElementById('velocity').getContext('2d');

const timeD = [];
const angle1D = []; 
const angle2D = [];
const velocity1D = [];
const velocity2D = [];
const kineticD = [];
const potentialD = [];
const totalD = [];


const angleChart = new Chart(anglec, {
    type: 'line',
    data: {
        labels: timeD,
        datasets: [
            {
                label: 'Theta 1',
                data: angle1D,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
            },  
            {
                label: 'Theta 2',
                data: angle2D,
                borderColor: 'rgba(153, 102, 255, 1)',
                fill: false,
            }   
        ],
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time (s)',
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Angle (radians)',
                },
            },
        },
    },
});

const velocityChart = new Chart(velocityc, {
    type: 'line',
    data: {     
        labels: timeD,
        datasets: [
            {
                label: 'Velocity 1',
                data: velocity1D,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
            },
            {
                label: 'Velocity 2',
                data: velocity2D,
                borderColor: 'rgba(153, 102, 255, 1)',
                fill: false,
            }
        ],
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time (s)',
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Velocity (m/s)',
                },
            },
        },
    },
});


const energyChart = new Chart(document.getElementById('energy').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Kinetic Energy (Total)',
        data: [],
        borderColor: 'rgb(34,197,94)', 
        borderWidth: 2,
        fill: false,
        tension: 0.15
      },
      {
        label: 'Potential Energy (Total)',
        data: [],
        borderColor: 'rgb(59,130,246)', 
        borderWidth: 2,
        fill: false,
        tension: 0.15
      },
      {
        label: 'Total Energy',
        data: [],
        borderColor: 'rgb(244,63,94)', 
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.15
      }
    ]
  },
  options: {
    animation: { duration: 0 },
    responsive: true,
    elements: { point: { radius: 0 } },
    scales: {
      x: { display: false },
      y: {
        beginAtZero: false,
        ticks: { color: '#333' },
        grid: { color: 'rgba(0,0,0,0.1)' }
      }
    },
    plugins: {
      legend: { labels: { color: '#333' } }
    }
  }
});
// AI used for this func to get good trails
function hexToRGBA(hex, alpha) {
    const bigint = parseInt(hex.slice(1), 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
// logic for charts ( trying to keep this front end only :prayge: )
let t = 0;
let frameCount = 0;

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const origin = { x: canvas.width / 2, y: 200 };

        async function update() {
            const res = await fetch('/coords');
            const data = await res.json();
            // ctx.clearRect(0, 0, canvas.width, canvas.height);
// ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
ctx.fillStyle = hexToRGBA(bgc, trailc);



ctx.fillRect(0, 0, canvas.width, canvas.height);
// ctx.strokeStyle = 'white';
            const x1 = origin.x + data.x1 * 100;
            const y1 = origin.y + data.y1 * 100;
            const x2 = origin.x + data.x2 * 100;
            const y2 = origin.y + data.y2 * 100;

            ctx.beginPath();
            ctx.moveTo(origin.x, origin.y);
            ctx.lineTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = threadc;
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.beginPath();
            ctx.fillStyle = ball1c;
            ctx.arc(x1, y1, 10, 0, Math.PI * 2);
            ctx.fill();
            

            ctx.beginPath();
            ctx.fillStyle = ball2c;

            ctx.arc(x2, y2, 10, 0, Math.PI * 2);
            ctx.fill();
            
            // Update charts only every 3 frames to improve performance
            frameCount++;
            if (frameCount % 3 === 0) {
                // charts
                // t += 0.02 ( this is looking too wierd)
                t = parseFloat((t+0.02).toFixed(2))
                timeD.push(t)
                angle1D.push(data.theta_1)
                angle2D.push(data.theta_2)
                velocity1D.push(data.omega_1)
                velocity2D.push(data.omega_2)
                kineticD.push(data.kinetic)
                potentialD.push(data.potential)
                totalD.push(data.energy)
                if (timeD.length>100){
                timeD.shift()
                angle1D.shift()
                angle2D.shift()
                velocity1D.shift()
                velocity2D.shift()
                kineticD.shift()
                potentialD.shift()
                totalD.shift()
                }
                angleChart.update('none')
                velocityChart.update('none')
                energyChart.data.labels = timeD;
                energyChart.data.datasets[0].data = kineticD;
                energyChart.data.datasets[1].data = potentialD;
                energyChart.data.datasets[2].data = totalD;

                energyChart.update('none')

            }

            requestAnimationFrame(update);
        }
        update();

