// Comportements communs à toutes les pages du tableau de bord
$(function () {
  // Sur petit écran, le menu latéral est masqué au départ (le bouton ☰ l'ouvre)
  if (window.innerWidth < 768) {
    $('body').addClass('sidebar-toggled');
    $('.sidebar').addClass('toggled');
  }

  // Les messages de succès disparaissent seuls ; les erreurs restent jusqu'à fermeture
  setTimeout(function () {
    $('.alert.alert-success, .alert.alert-info').alert('close');
  }, 6000);

  // Formulaires sensibles : <form data-confirmation="Texte de la question" data-confirmation-titre="Titre">
  var formulaireEnAttente = null;
  var $modale = $('#modaleConfirmation');

  $(document).on('submit', 'form[data-confirmation]', function (evenement) {
    if (this.dataset.confirme === 'oui') {
      return;
    }
    evenement.preventDefault();
    formulaireEnAttente = this;
    $modale.find('.modal-title').text(this.dataset.confirmationTitre || 'Confirmer');
    $modale.find('.modal-body').text(this.dataset.confirmation);
    $modale.modal('show');
  });

  $('#boutonConfirmer').on('click', function () {
    if (formulaireEnAttente) {
      formulaireEnAttente.dataset.confirme = 'oui';
      $(this).prop('disabled', true).html('<span class="spinner-border spinner-border-sm mr-2"></span>Envoi…');
      formulaireEnAttente.submit();
    }
  });

  $modale.on('hidden.bs.modal', function () {
    formulaireEnAttente = null;
  });
});
