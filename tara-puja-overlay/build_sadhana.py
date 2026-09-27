#!/usr/bin/env python3
# Build content.json for the 2-line overlay model from the Tibetan sadhana md.
# Menu sections = the `##` major headings, EXCEPT the big mandala ritual (4-0),
# which is split into named sub-parts (SUB4). Each verse has bo lines + en/zh
# placeholders, an optional controller-only rubric, and a kind (chant|mantra).
import json, re, sys

SRC = sys.argv[1]
OUT = sys.argv[2]

ID_RE = re.compile(r'\^([0-9]+(?:-[0-9]+)*)')
SMALL_RE = re.compile(r'<small>(.*?)</small>', re.DOTALL)
MANTRA_MARKERS = ["ཨོཾ", "ཧཱུྃ", "ཧཱུཾ", "སྭཱ་ཧཱ", "ཕཊ", "ཨཱཿ", "ཛཿ", "ཧོཿ", "བཛྲ", "ཨཱརྻ", "ༀ"]

# Section 4 (mandala ritual) sub-parts: block id where it begins -> (bo, en)
SUB4 = {
    "4-0":   ("སྐྱབས་སེམས།", "Refuge & Bodhichitta"),
    "4-6":   ("ཚོགས་བསགས།", "Accumulation (prostration, offering, confession)"),
    "4-14":  ("མཆོད་པ་བྱིན་རླབས།", "Blessing the offerings"),
    "4-18":  ("དཀོན་མཆོག་སྤྱི་མཆོད།", "Homage & offering to the Three Jewels"),
    "4-22":  ("ཡན་ལག་བདུན་པ།", "The Seven Branches"),
    "4-36":  ("མཎྜལ་འབུལ་བ།", "Mandala offering"),
    "4-44":  ("སྤྱན་འདྲེན་མཆོད་པ།", "Invitation & offering to Tārā"),
    "4-55":  ("ཕྱག་འཚལ་ཉེར་གཅིག", "Praise to the 21 Tārās"),
    "4-80":  ("སླར་ཡང་མཆོད་བསྟོད་ཕན་ཡོན།", "Repeated offerings, prostrations & benefits"),
    "4-105": ("གཏོར་མ།", "Torma offering"),
    "4-116": ("གསོལ་འདེབས་དང་བཟླས་པ།", "Supplication & mantra recitation"),
    "4-139": ("བསྔོ་སྨོན་ཤིས་བརྗོད།", "Dedication & auspicious verses"),
    "4-152": ("རྒྱུན་ཁྱེར།", "Condensed daily practice"),
}

raw = open(SRC, encoding="utf-8").read()
blocks = [b for b in re.split(r'\n\s*\n', raw) if b.strip()]

sections = []
cur = None
pending_rubric = []
in_s4 = False

def clean_title(t):
    t = re.sub(r'^#+\s*', '', t)
    t = ID_RE.sub('', t)
    return t.replace('༄༅། །', '').replace('༈', '').strip()

def is_mantra(lines):
    return len(lines) == 1 and any(m in lines[0] for m in MANTRA_MARKERS)

def flush_pending():
    global pending_rubric
    if pending_rubric and cur and cur["verses"]:
        tail = " ".join(pending_rubric)
        v = cur["verses"][-1]
        v["rubric"] = {"bo": (v["rubric"]["bo"] + " " + tail).strip()} if v["rubric"] else {"bo": tail}
    pending_rubric = []

def open_section(bid, title_bo, title_en=""):
    global cur
    flush_pending()
    cur = {"id": f"s{len(sections)+1}", "bid": bid,
           "title": {"bo": title_bo, "en": title_en, "zh": ""}, "verses": []}
    sections.append(cur)

for blk in blocks:
    mid = ID_RE.search(blk)
    bid = mid.group(1) if mid else None
    text = ID_RE.sub('', blk).rstrip()

    # doc title (single #) — skip
    if text.lstrip().startswith('# ') and not text.lstrip().startswith('## '):
        continue

    # major `##` heading
    if text.lstrip().startswith('## '):
        if bid == "4-0":
            in_s4 = True
            open_section(bid, *SUB4["4-0"])
        else:
            in_s4 = False
            open_section(bid, clean_title(text))
        continue

    if cur is None:
        continue

    # sub-part boundary inside section 4
    if in_s4 and bid in SUB4 and bid != "4-0":
        open_section(bid, *SUB4[bid])

    smalls = [s.strip() for s in SMALL_RE.findall(text)]
    body = SMALL_RE.sub('', text).strip()
    lines = [ln.strip() for ln in body.split('\n') if ln.strip()]

    if not lines:
        if smalls:
            pending_rubric.extend(smalls)
        continue

    rubric = " ".join(pending_rubric + smalls).strip()
    pending_rubric = []
    cur["verses"].append({
        "id": bid,
        "kind": "mantra" if is_mantra(lines) else "chant",
        "rubric": {"bo": rubric} if rubric else None,
        "lines": {"bo": lines, "en": [], "zh": []},
    })

flush_pending()

doc = {
    "_README": ("Zabtik Drolchok overlay content. Left-menu = sections; section 4 (the mandala "
                "ritual) is split into named sub-parts. Each verse has bo lines (filled) and en/zh "
                "placeholders (empty arrays — fill to enable those overlays). `rubric` is operator-only "
                "helper text shown in the controller, never on the overlays. The engine chunks each "
                "verse's lines into 2-line pairs."),
    "languages": ["bo", "en", "zh"],
    "lines_per_screen": 2,
    "sections": sections,
}
json.dump(doc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

nv = sum(len(s["verses"]) for s in sections)
print(f"sections: {len(sections)}  verses: {nv}")
for s in sections:
    vl = sum(len(v['lines']['bo']) for v in s['verses'])
    print(f"  {s['id']} ({s['bid']}): {len(s['verses'])} verses, {vl} lines — {s['title']['bo'][:40]}  [{s['title']['en']}]")
