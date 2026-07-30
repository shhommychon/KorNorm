## `kornorm.utils` — jamo primitives and the pecab patcher

Two low-level pieces the rest of the library stands on: a jamo layer that refuses to confuse an onset with a coda, and a one-time patch that teaches pecab's dictionary to split the compounds a pronunciation engine needs split.

> [← back to the main README](../../README.md) · siblings: [`alphanumeric`](../alphanumeric/README.md) · [`phonology`](../phonology/README.md) · [`heuristics`](../heuristics/README.md)

### `jamo.py` — positional jamo

Korean letters have two Unicode lives: the compatibility jamo block (`U+313x`, where ㄱ-as-onset and ㄱ-as-coda are the same character) and the conjoining block (`U+11xx`, where they are not). A G2P engine that uses the first will eventually apply a coda rule to an onset. KorNorm uses the second everywhere internally.

Constants are named for their position, so the position is visible at the call site:

| Prefix | Range | Count | Example |
|---|---|---|---|
| `O_*` — onset | `U+1100`–`U+1112` | 19 | `O_GIYEOK` = `'ᄀ'` |
| `N_*` — nucleus | `U+1161`–`U+1175` | 21 | `N_A` = `'ᅡ'` |
| `C_*` — coda | `U+11A8`–`U+11C2` | 27 | `C_GIYEOK` = `'ᆨ'` |
| `C_NONE` | `U+3164` | 1 | Hangul Filler, "this syllable has no coda" |

`C_NONE` is not decoration. Every syllable is stored as exactly three characters, so the engine can slice a jamo string in steps of three and know that index `i+2` is a coda — the LUT scan, the intra-token walk and the output formatter all depend on it.

| Function | Does | Example |
|---|---|---|
| `split_syllable_char(char)` | one syllable → `(onset, nucleus, coda)`; a codaless syllable gets `C_NONE`, a non-hangul character comes back as `(char, '', '')` | `'먹'` → `('ᄆ', 'ᅥ', 'ᆨ')`, `'가'` → `('ᄀ', 'ᅡ', C_NONE)` |
| `decompose(text)` | flattens a whole string; non-hangul passes through untouched | `"먹다"` → `U+1106 U+1165 U+11A8 U+1103 U+1161 U+3164` |
| `join_jamos(cho, joong, jong='')` | rebuilds one syllable; an empty or `C_NONE` coda means none, and invalid input is returned concatenated rather than raising | `('ᄆ', 'ᅥ', 'ᆨ')` → `'먹'` |
| `to_compat_jamo(jamo_str)` | positional jamo → the compatibility block, for display or for models trained on it | `decompose("먹다")` → `'ㅁㅓㄱㄷㅏ'` |

These are what the engine's three `output_format` modes are built from: `"positional"` is the raw jamo string with the fillers stripped, `"compat"` runs `to_compat_jamo`, and `"hangul"` runs `join_jamos` over every group of three.

### `_patch_pecab.py` — the dictionary patch

pecab ships a MeCab-style dictionary in which many compounds are registered as a single lexical entry. That is right for parsing and wrong for pronunciation: when the analyzer never exposes the morpheme boundary, 제15항 cannot fire and plain liaison (제13항) wins instead — the module's own example is 느닷없이 coming out [느다섭씨]. The fix runs once, at first engine construction, and rewrites the installed dictionary.

```python
from kornorm.utils._patch_pecab import patch_pecab_dictionary_if_needed

patch_pecab_dictionary_if_needed()   # called automatically by PhonologicProcessor.__init__
```

Three channels, all applied in one dictionary rebuild:

| Channel | Purpose | Example |
|---|---|---|
| `MORPHEMES_TO_EXCLUDE` | drop entries that hide a morpheme boundary | 겉옷, 값어치, 서울역, … (945 entries) |
| `WORD_COSTS_TO_SET` | lower a noun's cost so the headword analysis wins over a fragment analysis in isolated input | 길가, 말살, 절도, 줄넘기 |
| `MORPHEMES_TO_ADD` | add a 표준국어대사전 headword pecab lacks, cloning the attributes of a same-class noun | 입원료 (missing → mis-parsed as 입 + 원료 → [이붤료]) |

This is the sanctioned channel for tagging problems. Rule code does not carry lexical exception tuples — when the analyzer is wrong about a word, the dictionary gets fixed, not the rule. (The one exception is a closed grammatical list the norm itself enumerates, such as the 제27항 붙임 endings.)

Mechanics worth knowing:

- **`PATCH_REVISION`** is written into a marker file (`.kornorm_patched`) inside pecab's resource directory. A matching revision short-circuits the whole function, so startup stays fast; bump the constant when the lists change and every installation re-patches itself on next run. All three operations are idempotent.
- The rebuild follows pecab's own build path — surface merging with `'|'`, `DoubleArrayTrie` construction, Arrow IPC serialization — so the result is a dictionary pecab reads natively.
- The marker file is appended to pecab's `RECORD`, so `pip uninstall pecab` removes it too.
- Because the installed dictionary itself is rewritten, a `Pecab()` you construct yourself in the same environment also uses the patched dictionary. This is the intended contract — the patch fixes pronunciations the stock dictionary gets wrong, and there is one dictionary per environment — but if you need stock pecab behavior, use a separate environment.
- **It writes into `site-packages`.** In a read-only environment (a locked-down container, for example) the first call fails; run it once where the filesystem is writable. Redirecting the cache elsewhere was considered and rejected.

The first run prints a short notice and takes a while — it rebuilds the whole trie, which together with the CMU dictionary download in `alphanumeric` is where the ~40 seconds of first-call setup goes. Every later run does nothing but read one small file.
