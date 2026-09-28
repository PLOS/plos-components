// Post the collapsed item indexes with each plos_add_more add/delete so the server can
// keep those items collapsed after the swap (see logic.collapsed_after_add_or_delete).
document.addEventListener("htmx:configRequest", (event) => {
  const list = event.detail.elt.closest("[data-add-more]");
  if (!list) return;
  const sections = [...list.querySelectorAll(".govuk-accordion__section")];
  const collapsed = sections.flatMap((section, i) =>
    section.classList.contains("govuk-accordion__section--expanded") ? [] : [i]
  );
  event.detail.parameters[`${list.dataset.addMore}__collapsed`] = collapsed.join(",");
});
