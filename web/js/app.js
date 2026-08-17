import { AudioEngine } from "./audio-engine.js";
import { evaluateRoll, guideKindLabels, guidedFlow } from "./guided-flow.js";
import { SupabaseSync } from "./supabase-sync.js";

const app = document.querySelector("#app");
const sceneNav = document.querySelector("#scene-nav");
const progressCount = document.querySelector("#progress-count");
const progressFill = document.querySelector("#progress-fill");
const audioStatus = document.querySelector("#audio-status");
const topbarBack = document.querySelector("#topbar-back");
const screenTitle = document.querySelector("#screen-title");
const topbarMenu = document.querySelector("#topbar-menu");
const topbarMenuPanel = document.querySelector("#topbar-menu-panel");
const nightPhases = [
  { title: "Der Bruch", detail: "Manipulierte Kutsche, Schnee und der erste falsche Schutz.", symbol: "✦" },
  { title: "Das Dorf", detail: "Gasthaus, Kirche und Schmiede öffnen ihre Widersprüche.", symbol: "⌂" },
  { title: "Die Spur", detail: "Namen, Buchseiten und der Weg zur Alten Eiche.", symbol: "⌕" },
  { title: "Der Ruf", detail: "Die Glocke schlägt. Das Dorf muss sich entscheiden.", symbol: "!" },
  { title: "Der Morgen", detail: "Drei mögliche Enden und die Rechnung des Waldes.", symbol: "◉" },
];

