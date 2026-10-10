// Tableaux des listes d'incidents et de changements
$(document).ready(function () {
  var tableau = $('#dataTable').DataTable({
    order: [],  // garder l'ordre envoyé par le serveur (plus récents d'abord)
    pageLength: 10,
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'Tous']],
    columnDefs: [{ orderable: false, targets: -1 }],
    language: {
      url: '//cdn.datatables.net/plug-ins/1.10.24/i18n/French.json'
    }
  });

  // Filtres « Tous / En cours / Clôturés » sur la colonne Statut
  var colonneStatut = $('#dataTable thead th[data-colonne-statut]').index();
  $('.filtres-statut [data-filtre]').on('click', function () {
    $(this).addClass('active').siblings().removeClass('active');
    var filtre = $(this).data('filtre');
    tableau.column(colonneStatut).search(filtre ? '^\\s*' + filtre + '\\s*$' : '', true, false).draw();
  });
});
