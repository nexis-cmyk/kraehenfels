import { AudioEngine } from "./audio-engine.js";
import { evaluateRoll, guideKindLabels } from "./guided-flow.js?v=3.3.0-r7";

const app = document.querySelector("#app");
const sceneNav = document.querySelector("#scene-nav");
const progressCount = document.querySelector("#progress-count");
const progressFill = document.querySelector("#progress-fill");
const audioStatus = document.querySelector("#audio-status");
const topbarBack = document.querySelector("#topbar-back");
const screenTitle = document.querySelector("#screen-title");
const topbarMenu = document.querySelector("#topbar-menu");
const topbarMenuPanel = document.querySelector("#topbar-menu-panel");
let nightPhases = [];
const phaseSymbols = ["✦", "⌂", "⌕", "!", "◉"];

function normalizedNightPhase(value) {
  const index = Number(value);
  if (!Number.isFinite(index)) return 0;
  const phaseCount = nightPhases.length || 5;
  return Math.min(Math.max(Math.trunc(index), 0), phaseCount - 1);
}

function normalizedFinaleCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? Math.min(Math.max(Math.trunc(count), 0), 2) : 0;
}

const stored = (key, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
};

const state = {
  manifest: null,
  view: "home",
  currentSceneId: localStorage.getItem("kraehenfels.currentScene") || "S01",
  completed: new Set(stored("kraehenfels.completed", [])),
  clues: new Set(stored("kraehenfels.clues", [])),
  checklist: new Set(stored("kraehenfels.checklist", [])),
  playerNames: Array.from({ length: 3 }, (_, index) => {
    const saved = stored("kraehenfels.playerNames", []);
    return typeof saved[index] === "string" ? saved[index] : "";
  }),
  sessionNote: localStorage.getItem("kraehenfels.sessionNote") || "",
  sceneNotes: stored("kraehenfels.sceneNotes", {}),
  nightPhase: normalizedNightPhase(localStorage.getItem("kraehenfels.nightPhase")),
  threatLevel: Math.min(5, Math.max(0, Number(localStorage.getItem("kraehenfels.threatLevel") || 0))),
  npcStates: stored("kraehenfels.npcStates", {}),
  selectedHooks: stored("kraehenfels.selectedHooks", {}),
  gmMode: stored("kraehenfels.gmMode", false),
  guidedIndexes: stored("kraehenfels.guidedIndexes", {}),
  guideHistory: stored("kraehenfels.guideHistory", []),
  setupChecks: new Set(stored("kraehenfels.setupChecks", [])),
  discoveredItemIDs: new Set(stored("kraehenfels.discoveredItemIDs", [])),
  itemOwners: (() => {
    const value = stored("kraehenfels.itemOwners", {});
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  })(),
  itemUseRecords: (() => {
    const value = stored("kraehenfels.itemUseRecords", []);
    return Array.isArray(value) ? value : [];
  })(),
  guidedRolls: stored("kraehenfels.guidedRolls", {}),
  guidedRollHistory: stored("kraehenfels.guidedRollHistory", []),
  finaleSuccesses: normalizedFinaleCount(localStorage.getItem("kraehenfels.finaleSuccesses")),
  finaleFailures: normalizedFinaleCount(localStorage.getItem("kraehenfels.finaleFailures")),
  finaleOutcome: localStorage.getItem("kraehenfels.finaleOutcome") || "",
  audioRatings: stored("kraehenfels.audioRatings", {}),
  endingID: localStorage.getItem("kraehenfels.endingID") || "",
  rollOpen: false,
  pendingRoll: null,
  selectedConsequenceID: "",
  selectedItemEffectIDs: {},
  spoilersOpen: false,
  statusTone: "ok",
};

function persist() {
  localStorage.setItem("kraehenfels.currentScene", state.currentSceneId);
  localStorage.setItem("kraehenfels.completed", JSON.stringify([...state.completed]));
  localStorage.setItem("kraehenfels.clues", JSON.stringify([...state.clues]));
  localStorage.setItem("kraehenfels.checklist", JSON.stringify([...state.checklist]));
  localStorage.setItem("kraehenfels.playerNames", JSON.stringify(state.playerNames));
  localStorage.setItem("kraehenfels.sessionNote", state.sessionNote);
  localStorage.setItem("kraehenfels.sceneNotes", JSON.stringify(state.sceneNotes));
  localStorage.setItem("kraehenfels.nightPhase", String(state.nightPhase));
  localStorage.setItem("kraehenfels.threatLevel", String(state.threatLevel));
  localStorage.setItem("kraehenfels.npcStates", JSON.stringify(state.npcStates));
  localStorage.setItem("kraehenfels.selectedHooks", JSON.stringify(state.selectedHooks));
  localStorage.setItem("kraehenfels.gmMode", JSON.stringify(state.gmMode));
  localStorage.setItem("kraehenfels.guidedIndexes", JSON.stringify(state.guidedIndexes));
  localStorage.setItem("kraehenfels.guideHistory", JSON.stringify(state.guideHistory));
  localStorage.setItem("kraehenfels.setupChecks", JSON.stringify([...state.setupChecks]));
  localStorage.setItem("kraehenfels.discoveredItemIDs", JSON.stringify([...state.discoveredItemIDs]));
  localStorage.setItem("kraehenfels.itemOwners", JSON.stringify(state.itemOwners));
  localStorage.setItem("kraehenfels.itemUseRecords", JSON.stringify(state.itemUseRecords));
  localStorage.setItem("kraehenfels.guidedRolls", JSON.stringify(state.guidedRolls));
  localStorage.setItem("kraehenfels.guidedRollHistory", JSON.stringify(state.guidedRollHistory));
  localStorage.setItem("kraehenfels.finaleSuccesses", String(state.finaleSuccesses));
  localStorage.setItem("kraehenfels.finaleFailures", String(state.finaleFailures));
  localStorage.setItem("kraehenfels.finaleOutcome", state.finaleOutcome);
  localStorage.setItem("kraehenfels.audioRatings", JSON.stringify(state.audioRatings));
  localStorage.setItem("kraehenfels.endingID", state.endingID);
}

const audio = new AudioEngine({
  onStatus(message, tone) {
    state.statusTone = tone;
    audioStatus.textContent = message;
    audioStatus.dataset.tone = tone;
  },
  onChange: render,
});

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sceneById(id) {
  return state.manifest.scenes.find((scene) => scene.id === id);
}

function cueById(id) {
  return state.manifest.audioCues.find((cue) => cue.id === id);
}

function npcById(id) {
  return state.manifest.npcs.find((npc) => npc.id === id);
}

function handoutById(id) {
  return state.manifest.handouts.find((handout) => handout.id === id);
}

function clueById(id) {
  return state.manifest.clues.find((clue) => clue.id === id);
}

function classForCategory(category) {
  return { ambient: "Atmosphäre", music: "Musik", sfx: "Effekt" }[category] || category;
}

function renderNavigation() {
  const scenes = state.manifest.scenes;
  const done = state.completed.size;
  progressCount.textContent = `${done} / ${scenes.length}`;
  progressFill.style.width = `${(done / scenes.length) * 100}%`;
  sceneNav.innerHTML = scenes.map((scene) => {
    const active = scene.id === state.currentSceneId;
    const complete = state.completed.has(scene.id);
    return `<button class="scene-link ${active ? "is-active" : ""}" data-scene="${scene.id}" type="button" aria-current="${active ? "page" : "false"}">
      <span class="scene-link-id">${scene.id}</span>
      <span class="scene-link-copy"><strong>${escapeHtml(scene.shortTitle)}</strong><small>${escapeHtml(scene.duration)}</small></span>
      <span class="scene-link-state" aria-label="${complete ? "abgeschlossen" : "offen"}">${complete ? "✓" : "›"}</span>
    </button>`;
  }).join("");
}

function toggleSet(set, value) {
  if (set.has(value)) set.delete(value); else set.add(value);
  persist();
  render();
}

function renderCue(cue) {
  const active = audio.isPlaying(cue.id);
  const rating = Number(state.audioRatings[cue.id] || 0);
  const clue = cue.isClue ? `<span class="pill pill-warning">Hinweis: ${cue.printFallbackId}</span>` : "";
  return `<div class="cue-row ${active ? "is-playing" : ""}" data-cue="${cue.id}">
    <button class="cue-play" data-cue-play="${cue.id}" type="button" aria-pressed="${active}" aria-label="${active ? "Stoppen" : "Starten"}: ${escapeHtml(cue.title)}">
      <span class="cue-action" aria-hidden="true">${active ? "Ⅱ" : "▶"}</span>
    </button>
    <span class="cue-copy"><strong>${escapeHtml(cue.title)}</strong><small>${cue.id} · ${classForCategory(cue.category)}</small></span>
    ${clue}
    <span class="cue-state">${active ? "Läuft" : "Start"}</span>
    <span class="cue-rating" aria-label="Klangbewertung">
      <button class="cue-rating-button ${rating === 1 ? "is-good" : ""}" data-rating-cue="${cue.id}" data-rating="1" type="button" aria-pressed="${rating === 1}" title="Klang passt">✓</button>
      <button class="cue-rating-button ${rating === -1 ? "is-bad" : ""}" data-rating-cue="${cue.id}" data-rating="-1" type="button" aria-pressed="${rating === -1}" title="Klang passt nicht">×</button>
    </span>
  </div>`;
}

