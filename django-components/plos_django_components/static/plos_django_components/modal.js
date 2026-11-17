// Run plos_modal invoker commands (`command` and `commandfor`) where the browser can't.
const nativeCommands = "command" in HTMLButtonElement.prototype;

document.addEventListener("click", (event) => {
  const button = event.target.closest("button[command][commandfor]");
  if (!button || button.disabled) return;
  if (nativeCommands) return;
  const dialog = document.getElementById(button.getAttribute("commandfor"));
  if (!(dialog instanceof HTMLDialogElement)) return;

  const command = button.getAttribute("command").toLowerCase();
  if (command === "show-modal") {
    event.preventDefault();
    if (!dialog.open) dialog.showModal();
  } else if (command === "close") {
    event.preventDefault();
    dialog.close();
  } else if (command === "request-close") {
    event.preventDefault();
    dialog.requestClose ? dialog.requestClose() : dialog.close();
  }
});

// The server renders each plos_modal as a <details> that expands inline,
// so it works without JS. This script converts it into a trigger <button>
// and a <dialog>, on page load and after each HTMX swap.
function upgradeModalTriggers(root) {
  const disclosures = root.matches?.("details[data-plos-modal]")
    ? [root]
    : root.querySelectorAll("details[data-plos-modal]");
  for (const details of disclosures) {
    const summary = details.querySelector(":scope > summary");
    const content = details.querySelector(":scope > .plos-modal");

    const button = document.createElement("button");
    button.type = "button";
    button.className = summary.className;
    button.setAttribute("command", "show-modal");
    button.setAttribute("commandfor", content.id);
    button.append(...summary.childNodes);

    const dialog = document.createElement("dialog");
    dialog.id = content.id;
    dialog.className = content.className;
    dialog.classList.remove("plos-modal--inline");
    if (content.hasAttribute("data-alert")) dialog.setAttribute("role", "alertdialog");
    dialog.setAttribute("aria-labelledby", `${content.id}-title`);
    if (content.hasAttribute("data-describe-body")) {
      dialog.setAttribute("aria-describedby", `${content.id}-description`);
    }
    content.querySelectorAll("[data-plos-modal-no-js]").forEach((element) => element.remove());
    document.getElementById(`${content.id}-cancel-no-js`)?.remove();
    dialog.append(...content.childNodes);
    dialog.querySelectorAll("template[data-plos-modal-js]").forEach((template) => template.replaceWith(template.content));

    details.replaceWith(button, dialog);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => upgradeModalTriggers(document));
} else {
  upgradeModalTriggers(document);
}
document.addEventListener("htmx:load", (event) => upgradeModalTriggers(event.detail.elt));
