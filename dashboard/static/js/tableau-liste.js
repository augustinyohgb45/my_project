// Tableaux des listes d'incidents et de changements
$(document).ready(function() {
  $('#dataTable').DataTable({
    "order": [],  // garder l'ordre envoyé par le serveur (plus récents d'abord)
    "pageLength": 5,
    "lengthMenu": [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "Tous"]],
    "language": {
      "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/French.json"
    }
  });
});
