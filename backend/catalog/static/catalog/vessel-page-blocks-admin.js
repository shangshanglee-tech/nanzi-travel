(function () {
  "use strict";

  function editor() { return document.querySelector("[data-page-block-editor]"); }
  function rows() {
    var root = editor();
    return root ? Array.from(root.querySelectorAll(".page-block-editor__rows .inline-related:not(.empty-form)")) : [];
  }
  function blockType(row) {
    var select = row.querySelector('select[name$="-block_type"]');
    return select ? select.value : "";
  }
  function blockTypeLabel(row) {
    var select = row.querySelector('select[name$="-block_type"]');
    return select && select.selectedOptions[0] ? select.selectedOptions[0].textContent.trim() : "未设置类型";
  }
  function blockTitle(row) {
    var input = row.querySelector('input[name$="-title"]');
    return input && input.value.trim() ? input.value.trim() : "未命名内容";
  }
  function fieldWrapper(row, name) {
    var field = row.querySelector('[name$="-' + name + '"]');
    return field ? field.closest(".form-row") || field.parentElement : null;
  }
  function syncFieldsForType(row) {
    var isHeading = blockType(row) === "heading";
    ["image", "additional_images", "existing_additional_images", "body"].forEach(function (name) {
      var field = fieldWrapper(row, name);
      if (field) field.style.display = isHeading ? "none" : "";
    });
  }
  function deletionControl(row) { return row.querySelector('input[type="checkbox"][name$="-DELETE"]'); }
  function markForDeletion(row) {
    var checkbox = deletionControl(row);
    if (checkbox) checkbox.checked = true;
    row.dataset.pendingDelete = "true";
    closeEditor(row);
    refresh();
  }
  function setAdditionalImageDeleteButtons() {
    document.querySelectorAll("[data-delete-image]").forEach(function (button) {
      if (button.dataset.deleteControlReady === "true") return;
      button.dataset.deleteControlReady = "true";
      button.addEventListener("click", function () {
        var item = button.closest("li");
        var checkbox = item && item.querySelector('input[type="checkbox"]');
        if (checkbox && item) { checkbox.checked = true; item.style.display = "none"; }
      });
    });
  }
  function backdrop() {
    var existing = document.querySelector("[data-page-block-backdrop]");
    if (existing) return existing;
    var element = document.createElement("div");
    element.className = "page-block-editor__backdrop";
    element.dataset.pageBlockBackdrop = "true";
    element.addEventListener("click", function () { closeEditor(); });
    document.body.appendChild(element);
    return element;
  }
  function closeEditor(target) {
    var active = target || document.querySelector(".page-block-editor__rows .inline-related.is-editing");
    if (active) active.classList.remove("is-editing");
    var overlay = document.querySelector("[data-page-block-backdrop]");
    if (overlay) overlay.classList.remove("is-visible");
  }
  function openEditor(row) {
    rows().forEach(function (item) { item.classList.remove("is-editing"); });
    row.classList.add("is-editing");
    backdrop().classList.add("is-visible");
    var close = row.querySelector("[data-page-block-close]");
    if (!close) {
      close = document.createElement("button");
      close.type = "button";
      close.textContent = "完成编辑";
      close.dataset.pageBlockClose = "true";
      close.addEventListener("click", function () { closeEditor(row); refresh(); });
      row.querySelector("h3").appendChild(close);
    }
    syncFieldsForType(row);
    row.scrollTop = 0;
  }
  function updateSortOrders() {
    rows().filter(function (row) { return row.dataset.pendingDelete !== "true"; }).forEach(function (row, index) {
      var input = row.querySelector('input[name$="-sort_order"]');
      if (input) input.value = index;
    });
  }
  function syncAllInlineSortOrders() {
    var form = document.querySelector("#vessel_form");
    if (!form) return;
    form.querySelectorAll(".inline-group").forEach(function (group) {
      Array.from(group.querySelectorAll(".inline-related:not(.empty-form)"))
        .filter(function (row) {
          var checkbox = deletionControl(row);
          return row.dataset.pendingDelete !== "true" && !(checkbox && checkbox.checked);
        })
        .forEach(function (row, index) {
          var input = row.querySelector('input[name$="-sort_order"]');
          if (input) input.value = index;
        });
    });
  }
  function moveBlock(row, direction) {
    var visible = rows().filter(function (item) { return item.dataset.pendingDelete !== "true"; });
    var index = visible.indexOf(row);
    var other = visible[index + direction];
    if (!other) return;
    var container = row.parentElement;
    if (direction < 0) container.insertBefore(row, other);
    else container.insertBefore(other, row);
    updateSortOrders();
    refresh();
  }
  function addAction(parent, label, callback, disabled) {
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.disabled = Boolean(disabled);
    button.addEventListener("click", callback);
    parent.appendChild(button);
  }
  function renderList() {
    var root = editor();
    if (!root) return;
    var list = root.querySelector("[data-page-block-list]");
    list.replaceChildren();
    rows().filter(function (row) { return row.dataset.pendingDelete !== "true"; }).forEach(function (row, index, visible) {
      var item = document.createElement("div");
      item.className = "page-block-editor__item";
      var type = document.createElement("span"); type.className = "page-block-editor__type"; type.textContent = blockTypeLabel(row);
      var name = document.createElement("strong"); name.className = "page-block-editor__name"; name.textContent = blockTitle(row);
      var actions = document.createElement("div"); actions.className = "page-block-editor__actions";
      addAction(actions, "上移", function () { moveBlock(row, -1); }, index === 0);
      addAction(actions, "下移", function () { moveBlock(row, 1); }, index === visible.length - 1);
      addAction(actions, "编辑", function () { openEditor(row); });
      addAction(actions, "删除", function () { markForDeletion(row); });
      item.append(type, name, actions);
      list.appendChild(item);
    });
  }
  function addBlock(type) {
    var root = editor();
    var addLink = root && root.querySelector(".add-row a");
    if (!addLink) return;
    addLink.click();
    window.setTimeout(function () {
      var available = rows();
      var row = available[available.length - 1];
      var select = row && row.querySelector('select[name$="-block_type"]');
      if (!row || !select) return;
      select.value = type;
      select.dispatchEvent(new Event("change", {bubbles: true}));
      updateSortOrders();
      refresh();
      openEditor(row);
    }, 0);
  }
  function refresh() {
    rows().forEach(function (row) { syncFieldsForType(row); });
    setAdditionalImageDeleteButtons();
    renderList();
  }
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-page-block-create]");
    if (button) addBlock(button.dataset.pageBlockCreate);
  });
  document.addEventListener("input", function (event) {
    if (event.target.matches('#page_blocks-group input[name$="-title"]')) renderList();
  });
  document.addEventListener("change", function (event) {
    if (event.target.matches('#page_blocks-group select[name$="-block_type"]')) refresh();
  });
  document.addEventListener("keydown", function (event) { if (event.key === "Escape") closeEditor(); });
  document.addEventListener("submit", syncAllInlineSortOrders);
  if (window.django && window.django.jQuery) window.django.jQuery(document).on("formset:added", refresh);
  document.addEventListener("DOMContentLoaded", function () {
    syncAllInlineSortOrders();
    refresh();
  });
})();
