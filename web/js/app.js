import { AudioEngine } from "./audio-engine.js";
import { evaluateRoll, guideKindLabels } from "./guided-flow.js?v=4.0.0-r11";

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

function normalizedTrack(value, maximum = 5) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.min(Math.max(Math.trunc(number), 0), maximum) : 0;
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
  detail: null,
  detailStack: [],
  detailReturnView: "home",
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
  time: normalizedTrack(localStorage.getItem("kraehenfels.time"), 5),
  warmth: normalizedTrack(localStorage.getItem("kraehenfels.warmth") ?? 3, 5),
  trust: normalizedTrack(localStorage.getItem("kraehenfels.trust") ?? 3, 5),
  injuries: normalizedTrack(localStorage.getItem("kraehenfels.injuries"), 3),
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
  finaleMode: localStorage.getItem("kraehenfels.finaleMode") === "combat" ? "combat" : "guided",
  combatState: stored("kraehenfels.combatState", null),
  audioRatings: stored("kraehenfels.audioRatings", {}),
  endingID: localStorage.getItem("kraehenfels.endingID") || "",
  rollOpen: false,
  pendingRoll: null,
  selectedConsequenceID: "",
  selectedItemEffectIDs: {},
  sessionSchema: localStorage.getItem("kraehenfels.sessionSchema") || "",
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
  localStorage.setItem("kraehenfels.time", String(state.time));
  localStorage.setItem("kraehenfels.warmth", String(state.warmth));
  localStorage.setItem("kraehenfels.trust", String(state.trust));
  localStorage.setItem("kraehenfels.injuries", String(state.injuries));
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
  localStorage.setItem("kraehenfels.finaleMode", state.finaleMode);
  if (state.combatState) localStorage.setItem("kraehenfels.combatState", JSON.stringify(state.combatState));
  else localStorage.removeItem("kraehenfels.combatState");
  localStorage.setItem("kraehenfels.sessionSchema", "v7");
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
    const available = canEnterScene(scene.id);
    return `<button class="scene-link ${active ? "is-active" : ""} ${available ? "" : "is-locked"}" data-scene="${scene.id}" type="button" aria-current="${active ? "page" : "false"}" ${available ? "" : "disabled"}>
      <span class="scene-link-id">${scene.id}</span>
      <span class="scene-link-copy"><strong>${escapeHtml(scene.shortTitle)}</strong><small>${escapeHtml(scene.duration)}</small></span>
      <span class="scene-link-state" aria-label="${complete ? "abgeschlossen" : available ? "offen" : "gesperrt"}">${complete ? "✓" : available ? "›" : "🔒"}</span>
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
      ${npc.givesHandoutIds?.length ? `<div class="gives-handout"><span>GIBT</span><div class="npc-handout-links">${npc.givesHandoutIds.map(guideReferenceMarkup).join("")}</div></div>` : ""}
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
  const detailItem = state.detail?.kind === "handout" ? handoutById(state.detail.id) : state.detail?.kind === "clue" ? clueById(state.detail.id) : null;
  const backLabel = view === "guided" ? (state.guideHistory.length ? "Zurück" : "Übersicht") : view === "detail" ? "Zurück" : "Krähenfels";
  topbarBack.dataset.action = view === "guided" ? "guide-back" : view === "detail" ? "detail-back" : "home";
  topbarBack.querySelector("span:last-child").textContent = backLabel;
  topbarBack.setAttribute("aria-label", view === "detail" ? "Zur vorherigen Ansicht" : backLabel === "Zurück" ? "Zum vorherigen Spielleiterschritt" : `Zur ${backLabel}`);
  screenTitle.textContent = isHome ? "Krähenfels" : view === "gm-start" ? "Spielleiter-Modus" : view === "detail" ? detailItem ? `${detailItem.id} · ${detailItem.title}` : "Detail" : scene.shortTitle;
  document.body.dataset.view = view;
  topbarMenuPanel.hidden = true;
  topbarMenu.setAttribute("aria-expanded", "false");
}

function guideStepsFor(sceneID) {
  const steps = state.manifest?.guide?.steps?.[sceneID] || [];
  if (sceneID !== "S07") return steps;
  return state.finaleMode === "combat"
    ? steps.filter((step) => step.id !== "S07_DANGER")
    : steps.filter((step) => step.id !== "S07_COMBAT");
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

function migrateActiveLegacySession() {
  const preservedNames = [...state.playerNames];
  const preservedSessionNote = state.sessionNote;
  const preservedSceneNotes = { ...state.sceneNotes };
  state.gmMode = true;
  state.playerNames = preservedNames;
  state.sessionNote = preservedSessionNote;
  state.sceneNotes = preservedSceneNotes;
  state.currentSceneId = "S06";
  state.completed = new Set(["S01", "S02", "S03", "S04", "S05"]);
  state.clues = new Set();
  state.checklist = new Set();
  state.npcStates = {};
  state.selectedHooks = {};
  state.setupChecks = new Set();
  state.guidedIndexes = { S06: 0 };
  state.guideHistory = [];
  state.guidedRolls = {};
  state.guidedRollHistory = [];
  state.finaleSuccesses = 0;
  state.finaleFailures = 0;
  state.finaleOutcome = "";
  state.finaleMode = "guided";
  state.combatState = null;
  state.endingID = "";
  state.time = 0;
  state.warmth = 3;
  state.trust = 3;
  state.injuries = 0;
  resetItemState();
  persist();
}

function currentGuideIndex(sceneID) {
  const steps = guideStepsFor(sceneID);
  return Math.min(Math.max(Number(state.guidedIndexes[sceneID] || 0), 0), Math.max(0, steps.length - 1));
}

function currentGuideStep(sceneID) {
  return guideStepsFor(sceneID)[currentGuideIndex(sceneID)];
}

function optionAvailable(option) {
  const required = option?.requiresCompletedSceneIDs || [];
  return required.every((sceneID) => state.completed.has(sceneID) || sceneID === state.currentSceneId);
}

function canEnterScene(sceneID, includeCurrent = false) {
  const completed = (id) => state.completed.has(id) || (includeCurrent && id === state.currentSceneId);
  if (sceneID === state.currentSceneId || state.completed.has(sceneID)) return true;
  if (sceneID === "S01") return true;
  if (sceneID === "S02") return completed("S01");
  if (["S03", "S04", "S05"].includes(sceneID)) return completed("S02");
  if (sceneID === "S06") return ["S03", "S04", "S05"].every(completed);
  if (sceneID === "S07") return completed("S06");
  if (sceneID === "S08") return completed("S07");
  return false;
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
  const parts = [];
  const delta = (key, label) => {
    if (!Number.isFinite(Number(effect[key]))) return;
    const value = Number(effect[key]);
    parts.push(`${label} ${value >= 0 ? "+" : ""}${value}`);
  };
  delta("threatDelta", "Dorfspannung");
  if (Number.isFinite(Number(effect.minimumThreat))) parts.push(`Dorfspannung mindestens ${Number(effect.minimumThreat)}`);
  delta("timeDelta", "Zeit");
  delta("warmthDelta", "Wärme");
  delta("trustDelta", "Vertrauen");
  delta("injuryDelta", "Verletzungen");
  return parts.join(" · ");
}

function applyConsequence(consequence) {
  const effect = consequence?.effect || {};
  if (Number.isFinite(Number(effect.threatDelta))) {
    state.threatLevel = Math.min(5, Math.max(0, state.threatLevel + Number(effect.threatDelta)));
  }
  if (Number.isFinite(Number(effect.minimumThreat))) {
    state.threatLevel = Math.min(5, Math.max(state.threatLevel, Number(effect.minimumThreat)));
  }
  const delta = (key, property, maximum) => {
    if (!Number.isFinite(Number(effect[key]))) return;
    state[property] = normalizedTrack(state[property] + Number(effect[key]), maximum);
  };
  delta("timeDelta", "time", 5);
  delta("warmthDelta", "warmth", 5);
  delta("trustDelta", "trust", 5);
  delta("injuryDelta", "injuries", 3);
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

function ensureCombat() {
  const config = state.manifest?.guide?.combat;
  if (!config?.enemy) return null;
  if (state.combatState && state.combatState.endingID === state.endingID) return state.combatState;
  const spentShots = state.itemUseRecords.filter((record) => record.itemID === "item-revolver").length;
  const participants = state.playerNames.map((name, index) => ({
    id: `player-${index}`,
    name: name.trim() || `Figur ${index + 1}`,
    kind: "player",
    maxLP: 100,
    currentLP: 100,
    initiative: 0,
    attackSkill: 50,
    damageDice: "1W10",
    ammunition: Number(state.itemOwners["item-revolver"]) === index ? Math.max(0, 3 - spentShots) : 0,
    geistesblitze: 0,
    parryable: true,
    hasActed: false,
  }));
  participants.push({
    id: config.enemy.id,
    name: config.enemy.name,
    kind: "enemy",
    maxLP: Number(config.enemy.maxLP) || 120,
    currentLP: Number(config.enemy.maxLP) || 120,
    initiative: Number(config.enemy.initiative) || 7,
    attackSkill: Number(config.enemy.attackSkill) || 65,
    damageDice: config.enemy.damageDice || "7W10",
    ammunition: 0,
    geistesblitze: 0,
    parryable: Boolean(config.enemy.parryable),
    hasActed: false,
  });
  state.combatState = {
    isActive: true,
    round: 1,
    turnIndex: 0,
    endingID: state.endingID || "",
    participants,
    log: [`Kampf gestartet · ${config.enemy.name} · Ziel: ${state.endingID || "unbekanntes Ende"}`],
    outcome: null,
  };
  persist();
  return state.combatState;
}

function combatParticipant(id) {
  return state.combatState?.participants?.find((participant) => participant.id === id);
}

function updateCombatParticipant(id, updater) {
  if (!state.combatState) return;
  const participants = state.combatState.participants.map((participant) => {
    if (participant.id !== id) return participant;
    const next = { ...participant };
    updater(next);
    next.currentLP = Math.min(Math.max(Math.trunc(Number(next.currentLP) || 0), 0), next.maxLP);
    next.initiative = Math.max(0, Math.trunc(Number(next.initiative) || 0));
    next.ammunition = Math.max(0, Math.trunc(Number(next.ammunition) || 0));
    next.geistesblitze = Math.max(0, Math.trunc(Number(next.geistesblitze) || 0));
    return next;
  });
  state.combatState = { ...state.combatState, participants };
  persist();
  render();
}

function sortCombatByInitiative() {
  if (!state.combatState) return;
  const participants = [...state.combatState.participants].sort((a, b) => {
    if (a.initiative === b.initiative) return a.kind === "player" && b.kind !== "player" ? -1 : 1;
    return b.initiative - a.initiative;
  }).map((participant) => ({ ...participant, hasActed: false }));
  state.combatState = { ...state.combatState, participants, turnIndex: 0, log: [...state.combatState.log, "Initiative sortiert"].slice(-100) };
  persist();
  render();
}

function nextCombatTurn() {
  const current = state.combatState;
  if (!current?.isActive || !current.participants.length) return;
  const participants = current.participants.map((participant) => ({ ...participant }));
  const safeIndex = participants.findIndex((participant, index) => index === current.turnIndex && participant.currentLP > 0);
  const currentIndex = safeIndex >= 0 ? safeIndex : Math.max(0, current.turnIndex);
  if (participants[currentIndex]) participants[currentIndex].hasActed = true;
  let nextIndex = participants.findIndex((participant, index) => index > currentIndex && participant.currentLP > 0);
  let round = current.round;
  let log = [...current.log];
  if (nextIndex < 0) {
    round += 1;
    participants.forEach((participant) => { participant.hasActed = false; });
    nextIndex = participants.findIndex((participant) => participant.currentLP > 0);
    log.push(`Runde ${round} beginnt`);
  }
  state.combatState = { ...current, participants, round, turnIndex: nextIndex >= 0 ? nextIndex : 0, log: log.slice(-100) };
  persist();
  render();
}

function finishCombat(outcome) {
  if (!state.combatState || state.combatState.outcome) return;
  state.combatState = {
    ...state.combatState,
    isActive: false,
    outcome,
    log: [...state.combatState.log, `Kampf beendet · ${outcome}`].slice(-100),
  };
  persist();
  render();
}

function setFinaleMode(mode) {
  const nextMode = mode === "combat" ? "combat" : "guided";
  if (state.finaleMode === nextMode) return;
  state.finaleMode = nextMode;
  clearFinaleRolls();
  resetFinaleProgress();
  state.combatState = null;
  state.guidedIndexes.S07 = Math.min(currentGuideIndex("S07"), Math.max(0, guideStepsFor("S07").length - 1));
  persist();
  render();
}

function pushGuidePosition() {
  state.guideHistory.push({ sceneID: state.currentSceneId, stepIndex: currentGuideIndex(state.currentSceneId) });
}

function advanceGuideStep() {
  const steps = guideStepsFor(state.currentSceneId);
  const step = currentGuideStep(state.currentSceneId);
  if (step?.id === "S01_DISTRIBUTE" && !distributionComplete()) return false;
  if (step?.id === "S07_COMBAT" && !state.combatState?.outcome) return false;
  if (step?.id === "S01_ITEMS") discoverItems();
  [step?.clueID, ...(step?.clueIDs || [])].filter(Boolean).forEach((clueID) => state.clues.add(clueID));
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
    state.combatState = null;
    state.finaleMode = "guided";
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

function clearDetailNavigation() {
  state.detail = null;
  state.detailStack = [];
  state.detailReturnView = state.view === "detail" ? (state.gmMode ? "guided" : "scene") : state.view;
}

function openDetail(kind, id) {
  const item = kind === "handout" ? handoutById(id) : clueById(id);
  if (!item) return;
  if (state.view === "detail" && state.detail) {
    state.detailStack.push(state.detail);
  } else {
    state.detailReturnView = state.view;
    state.detailStack = [];
  }
  state.detail = { kind, id };
  state.view = "detail";
  render();
  document.querySelector("#scene-content")?.focus();
}

function closeDetail() {
  if (state.detailStack.length) {
    state.detail = state.detailStack.pop();
  } else {
    state.detail = null;
    state.view = state.detailReturnView || (state.gmMode ? "guided" : "scene");
    state.detailReturnView = "home";
  }
  render();
  document.querySelector("#scene-content")?.focus();
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

function guideReferenceMarkup(id) {
  const label = escapeHtml(guideReference(id));
  if (handoutById(id)) return `<button class="guide-reference" data-open-handout="${escapeHtml(id)}" type="button">${label}<span aria-hidden="true">›</span></button>`;
  if (clueById(id)) return `<button class="guide-reference" data-open-clue="${escapeHtml(id)}" type="button">${label}<span aria-hidden="true">›</span></button>`;
  return `<span class="guide-reference">${label}</span>`;
}

function guideReferences(step) {
  const ids = [...new Set([
    step.handoutID,
    ...(step.handoutIDs || []),
    step.clueID,
    ...(step.clueIDs || []),
    step.npcID,
    ...(step.npcIDs || []),
  ].filter(Boolean))];
  if (!ids.length) return "";
  return `<div class="guide-references"><span class="eyebrow">Direkt griffbereit</span><div>${ids.map(guideReferenceMarkup).join("")}</div></div>`;
}

function renderDetailBackButton() {
  return `<button class="button button-quiet detail-back" data-action="detail-back" type="button"><span aria-hidden="true">←</span> Zurück</button>`;
}

function renderHandoutDetail(handout) {
  const locked = Boolean(handout.spoiler && !state.spoilersOpen);
  const linkedClues = (handout.linkedClueIds || []).map(clueById).filter(Boolean);
  const preview = !locked && handout.previewAsset
    ? `<figure class="detail-preview"><img src="./assets/materials/handouts/${encodeURIComponent(handout.previewAsset)}" alt="Vorschau: ${escapeHtml(handout.title)}" loading="eager"><figcaption>Spieleransicht · ${escapeHtml(handout.format)}</figcaption></figure>`
    : "";
  const linkedCluesMarkup = !locked && linkedClues.length
    ? `<section class="detail-panel" aria-labelledby="detail-linked-clues"><div class="section-heading"><div><h2 id="detail-linked-clues">Verknüpfte Hinweise</h2><p>Diese Informationen gehören zu diesem Handout.</p></div><span>${linkedClues.length}</span></div><div class="detail-link-list">${linkedClues.map((clue) => `<button class="detail-link" data-open-clue="${escapeHtml(clue.id)}" type="button"><span><strong>${escapeHtml(clue.id)} · ${escapeHtml(clue.title)}</strong><small>${state.clues.has(clue.id) ? "als gefunden markiert" : "noch nicht markiert"}</small></span><span aria-hidden="true">›</span></button>`).join("")}</div></section>`
    : "";
  return `<div class="detail-view handout-detail">
    ${renderDetailBackButton()}
    <section class="detail-heading" aria-labelledby="detail-title">
      <div class="detail-heading-meta"><span class="eyebrow">${handout.spoiler ? "SL-SPOILER" : "SPIELERHANDOUT"}</span><span>${escapeHtml(handout.id)}</span></div>
      <h1 id="detail-title">${escapeHtml(handout.title)}</h1>
      <p>${escapeHtml(handout.format)}</p>
    </section>
    ${locked ? `<section class="detail-locked" aria-live="polite"><strong>Dieses Handout bleibt bis zum Spoiler-Schalter verborgen.</strong><p>Öffne zuerst „Spoiler zeigen“, wenn du den Inhalt für die Spielleitung brauchst.</p><button class="button button-quiet" data-action="spoilers" type="button">Spoiler zeigen</button></section>` : `${preview}<section class="detail-panel" aria-labelledby="detail-fallback-title"><div class="section-heading"><div><h2 id="detail-fallback-title">Papier-Fallback</h2><p>Wenn das gedruckte Stück fehlt, gib genau diese Information weiter.</p></div></div><p class="detail-copy">${escapeHtml(handout.fallback)}</p>${handout.asset ? `<small class="detail-meta">Druckreferenz: ${escapeHtml(handout.asset)}</small>` : ""}</section>`}
    ${linkedCluesMarkup}
  </div>`;
}

function renderClueDetail(clue) {
  const handout = clue.handoutId ? handoutById(clue.handoutId) : null;
  const fact = clue.factId ? state.manifest.facts.find((entry) => entry.id === clue.factId) : null;
  const found = state.clues.has(clue.id);
  return `<div class="detail-view clue-detail">
    ${renderDetailBackButton()}
    <section class="detail-heading" aria-labelledby="detail-title">
      <div class="detail-heading-meta"><span class="eyebrow">HINWEIS${clue.required ? " · PFLICHT" : ""}</span><span>${escapeHtml(clue.id)}</span></div>
      <h1 id="detail-title">${escapeHtml(clue.title)}</h1>
      <p>${found ? "Dieser Hinweis ist am Tisch bereits als gefunden markiert." : "Prüfe den Hinweis am Tisch und markiere ihn erst danach als gefunden."}</p>
    </section>
    <section class="detail-panel" aria-labelledby="clue-detail-title"><div class="section-heading"><div><h2 id="clue-detail-title">Was die Gruppe erfährt</h2><p>Diese Formulierung bleibt spielbar und eindeutig.</p></div></div><p class="detail-copy">${escapeHtml(clue.details)}</p><button class="button ${found ? "button-quiet" : "button-primary"} detail-toggle" data-clue="${escapeHtml(clue.id)}" type="button" aria-pressed="${found}">${found ? "Als offen markieren" : "Als gefunden markieren"}</button></section>
    ${handout ? `<section class="detail-panel" aria-labelledby="clue-handout-title"><div class="section-heading"><div><h2 id="clue-handout-title">Dazugehöriges Handout</h2><p>Öffne das Material, ohne den Fortschritt zu verlassen.</p></div></div><button class="detail-link" data-open-handout="${escapeHtml(handout.id)}" type="button"><span><strong>${escapeHtml(handout.id)} · ${escapeHtml(handout.title)}</strong><small>${escapeHtml(handout.format)}</small></span><span aria-hidden="true">›</span></button></section>` : ""}
    ${fact ? `<section class="detail-panel" aria-labelledby="clue-fact-title"><div class="section-heading"><div><h2 id="clue-fact-title">Akte</h2><p>Diese Schlussfolgerung wird mit den verknüpften Hinweisen bestätigt.</p></div></div><p class="detail-copy">${escapeHtml(fact.title)}</p></section>` : ""}
  </div>`;
}

function renderDetailView() {
  const detail = state.detail;
  if (!detail) return `<div class="detail-view"><p class="quiet-copy">Keine Detailansicht geöffnet.</p>${renderDetailBackButton()}</div>`;
  const item = detail.kind === "handout" ? handoutById(detail.id) : clueById(detail.id);
  if (!item) return `<div class="detail-view"><p class="quiet-copy">Dieses Material ist nicht mehr verfügbar.</p>${renderDetailBackButton()}</div>`;
  return detail.kind === "handout" ? renderHandoutDetail(item) : renderClueDetail(item);
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

function renderGuideState() {
  const track = (key, label, maximum, value) => `<label class="guide-state-control"><span>${label} <b>${value}/${maximum}</b></span><input data-state="${key}" type="range" min="0" max="${maximum}" step="1" value="${value}" aria-label="${label}"></label>`;
  return `<section class="guide-state-panel" aria-label="Lage im Blick"><div class="section-heading"><h3>Lage im Blick</h3><span>wird mit Konsequenzen geführt</span></div><div class="guide-state-grid">${track("time", "Zeit", 5, state.time)}${track("warmth", "Wärme", 5, state.warmth)}${track("trust", "Vertrauen", 5, state.trust)}${track("injuries", "Verletzungen", 3, state.injuries)}</div></section>`;
}

function renderFinaleModePicker() {
  return `<div class="finale-mode-picker"><span class="eyebrow">FINALE-MODUS</span><div class="finale-mode-options"><button class="mode-option ${state.finaleMode === "guided" ? "is-selected" : ""}" data-guide-action="finale-mode" data-mode="guided" type="button" aria-pressed="${state.finaleMode === "guided"}"><strong>Geführte Gefahrenszene</strong><small>Zwei Erfolge vor zwei Fehlschlägen.</small></button><button class="mode-option ${state.finaleMode === "combat" ? "is-selected" : ""}" data-guide-action="finale-mode" data-mode="combat" type="button" aria-pressed="${state.finaleMode === "combat"}"><strong>Voller Kampf</strong><small>Initiative, LP, Angriff und Parade am Tisch.</small></button></div></div>`;
}

function renderGuideNPCs(step) {
  const ids = [...new Set([step.npcID, ...(step.npcIDs || [])].filter(Boolean))];
  if (!ids.length) return "";
  const entries = ids.map((id) => {
    const npc = npcById(id);
    if (!npc) return "";
    const appearance = npc.appearances?.find((entry) => entry.sceneId === step.sceneID);
    if (!appearance) return "";
    return `<article class="guide-npc-entry"><div class="guide-npc-heading"><strong>${escapeHtml(npc.name)}</strong><span>${escapeHtml(npc.role)}</span></div><p><b>AUFTRITT</b> ${escapeHtml(appearance.when)}</p><p><b>SO SPIELEN</b> ${escapeHtml(appearance.playAs)}</p><blockquote>„${escapeHtml(appearance.openingLine)}“</blockquote><p><b>DANACH</b> ${escapeHtml(appearance.turn)}</p></article>`;
  }).filter(Boolean).join("");
  return entries ? `<section class="guide-npcs"><div class="section-heading"><h3>Jetzt relevante NPCs</h3><span>nur dieser Schritt</span></div>${entries}</section>` : "";
}

function combatStatusLabel(participant) {
  if (participant.currentLP <= 0) return "ausgeschaltet";
  if (participant.currentLP < 10) return "bewusstlos";
  if (participant.currentLP < participant.maxLP / 2) return "angeschlagen";
  return "handlungsfähig";
}

function renderCombatTracker() {
  const combat = ensureCombat();
  if (!combat) return `<div class="combat-empty">Keine Kampfkonfiguration geladen.</div>`;
  const currentID = combat.participants[combat.turnIndex]?.id;
  const participants = combat.participants.map((participant) => `<article class="combat-participant ${participant.id === currentID ? "is-current" : ""} ${participant.currentLP <= 0 ? "is-defeated" : ""}">
    <div class="combat-participant-heading"><strong>${escapeHtml(participant.name)}</strong><span>${participant.kind === "enemy" ? "Gegner" : "Spielerfigur"}</span><b>${escapeHtml(combatStatusLabel(participant))}</b></div>
    <div class="combat-fields"><label>LP<input data-combat-field="currentLP" data-combat-id="${escapeHtml(participant.id)}" type="number" min="0" max="${participant.maxLP}" value="${participant.currentLP}"></label><label>Initiative<input data-combat-field="initiative" data-combat-id="${escapeHtml(participant.id)}" type="number" min="0" max="30" value="${participant.initiative}"></label><label>Geistesblitze<input data-combat-field="geistesblitze" data-combat-id="${escapeHtml(participant.id)}" type="number" min="0" max="9" value="${participant.geistesblitze}"></label>${participant.kind === "player" ? `<label>Patronen<input data-combat-field="ammunition" data-combat-id="${escapeHtml(participant.id)}" type="number" min="0" max="12" value="${participant.ammunition}"></label>` : ""}</div>
    <div class="combat-participant-actions"><button class="button button-quiet" data-combat-action="log-attack" data-combat-id="${escapeHtml(participant.id)}" type="button">Angriff notieren</button>${participant.parryable ? `<button class="button button-quiet" data-combat-action="log-parry" data-combat-id="${escapeHtml(participant.id)}" type="button">Parade</button>` : ""}${participant.kind === "player" && participant.ammunition > 0 ? `<button class="button button-quiet" data-combat-action="spend-ammo" data-combat-id="${escapeHtml(participant.id)}" type="button">Schuss abstreichen</button>` : ""}</div>
  </article>`).join("");
  const outcome = combat.outcome
    ? `<div class="combat-outcome ${combat.outcome === "victory" ? "is-victory" : "is-defeat"}"><strong>${combat.outcome === "victory" ? "Sieg bestätigt" : "Niederlage bestätigt"}</strong>${state.endingID && state.manifest.guide.combat?.victoryByEnding?.[state.endingID] ? `<p>${escapeHtml(state.manifest.guide.combat.victoryByEnding[state.endingID])}</p>` : ""}<small>Schließe den Tracker und bestätige danach den Schritt „Zum Nachhall“.</small></div>`
    : `<div class="combat-result-actions"><button class="button button-primary" data-combat-action="finish" data-outcome="victory" type="button">Sieg bestätigen</button><button class="button button-quiet" data-combat-action="finish" data-outcome="defeat" type="button">Niederlage bestätigen</button></div>`;
  return `<div class="combat-tracker"><div class="combat-toolbar"><span class="eyebrow">RUNDE ${combat.round}</span><span>Am Zug: <b>${escapeHtml(combat.participants[combat.turnIndex]?.name || "—")}</b></span><button class="button button-quiet" data-combat-action="sort" type="button">Initiative sortieren</button><button class="button button-primary" data-combat-action="next" type="button" ${combat.isActive ? "" : "disabled"}>Nächster Zug</button></div><div class="combat-participants">${participants}</div><div class="combat-log"><div class="combat-log-input"><input data-combat-log type="text" placeholder="Ereignis notieren …"><button class="button button-quiet" data-combat-action="log" type="button">Eintragen</button></div>${combat.log.slice(-10).reverse().map((entry) => `<p>${escapeHtml(entry)}</p>`).join("")}</div>${outcome}</div>`;
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
  const allOptions = step.options || [];
  const options = allOptions.filter(optionAvailable);
  let action = "";
  if (step.id === "S07_COMBAT") action = `${renderCombatTracker()}${state.combatState?.outcome ? `<button class="button button-primary guide-action" data-guide-action="advance" type="button">Zum Nachhall weiter<span aria-hidden="true">›</span></button>` : ""}`;
  else if (step.roll) action = renderRollPanel(step);
  else if (allOptions.length) action = options.length ? `<div class="guide-options">${options.map((option) => `<button class="guide-option" data-guide-option="${option.id}" data-destination="${option.destinationSceneID || ""}" data-ending="${option.endingID || ""}" type="button"><strong>${escapeHtml(option.title)}</strong><small>${escapeHtml(option.detail)}</small><span aria-hidden="true">›</span></button>`).join("")}</div>` : `<p class="guide-locked-option">Noch keine Option freigeschaltet. Schließe zuerst die erforderlichen Ermittlungsorte ab.</p>`;
  else if (step.kind === "readAloud") action = `<button class="button button-primary guide-action" data-guide-action="read" data-cue="${cue?.id || ""}" type="button">${cue ? "Sound vorbereiten und vorlesen" : "Vorgelesen – weiter"}<span aria-hidden="true">›</span></button>`;
  else if (step.kind === "itemDistribution") action = `<button class="button button-primary guide-action" data-guide-action="advance" type="button" ${distributionComplete() ? "" : "disabled"}>${escapeHtml(step.actionLabel || "Verteilung abschließen")}<span aria-hidden="true">›</span></button>`;
  else if (step.kind === "clue" && [step.handoutID, ...(step.handoutIDs || [])].filter(Boolean).length) {
    const handoutIDs = [...new Set([step.handoutID, ...(step.handoutIDs || [])].filter(Boolean))];
    action = `<div class="guide-action-stack">${handoutIDs.map((id) => `<button class="button button-primary guide-action" data-open-handout="${escapeHtml(id)}" type="button">${escapeHtml(step.actionLabel || `${id} zeigen`)}<span aria-hidden="true">↗</span></button>`).join("")}<button class="button button-quiet guide-action" data-guide-action="advance" type="button">Handout gezeigt · weiter<span aria-hidden="true">›</span></button></div>`;
  }
  else action = `<button class="button button-primary guide-action" data-guide-action="advance" type="button">${escapeHtml(step.actionLabel || "Weiter")}<span aria-hidden="true">›</span></button>`;
  const clueLine = [step.clueID, ...(step.clueIDs || [])].filter(Boolean).length ? `<div class="guide-clue-note"><span>HINWEIS</span> Dieser Hinweis ist garantiert und darf nicht an einem Würfelwurf scheitern.</div>` : "";
  const itemPanel = step.kind === "itemSearch" ? renderItemFindings() : step.kind === "itemDistribution" ? renderItemDistribution() : "";
  return `<div class="guided-scene-view">
    <div class="guide-progress-row"><span>SCHRITT ${index + 1} VON ${steps.length}</span><b>${escapeHtml(scene.shortTitle)}</b></div>
    <div class="guide-progress-track"><i style="width:${((index + 1) / Math.max(1, steps.length)) * 100}%"></i></div>
    <section class="guide-scene-hero" style="--scene-art: url('./assets/art/${encodeURIComponent(scene.art)}')"><div><span>${escapeHtml(scene.id)} · ${escapeHtml(scene.duration)}</span><h2>${escapeHtml(scene.title)}</h2><p>${escapeHtml(scene.goal)}</p></div></section>
    ${renderGuideState()}
    <section class="guide-step-card kind-${step.kind}">
      <div class="guide-kind"><span>${escapeHtml(guideKindLabels[step.kind] || "SPIELLEITER-SCHRITT")}</span>${step.roll?.required ? "<b>PFLICHT</b>" : ""}</div>
      <h2>${escapeHtml(step.title)}</h2>
      <p class="guide-step-body">${escapeHtml(step.body)}</p>
      ${step.id === "S07_GM" ? renderFinaleModePicker() : ""}
      ${step.roll ? `<div class="roll-brief"><span class="eyebrow">WANN WIRD GEWÜRFELT?</span><strong>${escapeHtml(step.roll.actor)}</strong><p>${escapeHtml(step.roll.ability)} · ${escapeHtml(step.roll.target)}</p><small>${escapeHtml(step.roll.modifier)}</small></div>` : ""}
      ${step.id === "S07_DANGER" ? renderFinaleProgress() : ""}
      ${clueLine}${itemPanel}${renderGuideNPCs(step)}${guideReferences(step)}
      ${action}
    </section>
    <div class="guide-footer">
      <button class="button button-quiet" data-guide-action="back" type="button"><span aria-hidden="true">←</span> ${state.guideHistory.length ? "Zurück" : "Übersicht"}</button>
      <span>${allOptions.length ? "Wähle oben den nächsten Schritt." : "Der nächste Schritt bleibt unten sichtbar."}</span>
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
        const available = canEnterScene(item.id);
        const gmJump = available && item.id !== "S01" && !complete;
        return `<button class="home-scene-row ${item.id === scene.id ? "is-current" : ""} ${available ? "" : "is-locked"}" data-scene="${item.id}" type="button" ${available ? "" : "disabled"}><span class="home-scene-id">${item.id}</span><span class="home-scene-copy"><strong>${escapeHtml(item.title)}</strong><small class="${gmJump ? "is-warning" : ""}">${escapeHtml(item.duration)} · ${complete ? "abgeschlossen" : available ? (gmJump ? "bereit" : "empfohlen") : "gesperrt"}</small></span><span class="home-chevron" aria-hidden="true">${available ? "›" : "🔒"}</span></button>`;
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
  if (state.view === "detail") {
    renderFrame("detail", scene);
    app.innerHTML = renderDetailView();
    return;
  }
  const soundboard = cues.length ? `
    <section class="soundboard" aria-labelledby="soundboard-title">
      <div class="section-heading soundboard-heading"><div><h2 id="soundboard-title">Soundboard</h2><p>Preset für die Stimmung. Effekte bleiben bewusst einzeln.</p></div><button class="button button-primary" data-action="preset" type="button">Szene starten</button></div>
      <div class="audio-mix" aria-label="Lautstärken">
        ${[["master", "Gesamt"], ["ambient", "Atmosphäre"], ["music", "Musik"], ["sfx", "Effekte"]].map(([key, label]) => `<label>${label}<input data-volume="${key}" type="range" min="0" max="1" step="0.01" value="${audio.settings[key]}"></label>`).join("")}
        <label class="audio-toggle"><input data-audio-safety type="checkbox" ${audio.safetyMode ? "checked" : ""}> Sicherheitslautstärke</label>
        <label class="audio-toggle"><input data-audio-duck type="checkbox" ${audio.readAloudDuck ? "checked" : ""}> Musik beim Vorlesen absenken</label>
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
        ${clues.length ? clues.map((clue) => { const found = state.clues.has(clue.id); return `<div class="clue-row"><button class="check-row" data-open-clue="${escapeHtml(clue.id)}" type="button" aria-label="Hinweis ${escapeHtml(clue.id)} · ${escapeHtml(clue.title)} öffnen"><span class="checkmark">${found ? "✓" : ""}</span><span><strong>${escapeHtml(clue.title)}</strong><small>${escapeHtml(clue.details)}</small></span>${clue.required ? `<em>PFLICHT</em>` : ""}<span class="check-row-chevron" aria-hidden="true">›</span></button><button class="clue-toggle" data-clue="${escapeHtml(clue.id)}" type="button" aria-pressed="${found}" title="${found ? "Hinweis als offen markieren" : "Hinweis als gefunden markieren"}"><span class="checkmark">${found ? "✓" : ""}</span><span class="visually-hidden">${found ? "Als offen markieren" : "Als gefunden markieren"}</span></button></div>`; }).join("") : `<p class="quiet-copy">Keine Pflicht-Hinweise. Lass die Erscheinung auf die Gruppe reagieren.</p>`}
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
        <div class="handout-list">${handouts.map((handout) => { const locked = handout.spoiler && !state.spoilersOpen; return `<button class="handout-row ${locked ? "is-locked" : ""}" data-open-handout="${escapeHtml(handout.id)}" type="button" aria-label="${locked ? "Gesperrtes Handout" : "Handout"} ${escapeHtml(handout.id)} öffnen"><span>${locked ? "🔒" : "▤"}</span><div><strong>${escapeHtml(handout.id)} · ${escapeHtml(handout.title)}</strong><small>${locked ? "SL-Spoiler. Erst im Leitstand öffnen." : `${escapeHtml(handout.format)} · ${escapeHtml(handout.fallback)}`}</small></div><span class="handout-chevron" aria-hidden="true">›</span></button>`; }).join("")}</div>
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
    const destination = sceneButton.dataset.scene;
    if (!canEnterScene(destination)) {
      audioStatus.textContent = "Diese Szene ist noch gesperrt. Schließe zuerst die vorherigen Abschnitte ab.";
      audioStatus.dataset.tone = "warning";
      return;
    }
    clearDetailNavigation();
    state.currentSceneId = destination;
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
  const handoutButton = event.target.closest("[data-open-handout]");
  if (handoutButton) {
    openDetail("handout", handoutButton.dataset.openHandout);
    return;
  }
  const clueDetailButton = event.target.closest("[data-open-clue]");
  if (clueDetailButton) {
    openDetail("clue", clueDetailButton.dataset.openClue);
    return;
  }
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
    clearDetailNavigation();
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
    state.finaleMode = "guided";
    state.combatState = null;
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
  if (guideAction === "finale-mode") {
    setFinaleMode(event.target.closest("[data-mode]")?.dataset.mode || "guided");
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
      clearDetailNavigation();
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
    const option = (currentGuideStep(state.currentSceneId)?.options || []).find((candidate) => candidate.id === guideOption.dataset.guideOption);
    if (!option || !optionAvailable(option)) {
      audioStatus.textContent = "Diese Option ist noch nicht freigeschaltet.";
      audioStatus.dataset.tone = "warning";
      return;
    }
    const destination = guideOption.dataset.destination;
    const ending = guideOption.dataset.ending;
    if (ending) {
      state.endingID = ending;
      clearFinaleRolls();
      resetFinaleProgress();
      if (state.combatState && state.combatState.endingID !== ending) state.combatState = null;
    }
    if (destination) {
      if (!canEnterScene(destination, true)) {
        audioStatus.textContent = "Dieser Abschnitt bleibt gesperrt, bis alle erforderlichen Ermittlungsorte abgeschlossen sind.";
        audioStatus.dataset.tone = "warning";
        return;
      }
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
  const combatAction = event.target.closest("[data-combat-action]");
  if (combatAction) {
    const actionName = combatAction.dataset.combatAction;
    const participantID = combatAction.dataset.combatId;
    if (actionName === "sort") sortCombatByInitiative();
    if (actionName === "next") nextCombatTurn();
    if (actionName === "finish") finishCombat(combatAction.dataset.outcome === "victory" ? "victory" : "defeat");
    if (actionName === "spend-ammo" && participantID) {
      const participant = combatParticipant(participantID);
      if (participant && participant.ammunition > 0) {
        updateCombatParticipant(participantID, (next) => { next.ammunition -= 1; });
        if (state.combatState) {
          state.combatState = { ...state.combatState, log: [...state.combatState.log, `${participant.name} verwendet eine Revolverpatrone.`].slice(-100) };
          persist();
          render();
        }
      }
    }
    if (actionName === "log-attack" && participantID) {
      const participant = combatParticipant(participantID);
      if (participant && state.combatState) {
        state.combatState = { ...state.combatState, log: [...state.combatState.log, `${participant.name} greift an · ${participant.attackSkill} · Schaden ${participant.damageDice}`].slice(-100) };
        persist();
        render();
      }
    }
    if (actionName === "log-parry" && participantID) {
      const participant = combatParticipant(participantID);
      if (participant && state.combatState) {
        state.combatState = { ...state.combatState, log: [...state.combatState.log, `${participant.name} pariert mit Handeln.`].slice(-100) };
        persist();
        render();
      }
    }
    if (actionName === "log") {
      const input = document.querySelector("[data-combat-log]");
      const message = input?.value?.trim();
      if (message && state.combatState) {
        state.combatState = { ...state.combatState, log: [...state.combatState.log, message].slice(-100) };
        persist();
        render();
      }
    }
    return;
  }
  const setupButton = event.target.closest("[data-setup]");
  if (setupButton) {
    toggleSet(state.setupChecks, setupButton.dataset.setup);
    return;
  }
  if (action === "home") {
    clearDetailNavigation();
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
  if (action === "detail-back") {
    closeDetail();
    return;
  }
  if (action === "menu") {
    const isOpen = topbarMenu.getAttribute("aria-expanded") === "true";
    topbarMenu.setAttribute("aria-expanded", String(!isOpen));
    topbarMenuPanel.hidden = isOpen;
    return;
  }
  if (action === "start" || action === "continue") {
    clearDetailNavigation();
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
  if (event.target.matches("[data-audio-safety]")) {
    audio.setSafetyMode(event.target.checked);
    return;
  }
  if (event.target.matches("[data-audio-duck]")) {
    audio.setReadAloudDuck(event.target.checked);
    return;
  }
  if (event.target.matches("[data-combat-field]")) {
    const id = event.target.dataset.combatId;
    const field = event.target.dataset.combatField;
    const value = field === "name" ? event.target.value : Number(event.target.value);
    if (id && field) {
      updateCombatParticipant(id, (participant) => {
        if (field === "name") participant.name = String(value).trim() || participant.name;
        else participant[field] = Number.isFinite(value) ? value : 0;
      });
    }
    return;
  }
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
  if (event.target.matches("[data-state]")) {
    const key = event.target.dataset.state;
    const maximum = key === "injuries" ? 3 : 5;
    if (["time", "warmth", "trust", "injuries"].includes(key)) {
      state[key] = normalizedTrack(event.target.value, maximum);
      persist();
      render();
    }
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
  if (!window.confirm("Runde komplett zurücksetzen? Namen, Notizen und Storyfortschritt werden auf diesem Gerät gelöscht.")) return;
  state.completed.clear();
  state.clues.clear();
  state.checklist.clear();
  state.setupChecks.clear();
  state.guidedIndexes = {};
  state.guideHistory = [];
  state.guidedRolls = {};
  state.guidedRollHistory = [];
  state.finaleSuccesses = 0;
  state.finaleFailures = 0;
  state.finaleOutcome = "";
  state.finaleMode = "guided";
  state.combatState = null;
  state.pendingRoll = null;
  state.selectedConsequenceID = "";
  resetItemState();
  state.gmMode = false;
  state.endingID = "";
  state.currentSceneId = "S01";
  state.time = 0;
  state.warmth = 3;
  state.trust = 3;
  state.injuries = 0;
  state.playerNames = ["", "", ""];
   state.sessionNote = "";
   state.sceneNotes = {};
   state.detail = null;
   state.detailStack = [];
   state.detailReturnView = "home";
   state.view = "home";
  persist();
  render();
  audioStatus.textContent = "Fortschritt zurückgesetzt.";
});

async function boot() {
  app.replaceChildren(document.querySelector("#loading-template").content.cloneNode(true));
  try {
    const response = await fetch("./data/manifest.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.manifest = await response.json();
    if (state.gmMode && state.sessionSchema !== "v7") migrateActiveLegacySession();
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
