#!/usr/bin/env python3
# Build content.json from the EXPANDED sadhana source (bo-...གཤམ་ཡིག.md).
# ##-level section titles are READ FROM THE VAULT heading verbatim, minus only
# the leading ༄༅། །/༈ ornament glyphs. Sub-part sections (from inline rubrics,
# no ## title in the vault) use curated labels. Padas are Tibetan-anchored:
# each Tibetan line = one pada; following Latin lines are translit then English.
import json, re, sys

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
DRY = "--dry" in sys.argv

TIB = re.compile(r'[ཀ-ྼ]')  # Tibetan letters only (excludes ༔ ། ༄ punctuation)
SMALL = re.compile(r'<small>(.*?)</small>')
LEAD = re.compile(r'^[\s༄༅༆༇༈།༎༿༾]+')
MANTRA = ["ཨོཾ","ཧཱུྃ","ཧཱུཾ","སྭཱ་ཧཱ","སྭཱཧཱ","ཕཊ","ཨཱཿ","ཛཿ","ཧོཿ","བཛྲ","ༀ","ཨ་མྲྀ་ཏ","སྭ་བྷཱ","ཨཱརྻ","མཱུྃ"]

# (line, id, curated_bo, curated_en). bo/en=None -> read the ## heading from source.
BOUNDS = [
 (3,    "s1",  None, None),
 (208,  "s2",  None, None),
 (293,  "s3",  None, None),
 (312,  "s4",  None, None),
 (331,  "s5",  "སྐྱབས་སེམས།", "Refuge & Bodhichitta"),
 (351,  "s6",  "ཚོགས་བསགས།", "Accumulation (prostration, offering, confession)"),
 (445,  "s7",  "མཆོད་པ་བྱིན་རླབས།", "Blessing the offerings"),
 (476,  "s8",  "དཀོན་མཆོག་སྤྱི་མཆོད།", "Homage & offering to the Three Jewels"),
 (499,  "s9",  "ཡན་ལག་བདུན་པ།", "The Seven Branches"),
 (758,  "s10", "སྤྱན་འདྲེན་མཆོད་པ།", "Invitation & offerings to Tārā"),
 (1563, "s11", "ཕྱག་འཚལ་ཉེར་གཅིག", "Praise to the 21 Tārās"),
 (1940, "s12", "གཏོར་མ།", "Torma offering"),
 (2037, "s13", "གསོལ་འདེབས་དང་བཟླས་པ།", "Supplication & mantra recitation"),
 (2224, "s14", "བསྔོ་སྨོན་ཤིས་བརྗོད།", "Dedication & auspicious verses"),
 (2360, "s15", None, None),
 (3254, "s16", None, None),
 (3716, "s17", None, None),
 (3817, "s18", None, None),
 (3933, "s19", None, None),
 (4046, "s20", None, None),
 (4249, "s21", None, None),
 (4292, "s22", None, None),
]

lines = open(SRC, encoding="utf-8").read().split("\n")
Ntot = len(lines)

def strip_lead(t):
    return LEAD.sub("", re.sub(r'^#+\s*', "", t)).strip()

def header_titles(ln):  # ln = 1-indexed source line of the ## heading
    bo = strip_lead(lines[ln-1])
    en = ""
    for j in range(ln, min(ln+3, Ntot)):
        s = lines[j].strip()
        if not s: continue
        if not TIB.search(s): en = s
        break
    return bo, en

def sec_for(lineno):
    idx=-1
    for i,b in enumerate(BOUNDS):
        if lineno>=b[0]: idx=i
    return idx

blocks=[]; i=0
while i<Ntot:
    if lines[i].strip()=="": i+=1; continue
    start=i+1; buf=[]
    while i<Ntot and lines[i].strip()!="": buf.append(lines[i]); i+=1
    blocks.append((start,buf))

sections=[]
for ln,sid,cbo,cen in BOUNDS:
    bo,en = header_titles(ln) if cbo is None else (cbo,cen)
    sections.append({"id":sid,"title":{"bo":bo,"en":en,"zh":""},"verses":[]})

pending={"bo":"","en":""}; anomalies=[]
def add_pending(s):
    s=s.strip()
    if not s: return
    if TIB.search(s): pending["bo"]=(pending["bo"]+" "+s).strip()
    else: pending["en"]=(pending["en"]+" "+s).strip()
def is_mantra(bo): return len(bo)==1 and any(m in bo[0] for m in MANTRA)

def parse_padas(vl,start):
    bo=[];tr=[];en=[];j=0;lead=[]
    while j<len(vl) and not TIB.search(vl[j]): lead.append(vl[j]); j+=1
    if lead:
        anomalies.append((start,"lead-latin",lead[0][:34]))
        for l in lead: add_pending(l)
    while j<len(vl):
        bo.append(vl[j]); j+=1; t="";e=""
        if j<len(vl) and not TIB.search(vl[j]): t=vl[j]; j+=1
        if j<len(vl) and not TIB.search(vl[j]): e=vl[j]; j+=1
        ex=0
        while j<len(vl) and not TIB.search(vl[j]): e=(e+" "+vl[j]).strip(); j+=1; ex+=1
        if ex: anomalies.append((start,"extra-latin",vl[max(0,j-1)][:30]))
        tr.append(t); en.append(e)
    return bo,tr,en

for start,buf in blocks:
    si=sec_for(start)
    if si<0: continue
    sec=sections[si]; text="\n".join(buf); first=buf[0].lstrip()
    if first.startswith("# ") and not first.startswith("## "): continue
    if first.startswith("## "): continue
    if "<small>" in text and all(("<small>" in l or l.strip()=="") for l in buf):
        for s in SMALL.findall(text): add_pending(s)
        continue
    for s in SMALL.findall(text): add_pending(s)
    vl=[SMALL.sub("",l).strip() for l in buf]; vl=[l for l in vl if l]
    if not vl: continue
    if not any(TIB.search(l) for l in vl):
        for l in vl: add_pending(l)
        continue
    bo,tr,en=parse_padas(vl,start)
    if not bo: continue
    rub=None
    if pending["bo"] or pending["en"]:
        rub={k:v for k,v in pending.items() if v}; pending={"bo":"","en":""}
    sec["verses"].append({"id":f"{sec['id']}-{len(sec['verses'])+1}",
        "kind":"mantra" if is_mantra(bo) else "chant","rubric":rub,
        "lines":{"bo":bo,"en":en,"zh":[]},"tr":tr})

if not DRY:
    print("titles from source (##-level) + curated (sub-parts):")
    for s in sections: print(f"  {s['id']:4} {s['title']['en'][:60]}")
tot_v=sum(len(s['verses']) for s in sections)
print(f"verses={tot_v}  anomalies={len(anomalies)}")
if OUT and not DRY:
    doc={"_README":"Rebuilt from expanded source. ##-titles verbatim from vault (minus lead ornaments); sub-part titles curated. bo+tr+en filled; zh empty except preserved test-t21.",
         "languages":["bo","en","zh"],"lines_per_screen":2,"sections":sections}
    json.dump(doc,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("WROTE",OUT)