function renderNPC(npc, sceneID) {
  const appearance = npc.appearances?.find((entry) => entry.sceneId === sceneID);
  const prompt = !appearance && npc.prompts?.[0] ? `<p class="npc-prompt">Impuls: ${escapeHtml(npc.prompts[0])}</p>` : "";
  const appearanceCard = appearance ? `<div class="npc-appearance">
      <p><span>AUFTRITT</span>${escapeHtml(appearance.when)}</p>
      <p><span>SO SPIELEN</span>${escapeHtml(appearance.playAs)}</p>
      <blockquote>„${escapeHtml(appearance.openingLine)}“</blockquote>
      <p><span>DANACH</span>${escapeHtml(appearance.turn)}</p>
    </div>` : "";
  const spoiler = state.spoilersOpen ? `<div class="npc-spoiler">
      ${npc.knows?.length ? `<p><span>WEISS</span>${npc.knows.map(escapeHtml).join("<br>")}</p>` : ""}
      ${npc.hides?.length ? `<p><span>VERSCHWEIGT</span>${npc.hides.map(escapeHtml).join("<br>")}</p>` : ""}
      ${npc.givesHandoutIds?.length ? `<p class="gives-handout"><span>GIBT</span>${npc.givesHandoutIds.map((id) => `${id} · ${escapeHtml(handoutById(id)?.title ?? "")}`).join("<br>")}</p>` : ""}
    </div>` : "";
  const stateIndex = Number(state.npcStates[npc.id] || 0);
  const states = npc.states?.length ? `<label class="npc-state"><span>Haltung</span><select data-npc-state="${npc.id}">${npc.states.map((label, index) => `<option value="${index}" ${index === stateIndex ? "selected" : ""}>${escapeHtml(label)}</option>`).join("")}</select></label>` : "";
  return `<article class="npc-entry">
    <div class="npc-heading"><div><h3>${escapeHtml(npc.name)}</h3><p>${escapeHtml(npc.role)}</p></div></div>
    <p>${escapeHtml(npc.description)}</p>${appearanceCard}${states}${spoiler}${prompt}
  </article>`;
}

function renderFrame(view, scene) {
  const isHome = view === "home";
  topbarBack.hidden = isHome;
  const backLabel = view === "guided" ? (state.guideHistory.length ? "Zurück" : "Übersicht") : "Krähenfels";
  topbarBack.dataset.action = view === "guided" ? "guide-back" : "home";
  topbarBack.querySelector("span:last-child").textContent = backLabel;
  screenTitle.textContent = isHome ? "Krähenfels" : view === "gm-start" ? "Spielleiter-Modus" : scene.shortTitle;
  document.body.dataset.view = view;
  topbarMenuPanel.hidden = true;
  topbarMenu.setAttribute("aria-expanded", "false");
}

function guideStepsFor(sceneID) {
  return state.manifest?.guide?.steps?.[sceneID] || [];
}

function guideItems() {
  return state.manifest?.guide?.items || [];
}

function itemLocations() {
  return state.manifest?.guide?.itemFindLocations || [];
}

function itemById(id) {
  return guideItems().find((item) => item.id === id);
}

function itemOwnerName(itemID) {
  const owner = state.itemOwners[itemID];
  if (owner === undefined || owner === null || owner === "") return "Gemeinsamer Vorrat";
  return state.playerNames[Number(owner)]?.trim() || `Figur ${Number(owner) + 1}`;
}

function itemRemainingUses(item) {
  return Math.max(0, Number(item.initialUses || 1) - state.itemUseRecords.filter((record) => record.itemID === item.id).length);
}

function discoverItems() {
  guideItems().forEach((item) => state.discoveredItemIDs.add(item.id));
}

function distributionComplete() {
  const items = guideItems();
  if (!items.length || items.some((item) => state.itemOwners[item.id] === undefined || state.itemOwners[item.id] === "")) return false;
  return new Set(items.map((item) => String(state.itemOwners[item.id]))).size === 3;
}

function itemEffectsFor(step, timing, consequenceID = "") {
  return guideItems().flatMap((item) => {
    if (state.itemOwners[item.id] === undefined || itemRemainingUses(item) < 1) return [];
    return (item.effects || []).filter((effect) => {
      const endingIDs = effect.endingIDs || [];
      const consequenceIDs = effect.consequenceIDs || [];
      return effect.timing === timing
        && (!effect.stepIDs?.length || effect.stepIDs.includes(step.id))
        && (!effect.sceneIDs?.length || effect.sceneIDs.includes(step.sceneID))
        && (!endingIDs.length || endingIDs.includes(state.endingID))
        && (!consequenceIDs.length || consequenceIDs.includes(consequenceID));
    }).map((effect) => ({ item, effect }));
  });
}

function activeItemModifier(step) {
  return itemEffectsFor(step, "beforeRoll").reduce((total, option) => state.selectedItemEffectIDs[option.item.id] === option.effect.id ? total + Number(option.effect.modifier || 0) : total, 0);
}

function selectedItemSelections(step, consequenceID = "") {
  return itemEffectsFor(step, "beforeRoll")
    .concat(itemEffectsFor(step, "afterFailure", consequenceID))
    .filter((option) => state.selectedItemEffectIDs[option.item.id] === option.effect.id)
    .map((option) => ({ itemID: option.item.id, effectID: option.effect.id }));
}

function resetItemState() {
  state.discoveredItemIDs = new Set();
  state.itemOwners = {};
  state.itemUseRecords = [];
  state.selectedItemEffectIDs = {};
}

function currentGuideIndex(sceneID) {
  const steps = guideStepsFor(sceneID);
  return Math.min(Math.max(Number(state.guidedIndexes[sceneID] || 0), 0), Math.max(0, steps.length - 1));
}

function currentGuideStep(sceneID) {
  return guideStepsFor(sceneID)[currentGuideIndex(sceneID)];
}

function availableRollConsequences(step) {
  const all = step?.roll?.failureConsequences || [];
  const available = all.filter((consequence) => {
    const endingIDs = consequence.endingIDs || [];
    return !endingIDs.length || endingIDs.includes(state.endingID);
  });
  return available.length ? available : all;
}

function rollOutcomeText(result, roll) {
  if (result.criticalFailure) return roll.criticalFailure;
  if (result.criticalSuccess) return roll.critical;
  return result.success ? roll.success : roll.failure;
}

function consequenceEffectText(effect = {}) {
  if (Number.isFinite(Number(effect.threatDelta))) {
    const value = Number(effect.threatDelta);
    return `Dorfspannung ${value >= 0 ? "+" : ""}${value}`;
  }
  if (Number.isFinite(Number(effect.minimumThreat))) return `Dorfspannung mindestens ${Number(effect.minimumThreat)}`;
  return "";
}

function applyConsequence(consequence) {
  const effect = consequence?.effect || {};
  if (Number.isFinite(Number(effect.threatDelta))) {
    state.threatLevel = Math.min(5, Math.max(0, state.threatLevel + Number(effect.threatDelta)));
  }
  if (Number.isFinite(Number(effect.minimumThreat))) {
    state.threatLevel = Math.min(5, Math.max(state.threatLevel, Number(effect.minimumThreat)));
  }
}