function normalizedNightPhase(value) {
  const index = Number(value);
  if (!Number.isFinite(index)) return 0;
  return Math.min(Math.max(Math.trunc(index), 0), nightPhases.length - 1);
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
  setupChecks: new Set(stored("kraehenfels.setupChecks", [])),
  guidedRolls: stored("kraehenfels.guidedRolls", {}),
  audioRatings: stored("kraehenfels.audioRatings", {}),
  endingID: localStorage.getItem("kraehenfels.endingID") || "",
  rollOpen: false,
  spoilersOpen: false,
  statusTone: "ok",
  cloud: { status: "starting", error: "", session: null, ratings: {}, online: navigator.onLine },
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
  localStorage.setItem("kraehenfels.setupChecks", JSON.stringify([...state.setupChecks]));
  localStorage.setItem("kraehenfels.guidedRolls", JSON.stringify(state.guidedRolls));
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

const cloud = new SupabaseSync((snapshot) => {
  state.cloud = snapshot;
  // Remote rows are the source of truth for a signed-in session. Local-only
  // ratings stay visible until the next sync has a chance to upload them.
  if (snapshot.session && Object.keys(snapshot.ratings).length) {
    state.audioRatings = { ...state.audioRatings, ...snapshot.ratings };
    persist();
  }
  if (state.manifest) render();
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

function cloudStatusCopy() {
  if (!state.cloud.online) return "Offline · lokale Bewertungen bleiben erhalten";
  if (state.cloud.status === "connected") return state.cloud.session?.user?.email ? `Verbunden als ${state.cloud.session.user.email}` : "Bewertungen werden live synchronisiert";
  if (state.cloud.status === "error") return state.cloud.error || "Cloud-Synchronisierung fehlgeschlagen";
  if (state.cloud.status === "unavailable") return "Cloud nicht erreichbar · lokal weiterarbeiten";
  if (state.cloud.status === "signed-out") return "Noch nicht verbunden · lokal weiterarbeiten";
  return "Cloud-Verbindung wird vorbereitet …";
}

function renderCloudCard() {
  const signedIn = Boolean(state.cloud.session);
  return `<section class="cloud-card ${signedIn ? "is-connected" : ""}" aria-labelledby="cloud-title">
    <div class="cloud-card-copy"><span class="eyebrow">LIVE-SYNC</span><h2 id="cloud-title">Soundbewertungen zentral sammeln</h2><p>${escapeHtml(cloudStatusCopy())}</p></div>
    <div class="cloud-card-actions">
      ${signedIn ? `<button class="button button-quiet" data-action="cloud-sign-out" type="button">Abmelden</button>` : `<button class="button button-primary" data-action="cloud-sign-in" type="button">Mit Google anmelden</button>`}
      <span class="cloud-rating-count">${Object.keys(state.audioRatings).length} bewertet</span>
    </div>
    ${state.cloud.error ? `<small class="cloud-error">${escapeHtml(state.cloud.error)}</small>` : ""}
  </section>`;
}

function renderAuthGate() {
  const busy = state.cloud.status === "starting" || state.cloud.status === "authenticating";
  const unavailable = state.cloud.status === "unavailable";
  const title = busy ? "Anmeldung wird geprüft." : unavailable ? "Cloud nicht erreichbar." : "Nur für die Spielleitung.";
  const detail = busy
    ? "Einen Moment — Krähenfels prüft deine sichere Sitzung."
    : unavailable
      ? "Die Verbindung zu Supabase konnte nicht hergestellt werden. Prüfe deine Internetverbindung und versuche es erneut."
      : "Melde dich mit Google an, damit Soundbewertungen und dein Spielstand deinem Konto zugeordnet werden können.";
  const action = unavailable
    ? `<button class="button button-primary auth-button" data-action="cloud-retry" type="button">Verbindung erneut prüfen</button>`
    : `<button class="button button-primary auth-button" data-action="cloud-sign-in" type="button" ${busy ? "disabled" : ""}><span class="google-mark" aria-hidden="true">G</span>${state.cloud.status === "authenticating" ? "Weiter zu Google …" : "Mit Google anmelden"}</button>`;
  return `<section class="auth-view" aria-labelledby="auth-title">
    <div class="auth-card">
      <img class="auth-icon" src="./assets/icon.png" alt="" />
      <p class="home-kicker">Krähenfels · Die letzte Kutsche</p>
      <h1 id="auth-title">${title}</h1>
      <p class="auth-lead">${detail}</p>
      <div class="auth-points" aria-label="Vorteile der Anmeldung">
        <div><span aria-hidden="true">✓</span><p><strong>Dein Leitstand bleibt geschützt.</strong><small>Nur dein angemeldetes Konto kann die Spieloberfläche öffnen.</small></p></div>
        <div><span aria-hidden="true">↗</span><p><strong>Soundbewertungen live speichern.</strong><small>„Passt“ und „Falsch“ werden zwischen Web und iPhone synchronisiert.</small></p></div>
        <div><span aria-hidden="true">⌁</span><p><strong>Beim nächsten Mal direkt weiterspielen.</strong><small>Deine Sitzung wird sicher auf diesem Gerät wiedererkannt.</small></p></div>
      </div>
      ${action}
      ${state.cloud.error ? `<p class="auth-error" role="alert">${escapeHtml(state.cloud.error)}</p>` : ""}
      <p class="auth-footnote">Google verwaltet die Anmeldung. Krähenfels erhält nur die für die Sitzung nötige Konto-ID und E-Mail-Adresse.</p>
    </div>
  </section>`;
}

function renderNPC(npc) {
  const prompt = npc.prompts?.[0] ? `<p class="npc-prompt">Impuls: ${escapeHtml(npc.prompts[0])}</p>` : "";
  const spoiler = state.spoilersOpen ? `<div class="npc-spoiler">
      ${npc.knows?.length ? `<p><span>WEISS</span>${npc.knows.map(escapeHtml).join("<br>")}</p>` : ""}
      ${npc.hides?.length ? `<p><span>VERSCHWEIGT</span>${npc.hides.map(escapeHtml).join("<br>")}</p>` : ""}
      ${npc.givesHandoutIds?.length ? `<p class="gives-handout"><span>GIBT</span>${npc.givesHandoutIds.map((id) => `${id} · ${escapeHtml(handoutById(id)?.title ?? "")}`).join("<br>")}</p>` : ""}
    </div>` : "";
  const stateIndex = Number(state.npcStates[npc.id] || 0);
  const states = npc.states?.length ? `<label class="npc-state"><span>Haltung</span><select data-npc-state="${npc.id}">${npc.states.map((label, index) => `<option value="${index}" ${index === stateIndex ? "selected" : ""}>${escapeHtml(label)}</option>`).join("")}</select></label>` : "";
  return `<article class="npc-entry">
    <div class="npc-heading"><div><h3>${escapeHtml(npc.name)}</h3><p>${escapeHtml(npc.role)}</p></div></div>
    <p>${escapeHtml(npc.description)}</p>${states}${spoiler}${prompt}
  </article>`;
}

function renderFrame(view, scene) {
  const isHome = view === "home";
  topbarBack.hidden = isHome;
  screenTitle.textContent = isHome ? "Krähenfels" : view === "gm-start" ? "Spielleiter-Modus" : scene.shortTitle;
  document.body.dataset.view = view;
  topbarMenuPanel.hidden = true;
  topbarMenu.setAttribute("aria-expanded", "false");
}

function guideStepsFor(sceneID) {
  return guidedFlow.steps[sceneID] || [];
}

function currentGuideIndex(sceneID) {
  const steps = guideStepsFor(sceneID);
  return Math.min(Math.max(Number(state.guidedIndexes[sceneID] || 0), 0), Math.max(0, steps.length - 1));
}

function currentGuideStep(sceneID) {
  return guideStepsFor(sceneID)[currentGuideIndex(sceneID)];
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

function renderGMStart() {
  const checked = state.setupChecks.size;
  return `<div class="gm-start-view">
    <section class="gm-intro">
      <p class="home-kicker">Spielleiter-Modus</p>
      <h2>Heute Abend musst du nichts auswendig können.</h2>
      <p>Dieser Assistent führt dich durch Vorbereitung, Vorlesetexte, Spieleraktionen, Hinweise und Würfelproben. Du entscheidest jederzeit selbst, ob die Gruppe einen anderen Weg nimmt.</p>
    </section>
    <section class="guide-panel setup-panel" aria-labelledby="setup-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Vorbereitung</span><h2 id="setup-title">In fünf Minuten startklar</h2></div><b>${checked}/${guidedFlow.setupItems.length}</b></div>
      <div class="setup-list">${guidedFlow.setupItems.map((item) => `<button class="setup-row" data-setup="${item.id}" type="button" aria-pressed="${state.setupChecks.has(item.id)}"><span class="setup-check">${state.setupChecks.has(item.id) ? "✓" : ""}</span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></span></button>`).join("")}</div>
    </section>
    <section class="guide-panel characters-panel" aria-labelledby="characters-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Die drei Reisenden</span><h2 id="characters-title">Fertige Figuren für den Tisch</h2></div><span class="guide-muted">Namen kannst du später eintragen</span></div>
      <div class="character-grid">${guidedFlow.characters.map((character) => `<article class="character-card"><div class="character-avatar">${escapeHtml(character.name.slice(0, 1))}</div><div><h3>${escapeHtml(character.name)}</h3><p class="character-role">${escapeHtml(character.role)}</p><p>${escapeHtml(character.hook)}</p><div class="character-skills">${character.skills.map((skill) => `<span>${escapeHtml(skill)}</span>`).join("")}</div><small>${escapeHtml(character.tablePrompt)}</small></div></article>`).join("")}</div>
    </section>
    <section class="guide-panel briefing-panel" aria-labelledby="briefing-title">
      <div class="guide-panel-heading"><div><span class="eyebrow">Vor dem ersten Satz</span><h2 id="briefing-title">Das sagst du den Spielern</h2></div></div>
      <blockquote>${escapeHtml(guidedFlow.playerBriefing)}</blockquote>
      <p class="spoiler-line"><span>NICHT VERRATEN</span> ${escapeHtml(guidedFlow.hiddenFromPlayers)}</p>
    </section>
    <button class="button button-primary guide-start-button" data-guide-action="begin" type="button">${checked === guidedFlow.setupItems.length ? "Spielleiter-Modus starten" : "Trotzdem starten"}<span aria-hidden="true">›</span></button>
  </div>`;
}

function renderRollPanel(step) {
  const roll = step.roll;
  const previous = state.guidedRolls[step.id];
  if (!state.rollOpen) return `<button class="button button-primary guide-action" data-guide-action="open-roll" type="button">Probe auswerten</button>`;
  return `<div class="roll-panel"><div class="roll-panel-heading"><div><span class="eyebrow">W100-Probe</span><strong>${escapeHtml(roll.actor)}</strong></div><button class="text-button" data-guide-action="close-roll" type="button">Schließen</button></div><p><b>Fertigkeit:</b> ${escapeHtml(roll.ability)} · <b>Zielwert:</b> ${escapeHtml(roll.target)}</p><p class="roll-modifier">${escapeHtml(roll.modifier)}</p><div class="roll-inputs"><label class="roll-input"><span>Gewürfeltes Ergebnis</span><input data-roll-value type="number" min="1" max="100" inputmode="numeric" value="${previous?.roll || ""}" placeholder="z. B. 42"></label><label class="roll-input"><span>Zielwert der Fertigkeit</span><input data-roll-target type="number" min="1" max="100" inputmode="numeric" value="${previous?.target || 50}" placeholder="z. B. 65"></label></div><button class="button button-primary guide-action" data-guide-action="resolve-roll" data-step="${step.id}" type="button">Ergebnis auswerten</button>${previous ? `<div class="roll-result ${previous.success ? "is-success" : "is-failure"}"><strong>${escapeHtml(previous.label)}</strong><span>${previous.roll} gegen ${previous.target}</span><p>${escapeHtml(previous.success ? roll.success : roll.failure)}</p></div>` : ""}</div>`;
}

function renderGuideStep(step) {
  if (!step) return `<div class="guide-empty"><h2>Schritt abgeschlossen</h2><p>Wähle links eine Szene oder kehre zum Start zurück.</p></div>`;
  const scene = sceneById(step.sceneID || state.currentSceneId);
  const index = currentGuideIndex(state.currentSceneId);
  const steps = guideStepsFor(state.currentSceneId);
  const cue = step.audioCueID ? cueById(step.audioCueID) : null;
  const options = step.options || [];
  let action = "";
  if (step.kind === "roll") action = renderRollPanel(step);
  else if (options.length) action = `<div class="guide-options">${options.map((option) => `<button class="guide-option" data-guide-option="${option.id}" data-destination="${option.destinationSceneID || ""}" data-ending="${option.endingID || ""}" type="button"><strong>${escapeHtml(option.title)}</strong><small>${escapeHtml(option.detail)}</small><span aria-hidden="true">›</span></button>`).join("")}</div>`;
  else if (step.kind === "readAloud") action = `<button class="button button-primary guide-action" data-guide-action="read" data-cue="${cue?.id || ""}" type="button">${cue ? "Sound vorbereiten und vorlesen" : "Vorgelesen – weiter"}<span aria-hidden="true">›</span></button>`;
  else action = `<button class="button button-primary guide-action" data-guide-action="advance" type="button">${escapeHtml(step.actionLabel || "Weiter")}<span aria-hidden="true">›</span></button>`;
  const clueLine = step.clueID ? `<div class="guide-clue-note"><span>HINWEIS</span> Dieser Hinweis ist garantiert und darf nicht an einem Würfelwurf scheitern.</div>` : "";
  return `<div class="guided-scene-view">
    <div class="guide-progress-row"><span>SCHRITT ${index + 1} VON ${steps.length}</span><b>${escapeHtml(scene.shortTitle)}</b></div>
    <div class="guide-progress-track"><i style="width:${((index + 1) / Math.max(1, steps.length)) * 100}%"></i></div>
    <section class="guide-scene-hero" style="--scene-art: url('./assets/art/${encodeURIComponent(scene.art)}')"><div><span>${escapeHtml(scene.id)} · ${escapeHtml(scene.duration)}</span><h2>${escapeHtml(scene.title)}</h2><p>${escapeHtml(scene.goal)}</p></div></section>
    <section class="guide-step-card kind-${step.kind}">
      <div class="guide-kind"><span>${escapeHtml(guideKindLabels[step.kind] || "SPIELLEITER-SCHRITT")}</span>${step.required ? "<b>PFLICHT</b>" : ""}</div>
      <h2>${escapeHtml(step.title)}</h2>
      <p class="guide-step-body">${escapeHtml(step.body)}</p>
      ${step.roll ? `<div class="roll-brief"><span class="eyebrow">WANN WIRD GEWÜRFELT?</span><strong>${escapeHtml(step.roll.actor)}</strong><p>${escapeHtml(step.roll.ability)} · ${escapeHtml(step.roll.target)}</p><small>${escapeHtml(step.roll.modifier)}</small></div>` : ""}
      ${clueLine}${guideReferences(step)}
      ${action}
    </section>
    <div class="guide-quick-actions"><button class="quick-action" data-action="materials" type="button">▱ Materialien</button><button class="quick-action" data-action="rules" type="button">▧ Regeln</button><button class="quick-action" data-action="audio-check" type="button">≋ Soundplan</button><button class="quick-action" data-action="dossier" type="button">⌕ Fakten</button></div>
    <section class="guide-table-note"><div><span class="eyebrow">TISCHNOTIZ</span><p>Was ist gerade passiert? Was bleibt offen?</p></div><textarea data-scene-note="${scene.id}" rows="3" placeholder="Kurz notieren …">${escapeHtml(state.sceneNotes[scene.id] || "")}</textarea></section>
  </div>`;
}

function renderGuidedScene(scene) {
  return renderGuideStep(currentGuideStep(scene.id));
}

function renderHome(scene) {
  const scenes = state.manifest.scenes;
  const totalSteps = scene.id === "S01" ? 5 : Math.max(1, scene.checklist.length);
  const doneSteps = scene.checklist.filter((_, index) => state.checklist.has(`${scene.id}-${index}`)).length;
  const currentStep = Math.min(doneSteps + 1, totalSteps);
  const assignedPlayers = state.playerNames.filter((name) => name.trim()).length;
  const sceneProgress = Math.round((state.completed.size / Math.max(1, scenes.length)) * 100);
  const nightSegments = Array.from({ length: nightPhases.length + 1 }, (_, index) => `<i class="night-segment ${index <= state.nightPhase ? "is-active" : ""}"></i>`).join("");
  const stageLabel = state.completed.size ? `${state.completed.size}/${scenes.length}` : `0/${scenes.length}`;
  const unassigned = 3 - assignedPlayers;
  const tableLabel = assignedPlayers === 3 ? "Alle drei Reisenden sind zugewiesen" : unassigned === 3 ? "Drei Reisende sind noch nicht zugewiesen" : unassigned === 2 ? "Zwei Reisende sind noch nicht zugewiesen" : "Ein Reisender ist noch nicht zugewiesen";
  return `<div class="home-view">
    <section class="home-intro" aria-labelledby="home-title">
      <p class="home-kicker">Krähenfels · Die letzte Kutsche</p>
      <h1 id="home-title"><span>Dein Leitstand für</span><span>die Nacht.</span></h1>
      <p class="home-subtitle">Drei Reisende · Schwarzwald · November 1890</p>
    </section>

    ${renderCloudCard()}

    <button class="home-start-card" data-action="start" type="button">
      <span class="home-icon home-icon-play" aria-hidden="true">▶</span>
      <span class="home-card-copy"><strong>Spielleiter-Modus starten</strong><small>Vorbereitung, fertige Figuren und Schritt-für-Schritt-Führung</small></span>
      <span class="home-chevron" aria-hidden="true">›</span>
    </button>

    <button class="home-card continue-card" data-action="continue" type="button">
      <span class="home-icon home-icon-route" aria-hidden="true">⌁</span>
      <span class="home-card-copy"><span class="home-card-label">Jetzt weiterspielen <b>${stageLabel}</b></span><strong>${escapeHtml(scene.shortTitle)}</strong><small>Schritt ${currentStep} von ${totalSteps}</small><span class="home-progress"><i style="width:${sceneProgress}%"></i></span></span>
      <span class="home-chevron" aria-hidden="true">↗</span>
    </button>

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
      <button class="quick-action" data-action="rules" type="button"><span aria-hidden="true">▧</span>Regeln</button>
      <button class="quick-action" data-action="audio-check" type="button"><span aria-hidden="true">≋</span>Audio-Check</button>
      <button class="quick-action" data-action="dossier" type="button"><span aria-hidden="true">⌕</span>Akte</button>
    </section>
  </div>`;
}

function render() {
  if (!state.manifest) return;
  const scene = sceneById(state.currentSceneId) || state.manifest.scenes[0];
  const authenticated = Boolean(state.cloud.session);
  document.body.dataset.authRequired = authenticated ? "false" : "true";
  if (!authenticated) {
    renderFrame("auth", scene);
    app.innerHTML = renderAuthGate();
    return;
  }
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

    ${renderCloudCard()}

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
      <div class="npc-list">${npcs.length ? npcs.map(renderNPC).join("") : `<p class="quiet-copy">Der Wald reagiert auf die Gruppe und spricht nicht mit Worten.</p>`}</div>
    </section>

    <section class="content-section dossier-section">
      <div class="section-heading"><h2>Akte</h2><span>${state.manifest.facts.filter((fact) => fact.clueIds.every((id) => state.clues.has(id))).length} / ${state.manifest.facts.length} Schlussfolgerungen</span></div>
      <div class="fact-list">${state.manifest.facts.map((fact) => { const found = fact.clueIds.every((id) => state.clues.has(id)); return `<div class="fact-row ${found ? "is-found" : ""}"><span>${found ? "✓" : "·"}</span><div><strong>${escapeHtml(fact.title)}</strong><small>${escapeHtml(found ? fact.details : "Noch nicht bestätigt")}</small></div></div>`; }).join("")}</div>
      <div class="hook-list"><h3>Figuren-Verbindungen</h3><p class="muted">Wählt je eine persönliche Verbindung zum Fall – sie ist ein Aufhänger, kein zusätzlicher Plot.</p>${state.manifest.travelHooks.map((hook) => `<button class="check-row ${Object.values(state.selectedHooks).includes(hook.id) ? "is-found" : ""}" data-hook="${hook.id}" type="button" aria-pressed="${Object.values(state.selectedHooks).includes(hook.id)}"><span class="checkmark">${Object.values(state.selectedHooks).includes(hook.id) ? "✓" : ""}</span><span><strong>${escapeHtml(hook.title)}</strong><small>${escapeHtml(hook.prompt)}</small></span></button>`).join("")}</div>
    </section>

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
    void cloud.setRating(cueID, rating);
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
    state.gmMode = true;
    state.currentSceneId = "S01";
    state.guidedIndexes.S01 = 0;
    state.view = "guided";
    state.rollOpen = false;
    persist();
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (guideAction === "advance") {
    const steps = guideStepsFor(state.currentSceneId);
    state.guidedIndexes[state.currentSceneId] = Math.min(currentGuideIndex(state.currentSceneId) + 1, Math.max(0, steps.length - 1));
    state.rollOpen = false;
    persist();
    render();
    return;
  }
  if (guideAction === "read") {
    const cue = cueById(event.target.closest("[data-cue]")?.dataset.cue || "");
    // Start audio without making the guided flow wait for a browser autoplay promise.
    // The cue reports its own success or error in the persistent status line.
    if (cue) void audio.play(cue);
    const steps = guideStepsFor(state.currentSceneId);
    state.guidedIndexes[state.currentSceneId] = Math.min(currentGuideIndex(state.currentSceneId) + 1, Math.max(0, steps.length - 1));
    persist();
    render();
    return;
  }
  if (guideAction === "open-roll") { state.rollOpen = true; render(); return; }
  if (guideAction === "close-roll") { state.rollOpen = false; render(); return; }
  if (guideAction === "resolve-roll") {
    const step = currentGuideStep(state.currentSceneId);
    const value = Number(document.querySelector("[data-roll-value]")?.value || 1);
    const target = Number(document.querySelector("[data-roll-target]")?.value || 50);
    const result = evaluateRoll(value, target);
    state.guidedRolls[step.id] = result;
    state.rollOpen = false;
    state.guidedIndexes[state.currentSceneId] = Math.min(currentGuideIndex(state.currentSceneId) + 1, Math.max(0, guideStepsFor(state.currentSceneId).length - 1));
    if (!result.success && state.currentSceneId === "S06") state.threatLevel = Math.max(state.threatLevel, 4);
    persist();
    render();
    return;
  }
  const guideOption = event.target.closest("[data-guide-option]");
  if (guideOption) {
    const destination = guideOption.dataset.destination;
    const ending = guideOption.dataset.ending;
    if (ending) state.endingID = ending;
    if (destination) {
      state.currentSceneId = destination;
      state.guidedIndexes[destination] = 0;
      if (destination === "S08") state.completed.add("S07");
      if (destination === "S02") state.completed.add("S01");
      state.view = "guided";
    } else {
      const steps = guideStepsFor(state.currentSceneId);
      state.guidedIndexes[state.currentSceneId] = Math.min(currentGuideIndex(state.currentSceneId) + 1, Math.max(0, steps.length - 1));
    }
    state.rollOpen = false;
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
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (action === "cloud-sign-in") {
    await cloud.signInWithGoogle();
    return;
  }
  if (action === "cloud-retry") {
    await cloud.init();
    return;
  }
  if (action === "cloud-sign-out") {
    await cloud.signOut();
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
  if (action === "materials" || action === "rules" || action === "audio-check" || action === "dossier") {
    state.view = "scene";
    render();
    const target = { materials: ".handout-section", rules: ".dossier-section", "audio-check": ".soundboard", dossier: ".dossier-section" }[action];
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

document.addEventListener("input", (event) => {
  if (event.target.matches("[data-volume]")) audio.setVolume(event.target.dataset.volume, event.target.value);
  if (event.target.matches("[data-player-index]")) {
    state.playerNames[Number(event.target.dataset.playerIndex)] = event.target.value;
    persist();
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
  state.completed.clear(); state.clues.clear(); state.checklist.clear(); state.setupChecks.clear(); state.guidedIndexes = {}; state.guidedRolls = {}; state.gmMode = false; state.endingID = ""; state.currentSceneId = "S01"; state.view = "home"; persist(); render();
  audioStatus.textContent = "Fortschritt zurückgesetzt.";
});

async function boot() {
  app.replaceChildren(document.querySelector("#loading-template").content.cloneNode(true));
  try {
    const response = await fetch("./data/manifest.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.manifest = await response.json();
    if (!sceneById(state.currentSceneId)) state.currentSceneId = state.manifest.scenes[0].id;
    render();
    const localRatings = { ...state.audioRatings };
    await cloud.init();
    if (cloud.session) {
      await cloud.pushLocalRatings(localRatings, cloud.ratings);
      state.audioRatings = { ...state.audioRatings, ...cloud.ratings };
      persist();
      render();
    }
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./service-worker.js").catch(() => undefined);
  } catch (error) {
    app.innerHTML = `<section class="error-state"><h2>Leitstand konnte nicht starten</h2><p>Starte den lokalen Server über die Anleitung in <code>web/README.md</code>. Die App braucht einen Server, damit sie Inhalte und Audio laden kann.</p></section>`;
  }
}

boot();
