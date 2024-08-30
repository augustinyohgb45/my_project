$(document).ready(function() {
  $('#dataTable').DataTable({
      "pageLength": 10,  // Nombre d'éléments par page
      "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Tous"]],
      "language": {
          "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/French.json"
      }
  });
});
