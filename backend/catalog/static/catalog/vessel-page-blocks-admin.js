(function () {
  "use strict";

  function blockRows() {
    return Array.from(document.querySelectorAll("#page_blocks-group .inline-related"));
  }

  function blockType(row) {
    const select = row.querySelector('select[name$="-block_type"]');
    return select ? select.value : "";
  }

  function fieldWrapper(row, name) {
    const field = row.querySelector(`[name$="-${name}"]`);
    if (!field) return null;
    return field.closest(".form-row") || field.parentElement;
  }

  function syncFieldsForType(row) {
    const isHeading = blockType(row) === "heading";
    [fieldWrapper(row, "image"), fieldWrapper(row, "body")].forEach(function (field) {
      if (field) field.style.display = isHeading ? "none" : "";
    });
  }

  function setToggle(heading, cards) {
    const headingTitle = heading.querySelector("h3");
    if (!headingTitle) return;
    const existing = headingTitle.querySelector("[data-page-composer-toggle]");
    if (!cards.length) {
      if (existing) existing.remove();
      return;
    }

    let button = existing;
    if (!button) {
      button = document.createElement("button");
      button.type = "button";
      button.dataset.pageComposerToggle = "true";
      button.style.marginLeft = "12px";
      button.style.cursor = "pointer";
      headingTitle.appendChild(button);
    }
    const collapsed = heading.dataset.pageComposerCollapsed === "true";
    button.textContent = collapsed ? `展开 ${cards.length} 项` : `收起 ${cards.length} 项`;
    cards.forEach(function (card) { card.style.display = collapsed ? "none" : ""; });
    button.onclick = function () {
      heading.dataset.pageComposerCollapsed = collapsed ? "false" : "true";
      refresh();
    };
  }

  function refresh() {
    const headings = [];
    let active = null;
    blockRows().forEach(function (row) {
      row.style.display = "";
      syncFieldsForType(row);
      if (blockType(row) === "heading") {
        active = {row: row, cards: []};
        headings.push(active);
      } else if (blockType(row) === "card" && active) {
        active.cards.push(row);
      }
    });
    headings.forEach(function (heading) { setToggle(heading.row, heading.cards); });
  }

  document.addEventListener("change", function (event) {
    if (event.target.matches('#page_blocks-group select[name$="-block_type"]')) refresh();
  });
  if (window.django && window.django.jQuery) {
    window.django.jQuery(document).on("formset:added", refresh);
  }
  document.addEventListener("DOMContentLoaded", refresh);
})();
