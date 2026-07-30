## `kornorm.phonology` — the Standard Pronunciation G2P engine

A rule-by-rule implementation of 표준발음법 (the Standard Korean Pronunciation rules, National Institute of Korean Language) on top of morphological analysis, with lexical pronunciations from 표준국어대사전 applied before any rule runs. No regex table to maintain, no hand-written exception list.

> [← back to the main README](../../README.md) · siblings: [`alphanumeric`](../alphanumeric/README.md) · [`heuristics`](../heuristics/README.md) · [`utils`](../utils/README.md)

### Entry points

```pycon
>>> from kornorm import apply_phonology
>>> apply_phonology("맑게 갠 하늘과 꽃잎", output_format="hangul")
'말께 갠 하늘과 꼰닙'
>>> from kornorm import PhonologicProcessor
>>> processor = PhonologicProcessor()          # loads pecab + the Arrow dictionary once
>>> processor("옷 입고 한 일", output_format="hangul")
'온 닙꼬 한 닐'
```

`apply_phonology` is a thin wrapper that keeps one module-level engine alive; `PhonologicProcessor` is that engine, callable like g2pK's `G2p`. For multiprocessing there is `worker_init` (`from kornorm.phonology.engine import worker_init`), meant as a `BatchPipeline` initializer so each worker builds its own engine exactly once.

The same engine's morphological analysis is exposed as `pos` — either the method on the processor or the module-level wrapper (`from kornorm.phonology import pos`), which reuses the same shared engine:

```pycon
>>> from kornorm.phonology import pos
>>> pos("맑게 갠 하늘")
[('맑', 'VA'), ('게', 'EC'), ('갠', 'VV+ETM'), ('하늘', 'NNG')]
>>> pos("낮 한때", drop_space=False)
[('낮', 'NNG'), (' ', 'SP'), ('한', 'XSA+ETM'), ('때', 'NNG')]
```

What comes back is **the engine's view**, not vanilla pecab: the [dictionary patch](../utils/README.md) has been applied, numeral headwords are merged back together (육/NR+이/NR+오/NR → `('육이오', 'NNG')`), and surfaces that cannot decompose into syllables are re-classed as symbols (`('漢字', 'SH')`). Spaces are dropped by default, pecab-style; pass `drop_space=False` to keep them.

| `output_format` | `"독립문"` becomes | Codepoints |
|---|---|---|
| `"positional"` (default) | 동님문 | conjoining jamo, `U+1103 U+1169 U+11BC …` |
| `"compat"` | ㄷㅗㅇㄴㅣㅁㅁㅜㄴ | compatibility jamo, `U+3137 U+3157 U+3147 …` |
| `"hangul"` | 동님문 | composed syllables, `U+B3D9 U+B2D8 U+BB38` |

`"positional"` keeps onsets and codas distinguishable, which is what a speech model usually wants (and is the `apply_phonology` default); `"hangul"` is what a human wants to read. Note that `"positional"` renders as composed syllables in most fonts, so the first two rows look identical on screen while being entirely different strings.

Anything the analyzer tags as a symbol, a space, a Latin letter, a digit or a hanja is passed through by surface in every format — punctuation survives (`"같이 갈래?"` → `'가치 갈래?'`), and so does text the normalizer left behind (`"MP3 파일 목록"` → `'MP3 파일 몽녹'`). Surfaces that cannot decompose into syllables at all (raw hanja, bare jamo letters — `漢字`, `ㄱㄴㄷ`, `ㅋㅋㅋ`) are re-classed as symbols on the way in, even when the analyzer calls them nouns, so they take the same path.

### How a sentence flows

`PhonologicProcessor.__call__` is a flat sequence of pure `tokens → tokens` functions. Order is load-bearing where noted.

