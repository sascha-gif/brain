// Nimmt nur die erwartete Form an, alles andere fliegt raus.
const str = (v, max) => (typeof v === "string" ? v.trim().slice(0, max) : "");

export function clean(input) {
  const topics = Array.isArray(input?.topics) ? input.topics.slice(0, 200) : null;
  if (!topics) return null;
  return {
    topics: topics.map((t) => ({
      id: str(t?.id, 40),
      name: str(t?.name, 120) || "Ohne Namen",
      c: Number.isInteger(t?.c) && t.c >= 1 && t.c <= 12 ? t.c : 1,
      subs: (Array.isArray(t?.subs) ? t.subs.slice(0, 500) : []).map((s) => ({
        id: str(s?.id, 40),
        t: str(s?.t, 300) || "Ohne Titel",
        d: s?.d === true,
      })),
    })),
  };
}
