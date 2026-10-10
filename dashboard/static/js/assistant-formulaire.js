// Formulaire en plusieurs étapes : navigation, validation de chaque étape,
// champs « ajouter un nouveau… » et récapitulatif avant l'envoi.
(function () {
  var formulaire = document.querySelector('form.assistant');
  if (!formulaire) {
    return;
  }

  var etapes = Array.prototype.slice.call(formulaire.querySelectorAll('.etape'));
  var indicateurs = Array.prototype.slice.call(document.querySelectorAll('.etapes li'));
  var courante = 0;

  function champsDe(etape) {
    return Array.prototype.slice.call(etape.querySelectorAll('input, select, textarea'));
  }

  function afficher(index, initial) {
    courante = index;
    etapes.forEach(function (etape, i) {
      etape.classList.toggle('active', i === index);
    });
    indicateurs.forEach(function (li, i) {
      li.classList.toggle('active', i === index);
      li.classList.toggle('terminee', i < index);
    });
    if (etapes[index].hasAttribute('data-recapitulatif')) {
      remplirRecapitulatif();
    }
    if (initial) {
      return;
    }
    var premier = champsDe(etapes[index]).filter(function (c) { return c.offsetParent !== null; })[0];
    if (premier) {
      premier.focus({ preventScroll: true });
    }
    formulaire.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function marquer(champ) {
    var valide = champ.checkValidity();
    champ.classList.toggle('is-invalid', !valide);
    var retour = champ.parentNode.querySelector('.invalid-feedback.js');
    if (!valide) {
      if (!retour) {
        retour = document.createElement('div');
        retour.className = 'invalid-feedback js';
        champ.parentNode.appendChild(retour);
      }
      retour.textContent = champ.validationMessage;
    } else if (retour) {
      retour.remove();
    }
    return valide;
  }

  function etapeValide(index) {
    var valide = true;
    champsDe(etapes[index]).forEach(function (champ) {
      if (champ.offsetParent !== null || champ.type === 'hidden') {
        valide = marquer(champ) && valide;
      }
    });
    return valide;
  }

  formulaire.addEventListener('click', function (evenement) {
    var bouton = evenement.target.closest('[data-etape]');
    if (!bouton) {
      return;
    }
    if (bouton.dataset.etape === 'suivante') {
      if (etapeValide(courante) && courante < etapes.length - 1) {
        afficher(courante + 1);
      }
    } else if (bouton.dataset.etape === 'precedente' && courante > 0) {
      afficher(courante - 1);
    }
  });

  // Revalider un champ dès qu'on le corrige
  formulaire.addEventListener('input', function (evenement) {
    if (evenement.target.classList.contains('is-invalid')) {
      marquer(evenement.target);
    }
  });

  // Option « + Ajouter un nouveau… » (valeur vide) : afficher et exiger le champ associé
  Array.prototype.slice.call(formulaire.querySelectorAll('select[data-nouveau]')).forEach(function (select) {
    var conteneur = document.getElementById(select.dataset.nouveau);
    function maj() {
      var visible = select.value === '';
      conteneur.classList.toggle('d-none', !visible);
      conteneur.querySelector('input').required = visible;
    }
    select.addEventListener('change', maj);
    maj();
  });

  function texteDe(nom) {
    var champ = formulaire.elements[nom];
    if (!champ) {
      return '';
    }
    if (champ.tagName === 'SELECT') {
      if (champ.value === '' && champ.dataset.nouveau) {
        var nouveau = document.getElementById(champ.dataset.nouveau).querySelector('input').value;
        return nouveau ? nouveau + ' (nouveau)' : '';
      }
      return champ.value === '' ? '' : champ.options[champ.selectedIndex].text;
    }
    if (champ.type === 'datetime-local' && champ.value) {
      var d = new Date(champ.value);
      return d.toLocaleDateString('fr-FR') + ' à ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    }
    return champ.value;
  }

  function remplirRecapitulatif() {
    Array.prototype.slice.call(formulaire.querySelectorAll('[data-recap]')).forEach(function (cible) {
      cible.textContent = texteDe(cible.dataset.recap) || '—';
    });
  }

  // Empêcher le double envoi et montrer que l'enregistrement est en cours
  formulaire.addEventListener('submit', function (evenement) {
    for (var i = 0; i < etapes.length; i++) {
      if (!etapeValide(i)) {
        evenement.preventDefault();
        afficher(i);
        return;
      }
    }
    var bouton = formulaire.querySelector('button[type="submit"]');
    bouton.disabled = true;
    bouton.innerHTML = '<span class="spinner-border spinner-border-sm mr-2"></span>Enregistrement…';
  });

  // Après une erreur côté serveur, ouvrir directement l'étape concernée
  var erreur = formulaire.querySelector('.is-invalid');
  var etapeErreur = erreur ? etapes.indexOf(erreur.closest('.etape')) : -1;
  afficher(etapeErreur >= 0 ? etapeErreur : 0, etapeErreur < 0);
})();
