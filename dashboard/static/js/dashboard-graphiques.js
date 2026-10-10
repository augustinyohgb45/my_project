// Graphiques du tableau de bord, alimentés par les données envoyées par la vue acceuil
Chart.defaults.global.defaultFontFamily = 'Nunito, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

var BLEU = '0, 85, 122';
var JAUNE = '255, 203, 5';

var infoBulle = {
  backgroundColor: 'rgb(255,255,255)',
  bodyFontColor: '#858796',
  titleMarginBottom: 10,
  titleFontColor: '#6e707e',
  titleFontSize: 14,
  borderColor: '#dddfeb',
  borderWidth: 1,
  xPadding: 15,
  yPadding: 15,
  displayColors: false,
  caretPadding: 10,
};

function lireDonnees(id) {
  return JSON.parse(document.getElementById(id).textContent);
}

function courbe(libelle, couleur, valeurs) {
  return {
    label: libelle,
    lineTension: 0.3,
    backgroundColor: 'rgba(' + couleur + ', 0.05)',
    borderColor: 'rgba(' + couleur + ', 1)',
    pointRadius: 3,
    pointBackgroundColor: 'rgba(' + couleur + ', 1)',
    pointBorderColor: 'rgba(' + couleur + ', 1)',
    pointHoverRadius: 3,
    pointHitRadius: 10,
    pointBorderWidth: 2,
    data: valeurs,
  };
}

var graphique = lireDonnees('donnees-graphique');

// Nombre d'incidents et de changements enregistrés par mois
new Chart(document.getElementById('myAreaChart'), {
  type: 'line',
  data: {
    labels: graphique.mois,
    datasets: [
      courbe('Incidents', BLEU, graphique.incidents),
      courbe('Changements', JAUNE, graphique.changements),
    ],
  },
  options: {
    maintainAspectRatio: false,
    layout: { padding: { left: 10, right: 25, top: 25, bottom: 0 } },
    scales: {
      xAxes: [{
        gridLines: { display: false, drawBorder: false },
        ticks: { maxTicksLimit: 7 },
      }],
      yAxes: [{
        ticks: { beginAtZero: true, precision: 0, maxTicksLimit: 5, padding: 10 },
        gridLines: {
          color: 'rgb(234, 236, 244)',
          zeroLineColor: 'rgb(234, 236, 244)',
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2],
        },
      }],
    },
    legend: { display: true },
    tooltips: Object.assign({ intersect: false, mode: 'index' }, infoBulle),
  },
});

// Répartition entre incidents et changements
new Chart(document.getElementById('myPieChart'), {
  type: 'doughnut',
  data: {
    labels: ['incident', 'changement'],
    datasets: [{
      data: [lireDonnees('total-incidents'), lireDonnees('total-changements')],
      backgroundColor: ['rgb(' + BLEU + ')', 'rgb(' + JAUNE + ')'],
      hoverBackgroundColor: ['#003049', '#e0b000'],
      hoverBorderColor: 'rgba(234, 236, 244, 1)',
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: infoBulle,
    legend: { display: false },
    cutoutPercentage: 80,
  },
});