| Stage | What happens | Functions |
|---|---|---|
| tokenize | pecab morphological analysis; each token gets its jamo string, hanja flag, compound structure and dictionary pronunciation. Sino-Korean digit runs that form a headword are merged back into one token (육+이+오 → 육이오) | `_tokenize_and_tag`, `_merge_numeral_headwords` |
| 0. dictionary | lexical pronunciations applied up front, context-dependent homographs resolved | `apply_stdict_pronunciation`, `resolve_homograph` |
| 1. Sino-Korean words | 제20항 다만 (의견란류), 제26항 and the "-증" commentary | `norm20_p`, `norm26`, `norm26_c` |
| 2. compounds | 사이시옷 (제30항) then ㄴ-insertion (제29항) — 제29항 must run before the 제18항 addendum below | `norm30`, `norm29` |
| 3. absolute-final resolution | 제15항 and its proviso, before liaison can steal the coda | `norm15`, `norm15_p` |
| 4. vowels | 제5항 provisos 1–3 | `norm5_p1`, `norm5_p2`, `norm5_p3` |
| 5. representative sounds | 제10·11항 provisos, letter names (제16항) | `norm10_p`, `norm11_p`, `norm16` |
| 6. fortis | 제24·25·27항 and the 제27항 addendum | `norm24`, `norm25`, `norm27`, `norm27_a` |
| 7. palatalization | 제17항 and its addendum | `norm17`, `norm17_a` |
| 8. ㅎ aspiration | the 제12항 cases the LUT must not see | `norm12_1_c`, `norm12_1_a2` |
| 9. cohesive nasalization | 제18항 붙임, across a space | `norm18_a` |
| 10. **the 2D LUT** | every unconditional coda×onset interaction, in one O(1) lookup | `apply_phonology_lut` |
| 11. liaison | 제13·14항 and 제12항 4 (ㅎ deletion + liaison) | `norm13`, `norm14`, `norm12_4` |

Naming: `normN` is the rule itself, `_p` a 다만 (proviso), `_a` a 붙임 (addendum), `_c` a 해설 (commentary). Chapter files carry the full text of every rule — Korean and English — above each function, with a link to the official page, so the source doubles as the reference.

### Rule coverage

Every rule of 표준발음법 is present in the source. Some are implemented as functions, some are compiled into the LUT (those functions raise `NotImplementedError` pointing at `apply_lut`), and one is delegated to the dictionary. All examples below are actual engine output.

**Chapter 1 — 총칙** (`chapter1.py`) · 제1항 is the governing principle; no code.

**Chapter 2 — 자음과 모음** (`chapter2.py`)

| Rule | Where | Example |
|---|---|---|
| 제2·3·4항 (inventories) | premise of `utils/jamo.py` | — |
| 제5항 다만 1 — 용언 져/쪄/쳐 → [저/쩌/처] | `norm5_p1` | 가져 → 가저, 다쳐 → 다처 |
| 제5항 다만 2 — ㅖ → [ㅔ] except 예·례 | `norm5_p2` | 계집 → 게집, 상견례 → 상견녜 |
| 제5항 다만 3 — consonant + ㅢ → [ㅣ] | `norm5_p3` | 무늬 → 무니, 늴리리 → 닐리리, 희망 → 히망 |
| 제5항 다만 4 — non-initial 의 → [이], particle 의 → [에] | `norm5_p4_1`, `norm5_p4_2` — **off by default** (allowed variant) | 우리의 뜻 → 우리의 뜯 |

**Chapter 3 — 음의 길이** (`chapter3.py`) · 제6·7항 are documented but deliberately not implemented: KorNorm follows the common transcription convention of leaving vowel length unmarked.

**Chapter 4 — 받침의 발음** (`chapter4.py`)

