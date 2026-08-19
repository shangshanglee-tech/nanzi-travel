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
    if (!button) return;
    enableReplacement(button);
  });
}());
