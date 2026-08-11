export class AudioEngine {
  constructor({ onStatus, onChange }) {
    this.onStatus = onStatus;
    this.onChange = onChange;
    this.active = new Map();
    this.settings = {
      master: 0.82,
      ambient: 0.64,
      music: 0.58,
      sfx: 0.78,
    };
  }

  categoryVolume(category) {
    return this.settings[category] ?? 0.7;
  }

  volumeFor(cue) {
    const gain = 1 + Number(cue.gain ?? 0);
    return Math.max(0, Math.min(1, this.settings.master * this.categoryVolume(cue.category) * gain));
  }

  applyVolumes() {
    for (const { cue, audio } of this.active.values()) audio.volume = this.volumeFor(cue);
  }

  setVolume(category, value) {
    this.settings[category] = Number(value);
    this.applyVolumes();
    this.onChange();
  }

  isPlaying(id) {
    return this.active.has(id);
  }

  async play(cue) {
    if (this.active.has(cue.id)) {
      this.stop(cue.id);
      return;
    }
    const audio = new Audio(`./assets/audio/${encodeURIComponent(cue.file)}`);
    audio.loop = cue.mode === "loop";
    audio.volume = this.volumeFor(cue);
    audio.preload = "auto";
    audio.addEventListener("ended", () => {
      if (cue.mode !== "loop") {
        this.active.delete(cue.id);
        this.onChange();
      }
    });
    audio.addEventListener("error", () => {
      this.active.delete(cue.id);
      this.onStatus(`Audio konnte nicht geladen werden: ${cue.file}`, "error");
      this.onChange();
    });
    this.active.set(cue.id, { cue, audio });
    try {
      await audio.play();
      this.onStatus(`${cue.id} läuft: ${cue.title}`, "ok");
    } catch (error) {
      this.active.delete(cue.id);
      this.onStatus(`Browser blockiert den Ton. Tippe erneut auf einen Sound.`, "error");
    }
    this.onChange();
  }

  async playPreset(cues) {
    for (const cue of cues) {
      if (cue.category === "sfx") continue;
      if (!this.active.has(cue.id)) await this.play(cue);
    }
    this.onStatus("Szenen-Preset läuft. Effekte bleiben einzeln steuerbar.", "ok");
    this.onChange();
  }

  stop(id) {
    const entry = this.active.get(id);
    if (!entry) return;
    entry.audio.pause();
    entry.audio.currentTime = 0;
    this.active.delete(id);
    this.onChange();
  }

  stopAll() {
    for (const id of [...this.active.keys()]) this.stop(id);
    this.onStatus("Alle Sounds sind gestoppt.", "ok");
    this.onChange();
  }

  async testTone() {
    try {
      const context = new AudioContext();
      const gain = context.createGain();
      const oscillator = context.createOscillator();
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(880, context.currentTime);
      gain.gain.setValueAtTime(0.0001, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.17, context.currentTime + 0.025);
      gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.55);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + 0.58);
      this.onStatus("Testton gespielt. Wenn du nichts hörst: Lautstärke, Stummmodus und Bluetooth prüfen.", "ok");
    } catch (error) {
      this.onStatus("Der Browser konnte keinen Testton öffnen.", "error");
    }
  }
}