| Rule | Where | Example |
|---|---|---|
| 제8항 — seven codas | premise of the LUT | — |
| 제9항 — ㄲ ㅋ ㅅ ㅆ ㅈ ㅊ ㅌ ㅍ → [ㄱ ㄷ ㅂ] | LUT | 닦다 → 닥따, 덮다 → 덥따 |
| 제10항 — ㄳ ㄵ ㄼ ㄽ ㄾ ㅄ | LUT | 넋 → 넉, 넓다 → 널따, 없다 → 업따 |
| 제10항 다만 — 밟-, 넓죽/넓둥글- | `norm10_p` | 밟다 → 밥따, 넓죽하다 → 넙쭈카다 |
| 제11항 — ㄺ ㄻ ㄿ | LUT | 닭 → 닥, 젊다 → 점따, 읊다 → 읍따 |
| 제11항 다만 — ㄺ before ㄱ | `norm11_p` | 맑게 → 말께, 얽거나 → 얼꺼나 |
| 제12항 1 — ㅎ + ㄱㄷㅈ | LUT | 놓고 → 노코, 닳지 → 달치 |
| 제12항 1 해설 — ㅎ + 한자어 -증(症) is fortis, not aspirated | `norm12_1_c` | 싫증 → 실쯩, 건조증 → 건조쯩 |
| 제12항 1 붙임 1 — ㄱ(ㄺ) ㄷ ㅂ(ㄼ) ㅈ(ㄵ) + ㅎ | LUT | 각하 → 가카, 넓히다 → 널피다, 꽂히다 → 꼬치다 |
| 제12항 1 붙임 2 — ㅅ ㅈ ㅊ ㅌ + ㅎ, including across a space | `norm12_1_a2` | 숱하다 → 수타다, 옷 한 벌 → 오 탄 벌, 낮 한때 → 나 탄때 |
| 제12항 2 — ㅎ + ㅅ | LUT | 닿소 → 다쏘, 많소 → 만쏘 |
| 제12항 3 — ㅎ + ㄴ | LUT | 놓는 → 논는, 않네 → 안네 |
| 제12항 4 — ㅎ dropped before a vowel | `norm12_4` | 낳은 → 나은, 싫어도 → 시러도 |
| 제13항 — liaison to a functional morpheme | `norm13` | 깎아 → 까까, 꽃을 → 꼬츨 |
| 제14항 — liaison of a double coda | `norm14` | 넋이 → 넉씨, 값을 → 갑쓸, 읊어 → 을퍼 |
| 제15항 — representative sound before a lexical morpheme | `norm15` | 밭 아래 → 바 다래, 겉옷 → 거돋, 헛웃음 → 허두슴 |
| 제15항 다만 — 맛있다·멋있다 | `norm15_p` | 맛있다 → 마싣따 |
| 제15항 붙임 — double coda in the same environment | `norm15` | 넋 없다 → 너 겁따, 값있는 → 가빈는 |
| 제16항 — letter names | `norm16` | 디귿이 → 디그시, 히읗이 → 히으시 |

**Chapter 5 — 음의 동화** (`chapter5.py`)

| Rule | Where | Example |
|---|---|---|
| 제17항 — palatalization ㄷㅌ + 이 | `norm17` | 굳이 → 구지, 밭이 → 바치 |
| 제17항 붙임 — ㄷ + 히 | `norm17_a` | 굳히다 → 구치다, 묻히다 → 무치다 |
| 제18항 — nasalization | LUT | 국물 → 궁물, 앞마당 → 암마당, 없는 → 엄는 |
| 제18항 붙임 — across a cohesive space | `norm18_a` | 밥 먹는다 → 밤 멍는다, 책 넣는다 → 챙 넌는다 |
| 제19항 (+붙임) — ㄹ nasalized | LUT | 담력 → 담녁, 막론 → 망논, 법리 → 범니 |
| 제20항 (+붙임) — lateralization | LUT | 신라 → 실라, 광한루 → 광할루, 닳는 → 달른 |
| 제20항 다만 — the ㄴ-reading words | `norm20_p` + dictionary | 의견란 → 의견난, 공권력 → 공꿘녁, 입원료 → 이붠뇨 |
| 제21항 — no over-assimilation | nothing to implement: the rule forbids a change, so the LUT simply has no such cell | 감기 → 감기 (never 강기), 옷감 → 옫깜, 문법 → 문뻡 |
| 제22항 (+붙임) — 어 → [여], 오 → [요] | `norm22`, `norm22_a` — **off by default** (allowed variant) | 피어 → 피어, 되어 → 되어 |

**Chapter 6 — 경음화** (`chapter6.py`)

