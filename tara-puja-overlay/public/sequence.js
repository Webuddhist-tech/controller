// Loads content.json and flattens it into a list of "chunks" the controller
// walks through. Each chunk is up to `lines_per_screen` (2) lines of one verse.
// Sections (the major `##` parts) become the controller's left menu; "Next"
// advances chunk-by-chunk DOWN a section, then rolls into the next section.

async function loadSequence() {
  const res = await fetch("content.json");
  const content = await res.json();
  const N = content.lines_per_screen || 2;
  // Verses whose lines are long get one line per screen (so they wrap cleanly,
  // one at a time) instead of two; short verses stay as couplets.
  const LONG_LINE = content.long_line_threshold || 48;

  const chunks = [];
  const sections = [];

  content.sections.forEach((sec, si) => {
    const secEntry = { id: sec.id, title: sec.title, firstChunk: chunks.length, anytime: !!sec.anytime };  // anytime = Break/Tea, usable at any point
    sections.push(secEntry);

    sec.verses.forEach((v, vi) => {
      const bo = v.lines.bo || [];
      const en = v.lines.en || [];
      const zh = v.lines.zh || [];
      const tr = v.tr || [];   // transliteration (Latin), parallel to bo
      const trz = v.tr_zh || []; // Chinese phonetic transliteration, parallel to bo

      // Merge a short opener (Namo / Oṃ seed syllables) into the first sloka
      // line so the couplets pair cleanly (Namo + line 1, then 2+2) and the
      // reader still gets lookahead — Namo isn't held out long when chanted.
      const isLeadIn = (s) => s.length <= 16 && /^(ན་མོ|ཨོཾ|ཧཱུྃ|ༀ)/.test(s);
      const merged = bo.length > 1 && isLeadIn(bo[0]);
      const mb = merged ? [bo[0] + " " + bo[1], ...bo.slice(2)] : bo;
      const me = merged && en.length > 1 ? [en[0] + " " + en[1], ...en.slice(2)] : en;
      const mz = merged && zh.length > 1 ? [zh[0] + " " + zh[1], ...zh.slice(2)] : zh;
      const mtr = merged && tr.length > 1 ? [tr[0] + " " + tr[1], ...tr.slice(2)] : tr;
      const mtrz = merged && trz.length > 1 ? [trz[0] + " " + trz[1], ...trz.slice(2)] : trz;
      // lines-per-screen from the real pada lengths (ignore the short opener)
      const body = merged ? bo.slice(1) : bo;
      const maxLen = body.reduce((m, l) => Math.max(m, l.length), 0);
      const n = maxLen > LONG_LINE ? 1 : N;
      const total = Math.max(mb.length, 1);

      for (let start = 0; start < total; start += n) {
        chunks.push({
          gi: chunks.length,
          sIdx: si, sId: sec.id, sTitle: sec.title, anytime: !!sec.anytime,
          vId: v.id, kind: v.kind,
          reference: v.reference || null,
          rubric: start === 0 && v.rubric ? v.rubric.bo : "",  // operator-only, first screen
          vStart: start === 0,
          sStart: vi === 0 && start === 0,
          lines: {
            bo: mb.slice(start, start + n),
            en: me.slice(start, start + n),
            zh: mz.slice(start, start + n),
          },
          tr: mtr.slice(start, start + n),  // transliteration for the English overlay
          tr_zh: mtrz.slice(start, start + n),  // Chinese phonetic for the zh overlay
          image: v.image || null,      // per-verse image (21 Tara portraits)
          vTitle: v.title || null,     // per-verse title override (Tara name), {bo,en,zh}
          boSingle: !!v.bo_single,     // Tibetan 4-line mode: keep this verse one screen at a time
          returnTo: start + n >= total && v.return_to ? v.return_to : null,  // operator-only return button after the verse's last screen
        });
      }
    });

    secEntry.lastChunk = chunks.length - 1;
  });

  return { content, chunks, sections };
}