function consumeItemSelections(step, selections) {
  const created = [];
  for (const selection of selections) {
    const item = itemById(selection.itemID);
    const validEffect = itemEffectsFor(step, "beforeRoll").concat(itemEffectsFor(step, "afterFailure", state.selectedConsequenceID)).some(({ item: candidate, effect }) => candidate.id === selection.itemID && effect.id === selection.effectID);
    if (!item || !validEffect || state.itemOwners[item.id] === undefined || itemRemainingUses(item) < 1) {
      created.forEach((record) => {
        state.itemUseRecords = state.itemUseRecords.filter((itemRecord) => itemRecord.id !== record.id);
      });
      return [];
    }
    const record = {
      id: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`,
      itemID: item.id,
      effectID: selection.effectID,
      sceneID: step.sceneID || state.currentSceneId,
      stepID: step.id,
    };
    state.itemUseRecords.push(record);
    created.push(record);
  }
  return created;
}

function recordGuidedRoll(step, result, consequence, itemSelections = [], baseTarget = result.target) {
  const itemUseRecords = consumeItemSelections(step, itemSelections);
  if (itemSelections.length && itemUseRecords.length !== itemSelections.length) return false;
  const entry = {
    stepID: step.id,
    roll: result.roll,
    target: result.target,
    baseTarget,
    success: result.success,
    criticalSuccess: result.criticalSuccess,
    criticalFailure: result.criticalFailure,
    label: result.label,
    consequenceID: consequence?.id || "",
    consequenceTitle: consequence?.title || "",
    itemUseIDs: itemUseRecords.map((record) => record.id),
  };
  state.guidedRolls[step.id] = entry;
  state.guidedRollHistory.push(entry);
  if (!result.success) applyConsequence(consequence);
  return true;
}

function recordFinaleRoll(result, consequence, itemSelections = [], baseTarget = result.target) {
  if (!recordGuidedRoll({ id: "S07_DANGER", sceneID: "S07" }, result, consequence, itemSelections, baseTarget)) return { resolved: false, rejected: true };
  if (result.criticalFailure) {
    state.finaleFailures = Math.min(2, state.finaleFailures + 2);
  } else if (result.success) {
    state.finaleSuccesses = Math.min(2, state.finaleSuccesses + 1);
  } else {
    state.finaleFailures = Math.min(2, state.finaleFailures + 1);
  }
  if (state.finaleSuccesses >= 2) {
    state.finaleOutcome = "success";
    return { resolved: true };
  }
  if (state.finaleFailures >= 2) {
    state.finaleOutcome = "failure";
    state.threatLevel = Math.min(5, state.threatLevel + 1);
    return { resolved: true };
  }
  return { resolved: false };
}

function resetFinaleProgress() {
  state.finaleSuccesses = 0;
  state.finaleFailures = 0;
  state.finaleOutcome = "";
}

function clearFinaleRolls() {
  delete state.guidedRolls.S07_DANGER;
  state.guidedRollHistory = state.guidedRollHistory.filter((entry) => entry.stepID !== "S07_DANGER");
  state.itemUseRecords = state.itemUseRecords.filter((record) => record.stepID !== "S07_DANGER");
}

function pushGuidePosition() {
  state.guideHistory.push({ sceneID: state.currentSceneId, stepIndex: currentGuideIndex(state.currentSceneId) });
}

function advanceGuideStep() {
  const steps = guideStepsFor(state.currentSceneId);
  const step = currentGuideStep(state.currentSceneId);
  if (step?.id === "S01_DISTRIBUTE" && !distributionComplete()) return false;
  if (step?.id === "S01_ITEMS") discoverItems();
  if (step?.clueID) state.clues.add(step.clueID);
  pushGuidePosition();
  state.guidedIndexes[state.currentSceneId] = Math.min(currentGuideIndex(state.currentSceneId) + 1, Math.max(0, steps.length - 1));
  state.rollOpen = false;
  state.pendingRoll = null;
  state.selectedConsequenceID = "";
  state.selectedItemEffectIDs = {};
  return true;
}

function resetDependentPath(destination) {
  const order = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08"];
  const index = order.indexOf(destination);
  if (index < 0) return;
  const dependent = new Set(order.slice(index + 1));
  state.completed = new Set([...state.completed].filter((sceneID) => !dependent.has(sceneID)));
  state.guidedIndexes = Object.fromEntries(Object.entries(state.guidedIndexes).filter(([sceneID]) => !dependent.has(sceneID)));
  state.guidedRolls = Object.fromEntries(Object.entries(state.guidedRolls).filter(([stepID]) => !dependent.has(stepID.slice(0, 3))));
  state.guidedRollHistory = state.guidedRollHistory.filter((entry) => !dependent.has(String(entry.stepID || "").slice(0, 3)));
  state.itemUseRecords = state.itemUseRecords.filter((record) => !dependent.has(String(record.sceneID || "").slice(0, 3)));
  state.guideHistory = state.guideHistory.filter((position) => !dependent.has(position.sceneID));
  if (index < order.indexOf("S07")) {
    state.endingID = "";
    resetFinaleProgress();
  }
}

function goBackInGuide() {
  const previous = state.guideHistory.pop();
  if (!previous) {
    state.view = "home";
  } else {
    state.currentSceneId = previous.sceneID;
    state.guidedIndexes[previous.sceneID] = previous.stepIndex;
    state.view = "guided";
  }
  state.rollOpen = false;
  state.pendingRoll = null;
  state.selectedConsequenceID = "";
  state.selectedItemEffectIDs = {};
  persist();
  render();
  document.querySelector("#scene-content").focus();
}

function guideReference(id) {
  if (!id) return "";
  const handout = handoutById(id);
  const clue = clueById(id);
  const npc = npcById(id);
  if (handout) return `${handout.id} · ${handout.title}`;
  if (clue) return `${clue.id} · ${clue.title}`;
  if (npc) return `${npc.name} · ${npc.role}`;
  return id;
}

function guideReferences(step) {
  const ids = [...new Set([step.handoutID, ...(step.handoutIDs || []), step.clueID, step.npcID, ...(step.npcIDs || [])].filter(Boolean))];
  if (!ids.length) return "";
  return `<div class="guide-references"><span class="eyebrow">Direkt griffbereit</span><div>${ids.map((id) => `<span class="guide-reference">${escapeHtml(guideReference(id))}</span>`).join("")}</div></div>`;
}

function itemOwnerSelect(item, label = "Besitz") {
  const owner = state.itemOwners[item.id];
  return `<label class="item-owner-select"><span>${label}</span><select data-item-owner="${escapeHtml(item.id)}" aria-label="Besitz von ${escapeHtml(item.title)}"><option value="" ${owner === undefined || owner === "" ? "selected" : ""}>Gemeinsamer Vorrat</option>${state.playerNames.map((name, index) => `<option value="${index}" ${Number(owner) === index ? "selected" : ""}>${escapeHtml(name.trim() || `Figur ${index + 1}`)}</option>`).join("")}</select></label>`;
}

function renderItemFindings() {
  return `<div class="item-findings"><span class="eyebrow">Drei Fundorte · keine Probe</span><strong>Alle sechs Gegenstände werden gefunden.</strong>${itemLocations().map((location) => `<article class="item-location"><h3>${escapeHtml(location.title)}</h3><p>${escapeHtml(location.detail)}</p><ul>${(location.itemIDs || []).map((itemID) => `<li><span>□</span>${escapeHtml(itemById(itemID)?.title || itemID)}</li>`).join("")}</ul></article>`).join("")}</div>`;
}

function renderItemDistribution() {
  const items = guideItems();
  const complete = distributionComplete();
  return `<div class="item-distribution"><div class="item-distribution-heading"><span class="eyebrow">Sechs Gegenstände</span><b>${Object.values(state.itemOwners).filter((value) => value !== "").length}/${items.length} verteilt</b></div><p>Verteile alle Funde. Jede der drei Figuren braucht mindestens einen, die übrigen dürfen frei aufgeteilt werden.</p>${items.map((item) => `<article class="item-distribution-row"><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></div>${itemOwnerSelect(item)}</article>`).join("")}<div class="item-distribution-status ${complete ? "is-complete" : ""}">${complete ? "✓ Alle Figuren haben mindestens einen Gegenstand." : "Noch nicht bereit: alle Gegenstände verteilen und jede Figur berücksichtigen."}</div></div>`;
}

function renderInventorySection() {
  const items = guideItems();
  if (!items.length) return `<section class="content-section inventory-section"><div class="section-heading"><h2>Ausrüstung</h2><span>Keine Gegenstände geladen</span></div></section>`;
  return `<section class="content-section inventory-section" aria-labelledby="inventory-title"><div class="section-heading"><div><h2 id="inventory-title">Gemeinsame Ausrüstung</h2><p>Die sechs Gegenstände aus der Kutsche. Ihr könnt sie jederzeit weitergeben.</p></div><span>${distributionComplete() ? "vollständig verteilt" : "Verteilung offen"}</span></div><div class="inventory-list">${items.map((item) => `<article class="inventory-card"><div class="inventory-card-heading"><h3>${escapeHtml(item.title)}</h3><b>${itemRemainingUses(item)}/${Number(item.initialUses || 1)}</b></div><p>${escapeHtml(item.detail)}</p><small class="inventory-location">Fundort: ${escapeHtml(itemLocations().find((location) => location.id === item.locationID)?.title || item.locationID)}</small>${item.weapon ? `<small class="inventory-weapon">${escapeHtml(item.weapon.skill)} · Schaden ${escapeHtml(item.weapon.damageDice)} · nicht parierbar</small>` : ""}${(item.effects || []).map((effect) => `<small class="inventory-effect">${escapeHtml(effect.title)}: ${escapeHtml(effect.detail)}</small>`).join("")}${itemOwnerSelect(item)}</article>`).join("")}</div></section>`;
}

function renderGMStart() {
  const checked = state.setupChecks.size;
  return `<div class="gm-start-view">
    <section class="gm-intro">
      <p class="home-kicker">Spielleiter-Modus</p>
      <h2>Heute Abend musst du nichts auswendig können.</h2>
      <p>Dieser Assistent führt dich durch Vorbereitung, Vorlesetexte, Spieleraktionen, Hinweise und Würfelproben. Du entscheidest jederzeit selbst, ob die Gruppe einen anderen Weg nimmt.</p>
    </section>
    <section class="guide-panel setup-panel" aria-labelledby="setup-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Vorbereitung</span><h2 id="setup-title">In fünf Minuten startklar</h2></div><b>${checked}/${state.manifest.guide.setupItems.length}</b></div>
      <div class="setup-list">${state.manifest.guide.setupItems.map((item) => `<button class="setup-row" data-setup="${item.id}" type="button" aria-pressed="${state.setupChecks.has(item.id)}"><span class="setup-check">${state.setupChecks.has(item.id) ? "✓" : ""}</span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></span></button>`).join("")}</div>
    </section>
    <section class="guide-panel characters-panel" aria-labelledby="characters-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Drei eigene Figuren</span><h2 id="characters-title">Namen für den Spieltisch</h2></div><span class="guide-muted">Werte bleiben auf euren Bögen</span></div>
      <p class="guide-muted character-intro">Jede Person bringt ihren eigenen Charakter mit. Die App speichert nur die Namen und verwendet keine vorgegebenen Rollen oder Verbindungen.</p>
      <div class="character-input-grid">${state.playerNames.map((name, index) => `<label class="character-input"><span>${index + 1}. Figur</span><input data-player-index="${index}" type="text" autocomplete="off" autocapitalize="words" placeholder="Name der Figur" value="${escapeHtml(name)}"></label>`).join("")}</div>
    </section>
    <section class="guide-panel briefing-panel" aria-labelledby="briefing-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Vor dem ersten Satz</span><h2 id="briefing-title">Das sagst du den Spielern</h2></div></div>
      <blockquote>${escapeHtml(state.manifest.guide.playerBriefing)}</blockquote>
      <p class="spoiler-line"><span>NICHT VERRATEN</span> ${escapeHtml(state.manifest.guide.hiddenFromPlayers)}</p>
    </section>
    <button class="button button-primary guide-start-button" data-guide-action="begin" type="button" ${state.playerNames.every((name) => name.trim()) ? "" : "disabled"}>${checked === state.manifest.guide.setupItems.length ? "Spielleiter-Modus starten" : "Trotzdem starten"}<span aria-hidden="true">›</span></button>
    ${state.playerNames.every((name) => name.trim()) ? "" : "<p class=\"guide-start-hint\">Bitte alle drei eigenen Figuren benennen, bevor die Runde startet.</p>"}
  </div>`;
}

function itemUseTitles(entry) {
  return (entry?.itemUseIDs || []).map((recordID) => itemById(state.itemUseRecords.find((record) => record.id === recordID)?.itemID)?.title).filter(Boolean);
}

function renderItemEffectOptions(step, timing, consequenceID = "") {
  const options = itemEffectsFor(step, timing, consequenceID);
  if (!options.length) return "";
  const title = timing === "beforeRoll" ? "Ausrüstung vor der Probe" : "Ausrüstung für die gewählte Folge";
  return `<div class="item-effect-options"><span class="eyebrow">${title}</span><p>Die Anwendung wird erst beim Übernehmen verbraucht.</p>${options.map(({ item, effect }) => {
    const selected = state.selectedItemEffectIDs[item.id] === effect.id;
    const modifier = effect.modifier ? ` · Zielwert +${effect.modifier}` : "";
    return `<button class="item-effect-option ${selected ? "is-selected" : ""}" data-guide-action="select-item-effect" data-item-id="${escapeHtml(item.id)}" data-effect-id="${escapeHtml(effect.id)}" type="button" aria-pressed="${selected}"><span class="roll-consequence-marker" aria-hidden="true">${selected ? "✓" : "○"}</span><span><strong>${escapeHtml(item.title)} · ${escapeHtml(effect.title)}</strong><small>Besitz: ${escapeHtml(itemOwnerName(item.id))} · noch ${itemRemainingUses(item)} Anwendung(en)${modifier}</small><em>${escapeHtml(effect.detail)}</em></span></button>`;
  }).join("")}</div>`;
}

function renderRollPanel(step) {
  const roll = step.roll;
  const previous = state.guidedRolls[step.id];
  if (!state.rollOpen) {
    const previousItems = itemUseTitles(previous);
    const sessionSummary = previous
      ? `<div class="roll-session-summary"><strong>Letztes Ergebnis: ${escapeHtml(previous.label)}</strong><span>${previous.roll} gegen ${previous.target}</span>${previous.consequenceTitle ? `<em>Gewählte Folge: ${escapeHtml(previous.consequenceTitle)}</em>` : ""}${previousItems.length ? `<em>Eingesetzte Ausrüstung: ${escapeHtml(previousItems.join(", "))}</em>` : ""}</div>`
      : "";
    const optionalSkip = roll.required ? "" : `<button class="button button-quiet guide-action" data-guide-action="advance" type="button">Ohne Probe weiter<span aria-hidden="true">›</span></button>`;
    return `${sessionSummary}<button class="button button-primary guide-action" data-guide-action="open-roll" type="button">Probe auswerten</button>${optionalSkip}`;
  }
  const pending = state.pendingRoll?.stepID === step.id ? state.pendingRoll : null;
  const displayed = pending?.result || previous;
  const consequences = displayed && !displayed.success ? availableRollConsequences(step) : [];
  const selectedConsequence = consequences.find((consequence) => consequence.id === state.selectedConsequenceID);
  const hasPendingFailure = Boolean(pending && !pending.result.success);
  const needsSelection = hasPendingFailure && consequences.length > 0 && !selectedConsequence;
  const consequenceMarkup = hasPendingFailure && consequences.length
    ? `<div class="roll-consequences"><span class="eyebrow">${consequences.length === 1 ? "Folge bestätigen" : "Was passiert jetzt?"}</span><p>Wähle die Folge, die du am Tisch ausspielst.</p>${consequences.map((consequence) => {
      const selected = consequence.id === state.selectedConsequenceID;
      const effect = consequenceEffectText(consequence.effect);
      return `<button class="roll-consequence ${selected ? "is-selected" : ""}" data-guide-action="select-consequence" data-consequence="${escapeHtml(consequence.id)}" type="button" aria-pressed="${selected}"><span class="roll-consequence-marker" aria-hidden="true">${selected ? "✓" : "○"}</span><span><strong>${escapeHtml(consequence.title)}</strong><small>${escapeHtml(consequence.detail)}</small>${effect ? `<em>${escapeHtml(effect)}</em>` : ""}</span></button>`;
    }).join("")}${selectedConsequence ? renderItemEffectOptions(step, "afterFailure", selectedConsequence.id) : ""}</div>`
    : "";
  const resultMarkup = displayed
    ? `<div class="roll-result ${displayed.success ? "is-success" : "is-failure"}"><strong>${escapeHtml(displayed.label)}</strong><span>${displayed.roll} gegen ${displayed.target}</span><p>${escapeHtml(rollOutcomeText(displayed, roll))}</p>${!pending && displayed.consequenceTitle ? `<em class="roll-result-consequence">Gewählte Folge: ${escapeHtml(displayed.consequenceTitle)}</em>` : ""}${displayed.success ? "" : consequenceMarkup}${pending ? `<button class="button ${displayed.success || !needsSelection ? "button-primary" : "button-quiet"} guide-action roll-confirm" data-guide-action="confirm-roll" data-step="${step.id}" type="button" ${needsSelection ? "disabled" : ""}>${displayed.success || !consequences.length ? "Ergebnis übernehmen" : "Konsequenz übernehmen"}<span aria-hidden="true">›</span></button>` : ""}</div>`
    : "";
  const itemMarkup = renderItemEffectOptions(step, "beforeRoll");
  const baseTarget = pending?.baseTarget || previous?.baseTarget || previous?.target || 50;
  const activeModifier = activeItemModifier(step);
  return `<div class="roll-panel"><div class="roll-panel-heading"><div><span class="eyebrow">W100-Probe</span><strong>${escapeHtml(roll.actor)}</strong></div><button class="text-button" data-guide-action="close-roll" type="button">Schließen</button></div><p><b>Fertigkeit:</b> ${escapeHtml(roll.ability)} · <b>Zielwert:</b> ${escapeHtml(roll.target)}</p><p class="roll-modifier">${escapeHtml(roll.modifier)}</p><div class="roll-inputs"><label class="roll-input"><span>Gewürfeltes Ergebnis</span><input data-roll-value type="number" min="1" max="100" inputmode="numeric" value="${pending?.result.roll || previous?.roll || ""}" placeholder="z. B. 42"></label><label class="roll-input"><span>Basis-Zielwert</span><input data-roll-target type="number" min="1" max="100" inputmode="numeric" value="${baseTarget}" placeholder="z. B. 65"></label></div>${itemMarkup}${activeModifier ? `<p class="roll-item-modifier">Effektiver Zielwert: Basis +${activeModifier}, maximal 100.</p>` : ""}<button class="button button-primary guide-action" data-guide-action="resolve-roll" data-step="${step.id}" type="button">${pending ? "Ergebnis neu auswerten" : "Ergebnis auswerten"}<span aria-hidden="true">›</span></button>${resultMarkup}</div>`;
}

function renderFinaleProgress() {
  const status = state.finaleOutcome === "success"
    ? "Die Gefahrenszene ist zugunsten der Gruppe entschieden."
    : state.finaleOutcome === "failure"
      ? "Zwei Fehlschläge: Die Gefahrenszene ist zugunsten des Waldes entschieden."
      : "Zwei Erfolge vor zwei Fehlschlägen. Ein kritischer Misserfolg zählt doppelt.";
  return `<div class="roll-finale"><div><strong>Geführte Gefahrenszene</strong><b>${state.finaleSuccesses} : ${state.finaleFailures}</b></div><progress max="2" value="${state.finaleSuccesses}"></progress><small>${escapeHtml(status)}</small></div>`;
}

function renderRulesSection() {
  const rules = state.manifest.rules || [];
  return `<section class="content-section rules-section" aria-labelledby="rules-title">
    <div class="section-heading"><div><h2 id="rules-title">Regeln</h2><p>How to be a Hero, kurz am Tisch.</p></div><span>W100-System</span></div>
    <div class="rules-list">${rules.map((entry) => `<article class="rule-row"><h3>${escapeHtml(entry.title)}</h3><p>${escapeHtml(entry.body)}</p></article>`).join("")}</div>
  </section>`;
}

function renderGuideStep(step) {
  if (!step) return `<div class="guide-empty"><h2>Schritt abgeschlossen</h2><p>Wähle links eine Szene oder kehre zum Start zurück.</p></div>`;
  const scene = sceneById(step.sceneID || state.currentSceneId);
  const index = currentGuideIndex(state.currentSceneId);
  const steps = guideStepsFor(state.currentSceneId);
  const cue = step.audioCueID ? cueById(step.audioCueID) : null;
  const options = step.options || [];
  let action = "";
  if (step.roll) action = renderRollPanel(step);
  else if (options.length) action = `<div class="guide-options">${options.map((option) => `<button class="guide-option" data-guide-option="${option.id}" data-destination="${option.destinationSceneID || ""}" data-ending="${option.endingID || ""}" type="button"><strong>${escapeHtml(option.title)}</strong><small>${escapeHtml(option.detail)}</small><span aria-hidden="true">›</span></button>`).join("")}</div>`;
  else if (step.kind === "readAloud") action = `<button class="button button-primary guide-action" data-guide-action="read" data-cue="${cue?.id || ""}" type="button">${cue ? "Sound vorbereiten und vorlesen" : "Vorgelesen – weiter"}<span aria-hidden="true">›</span></button>`;
  else if (step.kind === "itemDistribution") action = `<button class="button button-primary guide-action" data-guide-action="advance" type="button" ${distributionComplete() ? "" : "disabled"}>${escapeHtml(step.actionLabel || "Verteilung abschließen")}<span aria-hidden="true">›</span></button>`;
  else action = `<button class="button button-primary guide-action" data-guide-action="advance" type="button">${escapeHtml(step.actionLabel || "Weiter")}<span aria-hidden="true">›</span></button>`;
  const clueLine = step.clueID ? `<div class="guide-clue-note"><span>HINWEIS</span> Dieser Hinweis ist garantiert und darf nicht an einem Würfelwurf scheitern.</div>` : "";
  const itemPanel = step.kind === "itemSearch" ? renderItemFindings() : step.kind === "itemDistribution" ? renderItemDistribution() : "";
  return `<div class="guided-scene-view">
    <div class="guide-progress-row"><span>SCHRITT ${index + 1} VON ${steps.length}</span><b>${escapeHtml(scene.shortTitle)}</b></div>
    <div class="guide-progress-track"><i style="width:${((index + 1) / Math.max(1, steps.length)) * 100}%"></i></div>
    <section class="guide-scene-hero" style="--scene-art: url('./assets/art/${encodeURIComponent(scene.art)}')"><div><span>${escapeHtml(scene.id)} · ${escapeHtml(scene.duration)}</span><h2>${escapeHtml(scene.title)}</h2><p>${escapeHtml(scene.goal)}</p></div></section>
    <section class="guide-step-card kind-${step.kind}">
      <div class="guide-kind"><span>${escapeHtml(guideKindLabels[step.kind] || "SPIELLEITER-SCHRITT")}</span>${step.roll?.required ? "<b>PFLICHT</b>" : ""}</div>
      <h2>${escapeHtml(step.title)}</h2>
      <p class="guide-step-body">${escapeHtml(step.body)}</p>
      ${step.roll ? `<div class="roll-brief"><span class="eyebrow">WANN WIRD GEWÜRFELT?</span><strong>${escapeHtml(step.roll.actor)}</strong><p>${escapeHtml(step.roll.ability)} · ${escapeHtml(step.roll.target)}</p><small>${escapeHtml(step.roll.modifier)}</small></div>` : ""}
      ${step.id === "S07_DANGER" ? renderFinaleProgress() : ""}
      ${clueLine}${itemPanel}${guideReferences(step)}
      ${action}
    </section>
    <div class="guide-footer">
      <button class="button button-quiet" data-guide-action="back" type="button"><span aria-hidden="true">←</span> ${state.guideHistory.length ? "Zurück" : "Übersicht"}</button>
      <span>${options.length ? "Wähle oben den nächsten Schritt." : "Der nächste Schritt bleibt unten sichtbar."}</span>
    </div>
    <div class="guide-quick-actions"><button class="quick-action" data-action="materials" type="button">▱ Materialien</button><button class="quick-action" data-action="inventory" type="button">□ Ausrüstung</button><button class="quick-action" data-action="rules" type="button">▧ Regeln</button><button class="quick-action" data-action="audio-check" type="button">≋ Soundplan</button><button class="quick-action" data-action="dossier" type="button">⌕ Fakten</button></div>
    <section class="guide-table-note"><div><span class="eyebrow">TISCHNOTIZ</span><p>Was ist gerade passiert? Was bleibt offen?</p></div><textarea data-scene-note="${scene.id}" rows="3" placeholder="Kurz notieren …">${escapeHtml(state.sceneNotes[scene.id] || "")}</textarea></section>
  </div>`;
}

function renderGuidedScene(scene) {
  return renderGuideStep(currentGuideStep(scene.id));
}

function renderHome(scene) {
  const scenes = state.manifest.scenes;
  const totalSteps = state.gmMode ? Math.max(1, guideStepsFor(scene.id).length) : Math.max(1, scene.checklist.length);
  const doneSteps = scene.checklist.filter((_, index) => state.checklist.has(`${scene.id}-${index}`)).length;
  const currentStep = Math.min(doneSteps + 1, totalSteps);
  const assignedPlayers = state.playerNames.filter((name) => name.trim()).length;
  const sceneProgress = Math.round((state.completed.size / Math.max(1, scenes.length)) * 100);
  const nightSegments = Array.from({ length: nightPhases.length + 1 }, (_, index) => `<i class="night-segment ${index <= state.nightPhase ? "is-active" : ""}"></i>`).join("");
  const stageLabel = state.completed.size ? `${state.completed.size}/${scenes.length}` : `0/${scenes.length}`;
  const sessionFinished = !state.gmMode && state.completed.has("S08");
  const unassigned = 3 - assignedPlayers;
  const tableLabel = assignedPlayers === 3 ? "Alle drei Reisenden sind zugewiesen" : unassigned === 3 ? "Drei Reisende sind noch nicht zugewiesen" : unassigned === 2 ? "Zwei Reisende sind noch nicht zugewiesen" : "Ein Reisender ist noch nicht zugewiesen";
  return `<div class="home-view">
    <section class="home-intro" aria-labelledby="home-title">
      <p class="home-kicker">Krähenfels · Die letzte Kutsche</p>
      <h1 id="home-title"><span>Dein Leitstand für</span><span>die Nacht.</span></h1>
      <p class="home-subtitle">Drei Reisende · Schwarzwald · November 1890</p>
    </section>

    <button class="home-start-card" data-action="start" type="button">
      <span class="home-icon home-icon-play" aria-hidden="true">▶</span>
      <span class="home-card-copy"><strong>Spielleiter-Modus starten</strong><small>Eigene Figuren, Kutschenfunde und Schritt-für-Schritt-Führung</small></span>
      <span class="home-chevron" aria-hidden="true">›</span>
    </button>

    ${sessionFinished
      ? `<section class="home-card continue-card" aria-label="Abenteuer abgeschlossen"><span class="home-icon home-icon-route" aria-hidden="true">✓</span><span class="home-card-copy"><span class="home-card-label">Abenteuer abgeschlossen</span><strong>Danke für euren Abend in Krähenfels.</strong><small>Starte oben eine neue Runde mit drei eigenen Figuren.</small></span></section>`
      : `<button class="home-card continue-card" data-action="continue" type="button"><span class="home-icon home-icon-route" aria-hidden="true">⌁</span><span class="home-card-copy"><span class="home-card-label">Jetzt weiterspielen <b>${stageLabel}</b></span><strong>${escapeHtml(scene.shortTitle)}</strong><small>Schritt ${currentStep} von ${totalSteps}</small><span class="home-progress"><i style="width:${sceneProgress}%"></i></span></span><span class="home-chevron" aria-hidden="true">↗</span></button>`}

    <section class="home-card table-summary" aria-labelledby="table-summary-title">
      <div class="home-card-copy"><span class="home-card-label" id="table-summary-title">Am Tisch</span><strong>${escapeHtml(tableLabel)}</strong></div>
      <button class="icon-button" data-action="table" type="button" aria-label="Tischdaten bearbeiten">⌕</button>
    </section>

    <section class="home-card night-summary" aria-labelledby="night-summary-title">
      <div class="night-summary-heading"><span class="home-card-label" id="night-summary-title">Nachtstand</span><b>Stufe ${state.nightPhase}/5</b></div>
      <div class="night-segments" aria-hidden="true">${nightSegments}</div>
      <p>${escapeHtml(nightPhases[state.nightPhase].detail)}</p>
      <label class="night-range"><span>Dorfspannung manuell setzen</span><input data-threat type="range" min="0" max="5" step="1" value="${state.threatLevel}" aria-label="Dorfspannung"></label>
    </section>

    <section class="home-scenes" aria-labelledby="home-scenes-title">
      <div class="home-section-heading"><h2 id="home-scenes-title">Szenen</h2><span>${scenes.length} Abschnitte</span></div>
      <div class="home-scene-list">${scenes.map((item) => {
        const complete = state.completed.has(item.id);
        const gmJump = item.id !== "S01" && !complete;
        return `<button class="home-scene-row ${item.id === scene.id ? "is-current" : ""}" data-scene="${item.id}" type="button"><span class="home-scene-id">${item.id}</span><span class="home-scene-copy"><strong>${escapeHtml(item.title)}</strong><small class="${gmJump ? "is-warning" : ""}">${escapeHtml(item.duration)} · ${complete ? "abgeschlossen" : gmJump ? "GM-Sprung" : "empfohlen"}</small></span><span class="home-chevron" aria-hidden="true">›</span></button>`;
      }).join("")}</div>
    </section>

    <section class="home-quick-grid" aria-label="Spielleiter-Materialien">
      <button class="quick-action" data-action="materials" type="button"><span aria-hidden="true">▱</span>Materialien</button>
      <button class="quick-action" data-action="inventory" type="button"><span aria-hidden="true">□</span>Ausrüstung</button>
      <button class="quick-action" data-action="rules" type="button"><span aria-hidden="true">▧</span>Regeln</button>
      <button class="quick-action" data-action="audio-check" type="button"><span aria-hidden="true">≋</span>Audio-Check</button>
      <button class="quick-action" data-action="dossier" type="button"><span aria-hidden="true">⌕</span>Akte</button>
    </section>
  </div>`;
}

function render() {
  if (!state.manifest) return;
  const scene = sceneById(state.currentSceneId) || state.manifest.scenes[0];
  const cues = scene.audioCueIds.map(cueById).filter(Boolean);
  const clues = scene.clueIds.map(clueById).filter(Boolean);
  const npcs = scene.npcIds.map(npcById).filter(Boolean);
  const handouts = scene.handoutIds.map(handoutById).filter(Boolean);
  const checklistCount = scene.checklist.filter((_, index) => state.checklist.has(`${scene.id}-${index}`)).length;
  const nextScene = scene.nextSceneIds[0] ? sceneById(scene.nextSceneIds[0]) : null;
  const nightPhase = nightPhases[state.nightPhase];
  renderNavigation();
  if (state.view === "home") {
    renderFrame("home", scene);
    app.innerHTML = renderHome(scene);
    return;
  }
  if (state.view === "gm-start") {
    renderFrame("gm-start", scene);
    app.innerHTML = renderGMStart();
    return;
  }
  if (state.view === "guided") {
    renderFrame("guided", scene);
    app.innerHTML = renderGuidedScene(scene);
    return;
  }
  const soundboard = cues.length ? `
    <section class="soundboard" aria-labelledby="soundboard-title">
      <div class="section-heading soundboard-heading"><div><h2 id="soundboard-title">Soundboard</h2><p>Preset für die Stimmung. Effekte bleiben bewusst einzeln.</p></div><button class="button button-primary" data-action="preset" type="button">Szene starten</button></div>
      <div class="audio-mix" aria-label="Lautstärken">
        ${[["master", "Gesamt"], ["ambient", "Atmosphäre"], ["music", "Musik"], ["sfx", "Effekte"]].map(([key, label]) => `<label>${label}<input data-volume="${key}" type="range" min="0" max="1" step="0.01" value="${audio.settings[key]}"></label>`).join("")}
      </div>
      <div class="cue-list">${cues.map(renderCue).join("")}</div>
    </section>` : `
    <section class="soundboard soundboard--silent" aria-labelledby="soundboard-title">
      <div class="section-heading"><div><h2 id="soundboard-title">Soundboard</h2><p>Der letzte Cue ist die Stille.</p></div></div>
      <p class="quiet-copy">Für den Epilog keine neue Tonspur starten. Lass nach der Entscheidung einen Moment Raum, bevor ihr erzählt, was von Krähenfels bleibt.</p>
    </section>`;

  renderFrame("scene", scene);
  app.innerHTML = `
    <section class="scene-hero" style="--scene-art: url('./assets/art/${encodeURIComponent(scene.art)}')">
      <div class="scene-hero-content">
        <div class="scene-meta"><span>${scene.id}</span><span>${escapeHtml(scene.duration)}</span><span>${escapeHtml(nightPhase.symbol)} ${escapeHtml(nightPhase.title)}</span><span>${escapeHtml(scene.soundPreset || "Freies Spiel")}</span></div>
        <h2>${escapeHtml(scene.title)}</h2>
        <p>${escapeHtml(scene.goal)}</p>
      </div>
      <div class="escalation" aria-label="Dorfspannung Stufe ${state.threatLevel} von 5">
        <span>Dorfspannung</span><div>${[0, 1, 2, 3, 4].map((level) => `<i class="${level < state.threatLevel ? "is-hot" : ""}"></i>`).join("")}</div><strong>${state.threatLevel}/5</strong>
      </div>
    </section>

    <section class="reading-block" aria-labelledby="read-aloud-title">
      <div class="section-heading"><h2 id="read-aloud-title">Vorlesen</h2><span aria-hidden="true">“</span></div>
      <p>${escapeHtml(scene.readAloud)}</p>
    </section>

    ${renderRulesSection()}

    <section class="content-section table-section" aria-labelledby="table-title">
      <div class="section-heading"><div><h2 id="table-title">Am Tisch</h2><p>Nur auf diesem Gerät gespeichert.</p></div><button class="text-button" data-action="clear-table" type="button">Tischdaten löschen</button></div>
      <div class="night-control" aria-label="Nachtstand">
        <div><span class="eyebrow">Nachtstand</span><strong>${escapeHtml(nightPhase.symbol)} ${escapeHtml(nightPhase.title)}</strong><small>${escapeHtml(nightPhase.detail)}</small></div>
        <div class="night-control-actions"><button class="button button-quiet" data-action="night-previous" type="button" ${state.nightPhase === 0 ? "disabled" : ""}>Zurück</button><select data-night-phase aria-label="Nachtstand auswählen">${nightPhases.map((phase, index) => `<option value="${index}" ${index === state.nightPhase ? "selected" : ""}>${escapeHtml(phase.title)}</option>`).join("")}</select><button class="button button-primary" data-action="night-next" type="button" ${state.nightPhase === nightPhases.length - 1 ? "disabled" : ""}>Weiter</button></div>
      </div>
      <label class="field threat-field"><span>Dorfspannung manuell setzen</span><input data-threat type="range" min="0" max="5" step="1" value="${state.threatLevel}"><small>Die App empfiehlt nur. Du entscheidest, wann die Lage kippt.</small></label>
      <div class="table-fields">
        ${state.playerNames.map((name, index) => `<label class="field"><span>Reisender ${index + 1}</span><input data-player-index="${index}" type="text" autocomplete="off" autocapitalize="words" placeholder="Name der Figur" value="${escapeHtml(name)}"></label>`).join("")}
      </div>
      <label class="field session-field"><span>Notiz vor der Runde</span><textarea data-session-note rows="3" placeholder="Beziehungen, Grenzen am Tisch oder offene Ideen für den Einstieg …">${escapeHtml(state.sessionNote)}</textarea></label>
    </section>

    <div class="content-grid">
      <section class="content-section notes-section">
        <div class="section-heading"><h2>SL-Notizen</h2><button class="text-button spoiler-toggle" data-action="spoilers" type="button" aria-expanded="${state.spoilersOpen}">${state.spoilersOpen ? "Spoiler schließen" : "Spoiler zeigen"}</button></div>
        ${state.spoilersOpen ? `<ul class="notes-list">${scene.gmNotes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>` : `<p class="quiet-copy">Hinter dem Schalter stehen die internen Hinweise, NPC-Wissen und Spoiler-Handouts.</p>`}
      </section>

      <section class="content-section clue-section">
        <div class="section-heading"><h2>Hinweise</h2><span class="counter">${clues.filter((clue) => state.clues.has(clue.id)).length} / ${clues.length}</span></div>
        ${clues.length ? clues.map((clue) => `<button class="check-row" data-clue="${clue.id}" type="button" aria-pressed="${state.clues.has(clue.id)}"><span class="checkmark">${state.clues.has(clue.id) ? "✓" : ""}</span><span><strong>${escapeHtml(clue.title)}</strong><small>${escapeHtml(clue.details)}</small></span>${clue.required ? `<em>PFLICHT</em>` : ""}</button>`).join("") : `<p class="quiet-copy">Keine Pflicht-Hinweise. Lass die Erscheinung auf die Gruppe reagieren.</p>`}
      </section>
    </div>

    <section class="content-section npc-section">
      <div class="section-heading"><h2>NPCs in dieser Szene</h2><span>${npcs.length ? "Verhalten und Handouts" : "Keine festen NPCs"}</span></div>
      <div class="npc-list">${npcs.length ? npcs.map((npc) => renderNPC(npc, scene.id)).join("") : `<p class="quiet-copy">Der Wald reagiert auf die Gruppe und spricht nicht mit Worten.</p>`}</div>
    </section>

    <section class="content-section dossier-section">
      <div class="section-heading"><h2>Akte</h2><span>${state.manifest.facts.filter((fact) => fact.clueIds.every((id) => state.clues.has(id))).length} / ${state.manifest.facts.length} Schlussfolgerungen</span></div>
      <div class="fact-list">${state.manifest.facts.map((fact) => { const found = fact.clueIds.every((id) => state.clues.has(id)); return `<div class="fact-row ${found ? "is-found" : ""}"><span>${found ? "✓" : "·"}</span><div><strong>${escapeHtml(fact.title)}</strong><small>${escapeHtml(found ? fact.details : "Noch nicht bestätigt")}</small></div></div>`; }).join("")}</div>
    </section>

    ${renderInventorySection()}

    ${soundboard}

    <div class="content-grid lower-grid">
      <section class="content-section handout-section">
        <div class="section-heading"><h2>Handouts</h2><span>Ausgabe am Tisch</span></div>
        <div class="handout-list">${handouts.map((handout) => `<div class="handout-row ${handout.spoiler && !state.spoilersOpen ? "is-locked" : ""}"><span>${handout.spoiler && !state.spoilersOpen ? "🔒" : "▤"}</span><div><strong>${handout.id} · ${escapeHtml(handout.title)}</strong><small>${handout.spoiler && !state.spoilersOpen ? "SL-Spoiler. Erst im Leitstand öffnen." : `${handout.format} · ${escapeHtml(handout.fallback)}`}</small></div></div>`).join("")}</div>
      </section>
      <section class="content-section stuck-section">
        <div class="section-heading"><h2>Wenn sie feststecken</h2><span>Gib nur einen Impuls</span></div>
        <ol class="stuck-list">${scene.stuckPrompts.map((prompt) => `<li>${escapeHtml(prompt)}</li>`).join("")}</ol>
      </section>
    </div>

    <section class="content-section maps-section">
      <div class="section-heading"><h2>Karten</h2><span>Spieler und SL-Ansicht</span></div>
      <div class="map-list">${(state.manifest.maps || []).map((map) => `<figure class="map-card"><img src="./assets/maps/${encodeURIComponent(map.playerAsset)}" alt="${escapeHtml(map.title)}" loading="lazy"><figcaption>${escapeHtml(map.title)} <small>Spielerkarte</small></figcaption></figure>`).join("")}</div>
    </section>

    <section class="content-section scene-note-section" aria-labelledby="scene-note-title">
      <div class="section-heading"><div><h2 id="scene-note-title">Deine Tischnotiz</h2><p>Für Entscheidungen, Aussagen und offene Fäden dieser Szene.</p></div><span class="save-state">speichert lokal</span></div>
      <label class="field"><span class="visually-hidden">Tischnotiz zu ${escapeHtml(scene.title)}</span><textarea data-scene-note="${scene.id}" rows="5" placeholder="Was ist passiert? Wer weiß schon zu viel? Was bleibt offen?">${escapeHtml(state.sceneNotes[scene.id] || "")}</textarea></label>
    </section>

    <section class="checklist-section">
      <div class="section-heading"><h2>Abschluss der Szene</h2><span class="counter">${checklistCount} / ${scene.checklist.length}</span></div>
      <div class="finish-list">${scene.checklist.map((item, index) => { const id = `${scene.id}-${index}`; return `<button class="finish-row" data-check="${id}" type="button" aria-pressed="${state.checklist.has(id)}"><span class="checkmark">${state.checklist.has(id) ? "✓" : ""}</span>${escapeHtml(item)}</button>`; }).join("")}</div>
      <button class="button button-finish" data-action="finish" type="button">${nextScene ? `Szene abschließen · weiter zu ${escapeHtml(nextScene.shortTitle)}` : "Szene abschließen"}</button>
    </section>`;
}

document.addEventListener("click", async (event) => {
  const sceneButton = event.target.closest("[data-scene]");
  if (sceneButton) {
    state.currentSceneId = sceneButton.dataset.scene;
    state.view = state.gmMode ? "guided" : "scene";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    persist();
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  const ratingButton = event.target.closest("[data-rating-cue]");
  if (ratingButton) {
    const cueID = ratingButton.dataset.ratingCue;
    const rating = Number(ratingButton.dataset.rating);
    state.audioRatings[cueID] = rating;
    persist();
    render();
    return;
  }
  const cueButton = event.target.closest("[data-cue-play]");
  if (cueButton) return audio.play(cueById(cueButton.dataset.cuePlay));
  const clueButton = event.target.closest("[data-clue]");
  if (clueButton) return toggleSet(state.clues, clueButton.dataset.clue);
  const checklistButton = event.target.closest("[data-check]");
  if (checklistButton) return toggleSet(state.checklist, checklistButton.dataset.check);
  const hookButton = event.target.closest("[data-hook]");
  if (hookButton) {
    const id = hookButton.dataset.hook;
    if (Object.values(state.selectedHooks).includes(id)) {
      state.selectedHooks = Object.fromEntries(Object.entries(state.selectedHooks).filter(([, value]) => value !== id));
    } else {
      const slot = ["0", "1", "2"].find((key) => !state.selectedHooks[key]);
      if (slot) state.selectedHooks[slot] = id;
    }
    persist();
    render();
    return;
  }
  const action = event.target.closest("[data-action]")?.dataset.action;
  const guideAction = event.target.closest("[data-guide-action]")?.dataset.guideAction;
  if (guideAction === "begin") {
    if (!state.playerNames.every((name) => name.trim())) {
      audioStatus.textContent = "Bitte zuerst alle drei eigenen Figuren benennen.";
      audioStatus.dataset.tone = "warning";
      return;
    }
    state.gmMode = true;
    state.completed.clear();
    state.clues.clear();
    state.checklist.clear();
    state.sceneNotes = {};
    state.sessionNote = "";
    state.nightPhase = 0;
    state.threatLevel = 0;
    state.npcStates = {};
    state.selectedHooks = {};
    state.currentSceneId = "S01";
    state.guidedIndexes = { S01: 0 };
    state.guideHistory = [];
    state.guidedRolls = {};
    state.guidedRollHistory = [];
    state.finaleSuccesses = 0;
    state.finaleFailures = 0;
    state.finaleOutcome = "";
    state.endingID = "";
    resetItemState();
    state.view = "guided";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    persist();
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (guideAction === "back") {
    goBackInGuide();
    return;
  }
  if (guideAction === "advance") {
    if (currentGuideStep(state.currentSceneId)?.id === "S08_NEXT") {
      state.completed.add("S08");
      state.gmMode = false;
      state.view = "home";
      persist();
      render();
      document.querySelector("#scene-content")?.focus();
      return;
    }
    advanceGuideStep();
    persist();
    render();
    return;
  }
  if (guideAction === "read") {
    const cue = cueById(event.target.closest("[data-cue]")?.dataset.cue || "");
    // Start audio without making the guided flow wait for a browser autoplay promise.
    // The cue reports its own success or error in the persistent status line.
    if (cue) void audio.play(cue);
    advanceGuideStep();
    persist();
    render();
    return;
  }
  if (guideAction === "open-roll") {
    state.rollOpen = true;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    return;
  }
  if (guideAction === "close-roll") {
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    return;
  }
  if (guideAction === "resolve-roll") {
    const step = currentGuideStep(state.currentSceneId);
    if (!step?.roll) return;
    const value = Number(document.querySelector("[data-roll-value]")?.value || 1);
    const baseTarget = Number(document.querySelector("[data-roll-target]")?.value || 50);
    if (![value, baseTarget].every((number) => Number.isInteger(number) && number >= 1 && number <= 100)) {
      audioStatus.textContent = "Wurf und Zielwert müssen ganze Zahlen zwischen 1 und 100 sein.";
      audioStatus.dataset.tone = "warning";
      return;
    }
    const target = Math.min(100, baseTarget + activeItemModifier(step));
    const result = evaluateRoll(value, target);
    state.pendingRoll = { stepID: step.id, result, baseTarget };
    state.selectedConsequenceID = "";
    render();
    return;
  }
  if (guideAction === "select-consequence") {
    if (!state.pendingRoll) return;
    state.selectedConsequenceID = event.target.closest("[data-consequence]")?.dataset.consequence || "";
    render();
    return;
  }
  if (guideAction === "select-item-effect") {
    const itemID = event.target.closest("[data-item-id]")?.dataset.itemId;
    const effectID = event.target.closest("[data-effect-id]")?.dataset.effectId;
    if (!itemID || !effectID) return;
    if (state.selectedItemEffectIDs[itemID] === effectID) delete state.selectedItemEffectIDs[itemID];
    else state.selectedItemEffectIDs[itemID] = effectID;
    render();
    return;
  }
  if (guideAction === "confirm-roll") {
    const step = currentGuideStep(state.currentSceneId);
    const pending = state.pendingRoll?.stepID === step?.id ? state.pendingRoll : null;
    if (!step?.roll || !pending) return;
    const result = pending.result;
    const consequences = result.success ? [] : availableRollConsequences(step);
    const consequence = consequences.find((item) => item.id === state.selectedConsequenceID);
    if (!result.success && consequences.length && !consequence) return;
    const itemSelections = selectedItemSelections(step, consequence?.id || "");
    let resolved = true;
    if (step.id === "S07_DANGER") {
      const finale = recordFinaleRoll(result, consequence, itemSelections, pending.baseTarget);
      if (finale.rejected) return;
      resolved = finale.resolved;
    } else {
      if (!recordGuidedRoll(step, result, consequence, itemSelections, pending.baseTarget)) return;
    }
    if (resolved) advanceGuideStep();
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    persist();
    render();
    return;
  }
  const guideOption = event.target.closest("[data-guide-option]");
  if (guideOption) {
    const destination = guideOption.dataset.destination;
    const ending = guideOption.dataset.ending;
    if (ending) {
      state.endingID = ending;
      clearFinaleRolls();
      resetFinaleProgress();
    }
    if (destination) {
      const currentScene = state.currentSceneId;
      const needsConfirmation = state.completed.has(destination);
      if (needsConfirmation && !window.confirm("Gefundene Hinweise und Tischnotizen bleiben erhalten. Spätere Szenen werden ab dem neuen Ziel zurückgesetzt. Pfad neu setzen?")) return;
      state.completed.add(currentScene);
      pushGuidePosition();
      if (needsConfirmation) resetDependentPath(destination);
      state.currentSceneId = destination;
      state.guidedIndexes[destination] = 0;
      state.view = "guided";
    } else {
      advanceGuideStep();
    }
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    persist();
    render();
    return;
  }
  const setupButton = event.target.closest("[data-setup]");
  if (setupButton) {
    toggleSet(state.setupChecks, setupButton.dataset.setup);
    return;
  }
  if (action === "home") {
    state.view = "home";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (action === "guide-back") {
    goBackInGuide();
    return;
  }
  if (action === "menu") {
    const isOpen = topbarMenu.getAttribute("aria-expanded") === "true";
    topbarMenu.setAttribute("aria-expanded", String(!isOpen));
    topbarMenuPanel.hidden = isOpen;
    return;
  }
  if (action === "start" || action === "continue") {
    state.view = action === "start" ? "gm-start" : state.gmMode ? "guided" : "scene";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (action === "table") {
    state.view = "scene";
    render();
    requestAnimationFrame(() => document.querySelector(".table-section")?.scrollIntoView({ behavior: "smooth", block: "start" }));
    return;
  }
  if (action === "materials" || action === "inventory" || action === "rules" || action === "audio-check" || action === "dossier") {
    state.view = "scene";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    const target = { materials: ".handout-section", inventory: ".inventory-section", rules: ".rules-section", "audio-check": ".soundboard", dossier: ".dossier-section" }[action];
    requestAnimationFrame(() => document.querySelector(target)?.scrollIntoView({ behavior: "smooth", block: "start" }));
    return;
  }
  if (action === "motif") {
    const cue = sceneById(state.currentSceneId).audioCueIds.map(cueById).find((item) => item?.category === "music");
    if (cue) await audio.play(cue);
    return;
  }
  if (action === "read-aloud") {
    state.view = "scene";
    state.rollOpen = false;
    state.pendingRoll = null;
    state.selectedConsequenceID = "";
    state.selectedItemEffectIDs = {};
    render();
    requestAnimationFrame(() => document.querySelector(".reading-block")?.scrollIntoView({ behavior: "smooth", block: "start" }));
    return;
  }
  if (action === "spoilers") {
    state.spoilersOpen = !state.spoilersOpen;
    render();
  }
  if (action === "night-previous") {
    state.nightPhase = Math.max(0, state.nightPhase - 1);
    persist();
    render();
  }
  if (action === "night-next") {
    state.nightPhase = Math.min(nightPhases.length - 1, state.nightPhase + 1);
    persist();
    render();
  }
  if (action === "preset") await audio.playPreset(sceneById(state.currentSceneId).audioCueIds.map(cueById).filter(Boolean));
  if (action === "finish") {
    const scene = sceneById(state.currentSceneId);
    state.completed.add(scene.id);
    if (scene.nextSceneIds[0]) state.currentSceneId = scene.nextSceneIds[0];
    persist();
    render();
  }
  if (action === "clear-table") {
    const shouldClear = window.confirm("Tischdaten löschen? Namen und eigene Notizen werden nur auf diesem Gerät entfernt.");
    if (!shouldClear) return;
    state.playerNames = ["", "", ""];
    state.sessionNote = "";
    state.sceneNotes = {};
    persist();
    render();
  }
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-item-owner]")) {
    const itemID = event.target.dataset.itemOwner;
    if (event.target.value === "") delete state.itemOwners[itemID];
    else state.itemOwners[itemID] = Number(event.target.value);
    persist();
    render();
  }
});

document.addEventListener("input", (event) => {
  if (event.target.matches("[data-volume]")) audio.setVolume(event.target.dataset.volume, event.target.value);
  if (event.target.matches("[data-player-index]")) {
    state.playerNames[Number(event.target.dataset.playerIndex)] = event.target.value;
    persist();
    const startButton = document.querySelector("[data-guide-action=begin]");
    if (startButton) startButton.disabled = !state.playerNames.every((name) => name.trim());
    const startHint = document.querySelector(".guide-start-hint");
    if (startHint) startHint.hidden = state.playerNames.every((name) => name.trim());
  }
  if (event.target.matches("[data-session-note]")) {
    state.sessionNote = event.target.value;
    persist();
  }
  if (event.target.matches("[data-scene-note]")) {
    state.sceneNotes[event.target.dataset.sceneNote] = event.target.value;
    persist();
  }
  if (event.target.matches("[data-night-phase]")) {
    state.nightPhase = normalizedNightPhase(event.target.value);
    persist();
    render();
  }
  if (event.target.matches("[data-threat]")) {
    state.threatLevel = Math.min(5, Math.max(0, Number(event.target.value)));
    persist();
    render();
  }
  if (event.target.matches("[data-npc-state]")) {
    state.npcStates[event.target.dataset.npcState] = Number(event.target.value);
    persist();
  }
});

document.querySelector("#stop-all").addEventListener("click", () => audio.stopAll());
document.querySelector("#transport-stop").addEventListener("click", () => audio.stopAll());
document.querySelector("#audio-test").addEventListener("click", () => audio.testTone());
document.querySelector("#reset-progress").addEventListener("click", () => {
  state.completed.clear(); state.clues.clear(); state.checklist.clear(); state.setupChecks.clear(); state.guidedIndexes = {}; state.guideHistory = []; state.guidedRolls = {}; state.guidedRollHistory = []; state.finaleSuccesses = 0; state.finaleFailures = 0; state.finaleOutcome = ""; state.pendingRoll = null; state.selectedConsequenceID = ""; resetItemState(); state.gmMode = false; state.endingID = ""; state.currentSceneId = "S01"; state.view = "home"; persist(); render();
  audioStatus.textContent = "Fortschritt zurückgesetzt.";
});

async function boot() {
  app.replaceChildren(document.querySelector("#loading-template").content.cloneNode(true));
  try {
    const response = await fetch("./data/manifest.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.manifest = await response.json();
    const hasInventoryData = ["kraehenfels.discoveredItemIDs", "kraehenfels.itemOwners", "kraehenfels.itemUseRecords"].some((key) => localStorage.getItem(key) !== null);
    if (state.gmMode && !hasInventoryData) {
      discoverItems();
      persist();
    }
    nightPhases = (state.manifest.phases || []).map((phase, index) => ({ ...phase, symbol: phaseSymbols[index] || "•" }));
    state.nightPhase = normalizedNightPhase(state.nightPhase);
    if (!sceneById(state.currentSceneId)) state.currentSceneId = state.manifest.scenes[0].id;
    render();
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./service-worker.js").catch(() => undefined);
  } catch (error) {
    app.innerHTML = `<section class="error-state"><h2>Leitstand konnte nicht starten</h2><p>Starte den lokalen Server über die Anleitung in <code>web/README.md</code>. Die App braucht einen Server, damit sie Inhalte und Audio laden kann.</p></section>`;
  }
}

boot();