| Rule | Where | Example |
|---|---|---|
| 제23항 — after an obstruent coda | LUT | 국밥 → 국빱, 옆집 → 엽찝, 값지다 → 갑찌다 |
| 제24항 — verb stem ㄴ(ㄵ) ㅁ(ㄻ) + ending | `norm24` | 앉고 → 안꼬, 젊지 → 점찌 |
| 제25항 — verb stem ㄼ ㄾ + ending | `norm25` | 넓게 → 널께, 훑소 → 훌쏘 |
| 제26항 (+다만) — Sino-Korean ㄹ + ㄷㅅㅈ | `norm26` | 발전 → 발쩐, 물질 → 물찔; 허허실실 → 허허실실 |
| 제26항 해설 — suffixal 증(症·證) is fortis after any noun, not just after ㄹ | `norm26_c` | 갈증 → 갈쯩, 스마트폰 중독증 → 스마트폰 중독쯩 |
| 제27항 — after the prospective ending -(으)ㄹ | `norm27` | 할 것을 → 할 꺼슬, 만날 사람 → 만날 싸람 |
| 제27항 붙임 — the closed list of -(으)ㄹ forms | `norm27_a` | 할걸 → 할껄, 할수록 → 할쑤록, 할진대 → 할찐대 |
| 제28항 — fortis in genitive compounds | dictionary (not generalizable as a rule) | 문고리 → 문꼬리, 손등 → 손뜽, 길가 → 길까 |

**Chapter 7 — 음의 첨가** (`chapter7.py`)

| Rule | Where | Example |
|---|---|---|
| 제29항 — ㄴ-insertion at a compound boundary | `norm29` | 솜이불 → 솜니불, 색연필 → 생년필, 늑막염 → 능망념 |
| 제29항 붙임 1 — insertion after ㄹ | `norm29` | 들일 → 들릴, 서울역 → 서울력, 휘발유 → 휘발류 |
| 제29항 붙임 2 — across a cohesive space | `norm29` + `_is_cohesive_boundary` | 한 일 → 한 닐, 옷 입다 → 온 닙따, 못 이겨 → 몬 니겨 |
| 제29항 다만 — read as written | dictionary | 등용문 → 등용문 |
| 제30항 — 사이시옷 | `norm30` | 콧등 → 코뜽, 뱃머리 → 밴머리, 나뭇잎 → 나문닙 |

### The 2D LUT — `apply_lut.py`

`PHONOLOGY_LUT[coda][onset] = (new_coda, new_onset, rule_id)`. Every unconditional interaction between an adjacent coda and onset — nasalization, lateralization, aspiration, fortis, representative sounds — is precomputed into a single cell, so chained changes need no rule ordering at all. The classic 법리 → 법니 (제19항) → 범니 (제18항) is one lookup, and the `rule_id` in each cell records which rules the cell compresses.

The table is laid out in 훈민정음 consonant order: 27 codas × the onsets each one actually interacts with, 411 cells in all, plus a synthetic `<EOW>` onset standing for word-final position.

Two policies matter:

- **A space is word-final.** A coda before a space is only reduced to its representative sound (옷 두 벌 → 옫 두 벌); anything that must cross a space is the business of a rule function that decides its own space policy (`norm15`, `norm12_1_a2`, `norm27`, `norm18_a`, `norm29`). g2pK applies its table regardless of spacing, which over-fires: 시를 읊어 comes out `'시르 를퍼'` there and `'시를 을퍼'` here.
- **Token-internal boundaries are scanned too**, so compounds the analyzer left whole still get their internal syllable-boundary changes.

### Dictionary-first — `apply_stdict_pronunciation`

Before any rule runs, tokens are looked up in a compiled 표준국어대사전 (double-array trie over Arrow IPC, memory-mapped and zero-copy) and lexical pronunciations are written straight into the jamo string. This is what replaces g2pK's `idioms.txt`: 대관령[대괄령] versus 동원령[동원녕] is a dictionary fact, not a rule.

Details that took a while to get right, and that a subclass should not undo:

