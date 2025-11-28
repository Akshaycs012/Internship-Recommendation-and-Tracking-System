import Chart from "https://cdn.jsdelivr.net/npm/chart.js";

// FUTURE: Replace static with real DB analytics
// data can come from progress table later

new Chart(document.getElementById("internChart"), {
  type: "bar",
  data: {
    labels:["Week 1","Week 2","Week 3","Week 4"],
    datasets:[{
      label: "Performance % (Demo)",
      data: [70, 75, 80, 90], // replace with backend data later
      borderWidth: 1
    }]
  },
  options:{
    responsive: true,
    plugins:{
      legend:{ display:true },
      title:{ display:false }
    },
    scales:{
      y:{ beginAtZero:true, max:100 }
    }
  }
});
