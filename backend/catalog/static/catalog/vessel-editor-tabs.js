(function () {
  "use strict";

  function initVesselEditorTabs() {
    var root = document.querySelector("[data-vessel-editor-tabs]");
    if (!root) return;

    var buttons = Array.from(root.querySelectorAll("[data-vessel-tab]"));
    var panels = Array.from(document.querySelectorAll("[data-vessel-tab-panel]"));
    if (!buttons.length || !panels.length) return;

    function activate(tab) {
      buttons.forEach(function (button) {
        var active = button.dataset.vesselTab === tab;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.vesselTabPanel !== tab;
      });
      root.dataset.activeTab = tab;
    }

    function firstInvalidPanel() {
      return panels.find(function (panel) {
        return panel.querySelector(".errorlist, .errors, .errornote");
      });
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        activate(button.dataset.vesselTab);
      });
    });

    var invalidPanel = firstInvalidPanel();
    activate(invalidPanel ? invalidPanel.dataset.vesselTabPanel : "general");
  }

  document.addEventListener("DOMContentLoaded", initVesselEditorTabs);
})();
