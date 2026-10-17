const $ = (id) => document.getElementById(id);
let allItems = [];

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  })[ch]);
}
function riskBadge(level) {
  return `<span class="risk ${esc(level)}">${esc(level)}</span>`;
}
function scoreBar(score) {
  const color = score >= 72 ? "#d94b5c" : score >= 52 ? "#d68b3e" : score >= 32 ? "#d4b444" : "#1a9a72";
  return `<div class="score"><div class="bar"><i style="width:${Math.min(100,score)}%;background:${color}"></i></div><b>${Number(score).toFixed(0)}</b></div>`;
}
async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}
async function load() {
  try {
    const [summary, inv, recs] = await Promise.all([
      api("/api/summary"), api("/api/inventory"), api("/api/recommendations")
    ]);
    allItems = inv.items;
    $("totalItems").textContent = summary.total_items;
    $("criticalItems").textContent = summary.critical_items;
    $("highItems").textContent = summary.high_risk_items;
    $("averageRisk").textContent = summary.average_risk;
    renderInventory();
    renderRecommendations(recs.recommendations);
    $("simSku").innerHTML = allItems.map(x => `<option value="${esc(x.sku)}">${esc(x.name)}</option>`).join("");
  } catch (error) {
    $("inventoryRows").innerHTML = `<tr><td colspan="5">Could not load data. Is the API running? ${esc(error.message)}</td></tr>`;
    $("recommendations").textContent = "Could not load recommendations.";
  }
}
function renderInventory() {
  const term = $("search").value.trim().toLowerCase();
  const level = $("riskFilter").value;
  const rows = allItems.filter(x => (!level || x.risk_level === level) &&
    (!term || `${x.name} ${x.category} ${x.sku}`.toLowerCase().includes(term)))
    .sort((a,b) => b.risk_score - a.risk_score);
  $("rowCount").textContent = `${rows.length} of ${allItems.length} items`;
  $("inventoryRows").innerHTML = rows.map(x => `<tr>
    <td><span class="item-name">${esc(x.name)}</span><span class="item-sub">${esc(x.sku)} · ${esc(x.site)}</span></td>
    <td><b>${Number(x.days_remaining).toFixed(1)} days</b><span class="item-sub">Lead time: ${x.lead_days} days</span></td>
    <td>${riskBadge(x.risk_level)}</td>
    <td>${scoreBar(x.risk_score)}</td>
    <td><b>${Number(x.recommended_order).toLocaleString()}</b><span class="item-sub">units</span></td>
  </tr>`).join("") || `<tr><td colspan="5">No items match this filter.</td></tr>`;
}
function renderRecommendations(items) {
  $("recommendations").innerHTML = items.map((x,i) => `<div class="reco">
    <div class="reco-num">${String(i+1).padStart(2,"0")}</div><div class="reco-body">
      <div class="reco-title">${esc(x.name)}</div>
      <div class="reco-meta">${riskBadge(x.risk_level)} &nbsp; Score ${x.risk_score} · ${x.days_remaining} days cover</div>
      <div class="reco-order">Review order of ${Number(x.recommended_order).toLocaleString()} units</div>
    </div></div>`).join("");
}
async function simulate() {
  const button = $("runSimulation");
  button.disabled = true; button.textContent = "Running…";
  try {
    const data = await api("/api/simulate", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({sku:$("simSku").value,demand_multiplier:Number($("multiplier").value),stock_delta:0})
    });
    $("simulationResult").innerHTML = `<div class="sim-comparison">
      <div><small>BASELINE RISK</small><strong>${riskBadge(data.baseline.risk_level)} ${data.baseline.risk_score}/100</strong><small>${data.baseline.days_remaining} days of stock</small></div>
      <div><small>SCENARIO RISK</small><strong>${riskBadge(data.scenario.risk_level)} ${data.scenario.risk_score}/100</strong><small>${data.scenario.days_remaining} days of stock</small></div>
      <div class="sim-note">Demand multiplier: ${data.assumptions.demand_multiplier}×. ${esc(data.note)}</div>
    </div>`;
  } catch (error) {
    $("simulationResult").textContent = `Scenario failed: ${error.message}`;
  } finally { button.disabled = false; button.textContent = "Run scenario →"; }
}
$("search").addEventListener("input", renderInventory);
$("riskFilter").addEventListener("change", renderInventory);
$("refresh").addEventListener("click", load);
$("runSimulation").addEventListener("click", simulate);
load();
