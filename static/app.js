const panel = document.getElementById("panel");
const cells = document.querySelectorAll(".cell");
const mods = document.querySelectorAll('input[name="mod"]');
let selected = null;

function esc(s) { return s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

async function refresh() {
  if (!selected) return;
  const chosen = [...mods].filter(m => m.checked).map(m => m.value).join(",");
  const r = await fetch(`/api/score?scope=${selected.dataset.scope}&tier=${selected.dataset.tier}&mods=${chosen}`);
  const d = await r.json();
  const changed = d.final !== d.base;
  panel.classList.remove("empty");
  panel.innerHTML = `
    <div class="badge ${d.final}">${d.final} <small>${esc(d.targets.name)}</small></div>
    ${changed ? `<p class="axis">Matrix said <b>${d.base}</b>; modifiers moved it to <b>${d.final}</b>.</p>` : ""}
    <h2>Why</h2>
    <p class="axis"><b>Scope:</b> ${esc(d.scope.label)} — ${esc(d.scope.why)}</p>
    <p class="axis"><b>Criticality:</b> ${esc(d.tier.label)} — ${esc(d.tier.why)}</p>
    <ul class="steps">
      ${d.steps.map(s => `<li><span class="arrow">${s.priority}</span><b>${esc(s.label)}</b><br>${esc(s.why)}</li>`).join("")}
    </ul>
    <h2>What ${d.final} commits us to</h2>
    <div class="targets">
      <div><span>Respond</span>${esc(d.targets.respond)}</div>
      <div><span>Update people</span>${esc(d.targets.update)}</div>
      <div class="work"><span>Work pattern</span>${esc(d.targets.work)}</div>
    </div>
    <div class="check"><b>Sanity check:</b> if the reasoning above doesn't match the ticket in front of you,
      the scope or tier is probably wrong — re-check those before overriding the priority.</div>`;
}

cells.forEach(c => c.addEventListener("click", () => {
  cells.forEach(x => x.classList.remove("selected"));
  c.classList.add("selected");
  selected = c;
  refresh();
}));
mods.forEach(m => m.addEventListener("change", refresh));
