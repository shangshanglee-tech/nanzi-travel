(function () {
  "use strict";

  function enableReplacement(button) {
    var root = button.closest('[data-deck-plan-upload="true"]');
    if (!root) return;
    var preview = root.querySelector('[data-deck-plan-preview="true"]');
    var replacement = root.querySelector('[data-deck-plan-replacement="true"]');
    if (preview) preview.hidden = true;
    if (replacement) replacement.hidden = false;
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest('[data-deck-plan-delete="true"]');
    if (button) {
      enableReplacement(button);
      return;
    }
    var rowDeleteButton = event.target.closest('[data-deck-plan-row-delete="true"]');
    if (!rowDeleteButton) return;
    var row = rowDeleteButton.closest(".inline-related");
    var checkbox = row && row.querySelector('input[type="checkbox"][name$="-DELETE"]');
    if (!row || !checkbox) return;
    checkbox.checked = true;
    row.dataset.pendingDelete = "true";
    row.classList.add("is-pending-delete");
  });
}());