- **Word-final codas keep the surface form.** Dictionary pronunciations are citation forms with final neutralization already applied; restoring the coda is what keeps 나뭇잎[나문닙] → 나뭇잎이[나문니피] working.
- **Only N / M / XR / V\* tokens are eligible**, so an ending never collides with a homographic headword (the ending 다가 versus 多價[다까]).
- **Verb stems are looked up as stem + 다** and the final syllable of the result is trimmed (설익다[설릭따] → stem 설릭). A direct hit on the stem itself is discarded, because homographic nouns would poison it (감돌다's stem versus the noun 감돌[감똘]).
- **Substituted tokens are marked** `stdict_applied`, which spelling-based rules check so they cannot re-transform a pronunciation-derived jamo (협의 stays [혀븨]).
- A pronunciation identical to the spelling is not substituted, but it is still positive evidence for 제29항 다만 ("read as written" — 등용문).

### Word-boundary policy and cohesion — `common.py`

There is no global "cross word boundary" switch. Each rule decides, and rules that may cross a space ask whether the two 어절 are cohesive enough to be "pronounced as one phrase", judged on the POS pair around the space:

- `_is_cohesive_boundary` (제29항 붙임 2): bare substantive + predicate, determiner/numeral + substantive, adnominal ending + substantive, adverb + predicate — 한 일 → 한 닐, 옷 입다 → 온 닙따.
- `_is_tight_cohesive_boundary` (제18항 붙임): bare noun + predicate only, so 여덟 명 is left alone while 밥 먹는다 → 밤 멍는다.
- `_ends_with_functional`: an 어절 that ends in a particle or ending is never the left half of a cohesive pair — a pause is available there.

`_is_functional` is the shared test for "is the next morpheme a functional one", used by liaison (제12항 4, 제13·14항), absolute-final resolution (제15항), letter names (제16항) and palatalization (제17항) alike, so those rules can never disagree with each other. It also corrects two known pecab mis-taggings rather than special-casing the words involved.

### Context-dependent homographs — `homographs.py`

The dictionary resource can carry one pronunciation per surface form, so surface forms whose reading depends on context are listed separately with cue words and a default. The decision is a majority vote over co-occurring tokens.

```pycon
>>> processor("이불을 깔고 잠자리에 들었다", output_format="hangul")   # bedding
'이부를 깔고 잠짜리에 드럳따'
>>> processor("여름 잠자리를 잡았다", output_format="hangul")         # dragonfly
'여름 잠자리를 자받따'
```

`CONTEXT_HOMOGRAPHS` is a deliberately closed, curated list — an approximation, and documented as one.

### Customizing the pipeline

Rules that ship implemented but switched off, because they are 허용 (allowed) variants rather than the principle form:

| Function | Rule | Effect if enabled |
|---|---|---|
| `norm5_p4_1`, `norm5_p4_2` | 제5항 다만 4 | non-initial 의 → [이], particle 의 → [에] |
| `norm22`, `norm22_a` | 제22항 (+붙임) | 어 → [여], 오 → [요] |

One allowed variant *is* on by default, as a deliberate exception: 제5항 다만 2 (ㅖ → [ㅔ]), because [ㅔ] dominates in ordinary speech and this matches common transcription practice.

To change the policy, subclass `PhonologicProcessor` and override `__call__`. There is no hook to register a rule into — the pipeline is a plain, readable sequence of function calls in `engine.py`, so overriding means copying that sequence and inserting (or dropping) the lines you want. Everything else — the tokenizer, the dictionary trie, the LUT — is loaded in `__init__` and inherited as is.

### Files

| File | Contents |
|---|---|
| `engine.py` | `PhonologicProcessor`, `apply_phonology`, `worker_init`, the dictionary pass, tokenization |
| `chapter1.py` … `chapter7.py` | the rules, one file per chapter of 표준발음법, full rule text included |
| `apply_lut.py` | `PHONOLOGY_LUT` and `apply_phonology_lut` |
| `common.py` | `MorphToken`, `FORTIS_MAPPING`, POS tag sets, the functional-morpheme and cohesion tests |
| `homographs.py` | `CONTEXT_HOMOGRAPHS`, `resolve_homograph` |
| `_resources/` | `stdict_words.arrow` (9 MB) and `stdict_arrays.arrow` (33 MB) — the compiled dictionary, shipped inside the wheel |

### Limitations

- Input is expected to be normalized hangul. Run [`dealers_choice`](../alphanumeric/README.md) first (or call `normalize`) — digits and Latin letters reaching the engine are not pronunciations the rules can work with.
- 제6·7항 (vowel length) are not implemented, by convention.
- 제28항 has no rule implementation; it rides on the dictionary, so compounds outside 표준국어대사전 will not get their fortis.
- Context homographs are resolved by a cue vote, and the cue list is short.
- Bracket notation in the rules deletes spaces, which the engine does not: 낮 한때 is [나탄때] in the norm and `'나 탄때'` here. (Written closed, 낮한때 → `'나찬때'`.)
