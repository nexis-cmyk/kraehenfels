import { AudioEngine } from "./audio-engine.js";

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
  const clue = cue.isClue ? `<span class="pill pill-warning">Hinweis: ${cue.printFallbackId}</span>` : "";
  return `<button class="cue-row ${active ? "is-playing" : ""}" data-cue="${cue.id}" type="button" aria-pressed="${active}">
    <span class="cue-action" aria-hidden="true">${active ? "Ⅱ" : "▶"}</span>
    <span class="cue-copy"><strong>${escapeHtml(cue.title)}</strong><small>${cue.id} · ${classForCategory(cue.category)}</small></span>
    ${clue}
    <span class="cue-state">${active ? "Läuft" : "Start"}</span>
  </button>`;
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
  screenTitle.textContent = isHome ? "Krähenfels" : scene.shortTitle;
  document.body.dataset.view = view;
  topbarMenuPanel.hidden = true;
  topbarMenu.setAttribute("aria-expanded", "false");
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
    state.view = "scene";
    persist();
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  const cueButton = event.target.closest("[data-cue]");
  if (cueButton) return audio.play(cueById(cueButton.dataset.cue));
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
  if (action === "home") {
    state.view = "home";
    render();
    document.querySelector("#scene-content").focus();
    return;
  }
  if (action === "menu") {
    const isOpen = topbarMenu.getAttribute("aria-expanded") === "true";
    topbarMenu.setAttribute("aria-expanded", String(!isOpen));
    topbarMenuPanel.hidden = isOpen;
    return;
  }
  if (action === "start" || action === "continue") {
    state.view = "scene";
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
  state.completed.clear(); state.clues.clear(); state.checklist.clear(); state.currentSceneId = "S01"; persist(); render();
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
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./service-worker.js").catch(() => undefined);
  } catch (error) {
    app.innerHTML = `<section class="error-state"><h2>Leitstand konnte nicht starten</h2><p>Starte den lokalen Server über die Anleitung in <code>web/README.md</code>. Die App braucht einen Server, damit sie Inhalte und Audio laden kann.</p></section>`;
  }
}

boot();
