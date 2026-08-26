export const guideKindLabels = {
  readAloud: "JETZT VORLESEN",
  gmInfo: "NUR FÜR DIE SPIELLEITUNG",
  playerAction: "DIE SPIELER KÖNNEN JETZT",
  trigger: "WENN DAS PASSIERT",
  roll: "WÜRFELPROBE",
  clue: "HINWEIS ODER GEGENSTAND",
  choice: "ENTSCHEIDUNG",
  next: "NÄCHSTER SCHRITT",
};

export function evaluateRoll(roll, target, gifted = false) {
  const safeRoll = Math.min(Math.max(Number(roll) || 1, 1), 100);
  const safeTarget = Math.min(Math.max(Number(target) || 1, 1), 100);
  const criticalSuccess = safeRoll <= safeTarget * 0.10;
  const criticalFailure = safeRoll >= 90 + safeTarget * 0.10;
  const success = safeRoll <= safeTarget && !criticalFailure;
  return {
    roll: safeRoll,
    target: safeTarget,
    success,
    criticalSuccess,
    criticalFailure,
    label: criticalFailure ? "Kritischer Misserfolg" : criticalSuccess ? "Kritischer Erfolg" : safeRoll <= safeTarget ? "Erfolg" : "Misserfolg",
  };
}
