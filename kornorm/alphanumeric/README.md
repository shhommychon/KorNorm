## `kornorm.alphanumeric` — text normalization

Everything in a Korean sentence that is not hangul yet: digits, units, currencies, symbols, abbreviations and English words. Every conversion is a standalone pure function (`str` → `str`) that can be used on its own, and `dealers_choice` is the house preset that runs them in an order that works. Nine converters also have read-only `find_` twins that report matches without rewriting anything ([Finders](#finders--detect-without-touching)).

> [← back to the main README](../../README.md) · siblings: [`phonology`](../phonology/README.md) · [`heuristics`](../heuristics/README.md) · [`asia`](../asia/README.md) · [`utils`](../utils/README.md)

### The preset — `dealers_choice`

```pycon
>>> from kornorm import dealers_choice
>>> dealers_choice("2026.07.30 오후 3:15에 만나자")
'이천이십육년 칠월 삼십일 오후 세시 십오분에 만나자'
>>> dealers_choice("이 old school 감성의 MP3 파일은 3.5MB밖에 안 한다")
'이 올드 스쿨 감성의 엠피쓰리 파일은 삼 쩜 오메가바이트밖에 안 한다'
```

Fourteen steps, in this order:

| # | Step | Functions |
|---|---|---|
| 1 | strip thousands separators | `remove_commas` |
| 2 | currencies | `read_currencies` |
| 3 | phone numbers | `read_phone_number` |
| 4 | dates and times | `read_date_format`, `read_time_format` |
| 5 | interpunct digit readings (6·25 → 육이오) | `read_interpunct_digits` |
| 6 | units | `read_unit_exceptions`, `read_units` |
| 7 | decimal points | `read_decimal_point` |
| 8 | letter+digit tokens (H2O → 에이치투오) | `read_alphanum_combos` |
| 9 | all-caps abbreviations | `read_abbreviations` |
| 10 | numerals — bound (native) then standalone (Sino) | `convert_bound_numerals`, `convert_standalone_numerals` |
| 11 | stray symbols and Greek letters | `read_special_symbols` |
| 12 | numeral exceptions (육월 → 유월) | `fix_num_exceptions` |
| 13 | English words via CMU dict | `read_english_words` |
| 14 | leftover Latin letters, read as letter names | `alphabet_to_hangul` |

The order is load-bearing in two places. Units run **before** the decimal point — run it the other way around and `3.5GHz` is already `삼 쩜 오GHz`, so the unit pattern (digit + unit) no longer matches. English words run **last but one**, because the CMU dictionary happily reads things that were meant to be read as letters or units: on its own, `read_english_words("NASA")` gives `'내서'` and `read_english_words("hz")` gives `'허트즈'`.

### Numerals and letters — `base.py`

| Function | Does | Example |
|---|---|---|
| `num_to_sino(num_str)` | digits → Sino-Korean cardinal; a bare `0` reads 영, and a multi-digit number with a leading zero is a code, read digit by digit | `"1950"` → `'천구백오십'`, `'0'` → `'영'`, `"007"` → `'공공칠'` |
| `num_to_native(num_str)` | digits → native Korean numeral, mixing in Sino above 100 (with the 스물 → 스무 exception) | `"21"` → `'스물한'`, `"108"` → `'백여덟'` |
| `alphabet_to_hangul(char)` | one Latin letter → its Korean letter name; anything else passes through | `'q'` → `'큐'`, `'Z'` → `'즤'` |

### Numbers in context — `contextual_numbers.py`

| Function | Does | Example |
|---|---|---|
| `remove_commas` | drops `,` between digit groups only | `"45,000원"` → `'45000원'` |
| `read_phone_number` | reads digits one by one, drops the separators (a leading space is a word boundary, not a separator — it stays); `0` is 공 by default | `"010-1234-5678"` → `'공일공일이삼사오육칠팔'` |
| `read_date_format` | `YYYY.MM.DD` / `-` / `/` → 년 월 일, leading zeros dropped | `"1950-06-25 발발"` → `'1950년 6월 25일 발발'` |
| `read_time_format` | `HH:MM[:SS]` → 시 분 초 | `"1:02:03"` → `'1시 2분 3초'` |
| `read_decimal_point` | fraction digits read one by one | `"3.14"` → `'3 쩜 일사'` |
| `read_interpunct_digits` | interpunct groups read digit-by-digit, not place-by-place | `"6·25"` → `'육이오'`, `"3·1절"` → `'삼일절'` |
| `convert_bound_numerals` | digits before a classifier → native numeral | `"커피 3잔"` → `'커피 세잔'`, `"20명"` → `'스무명'` |
| `convert_standalone_numerals` | every remaining digit run → Sino cardinal | `"1950년"` → `'천구백오십년'` |
| `fix_num_exceptions` | irregular readings after the fact | `"육월 십월"` → `'유월 시월'` |

### Symbols, units and abbreviations — `entities.py`

| Function | Does | Example |
|---|---|---|
| `read_currencies` | currency signs on either side of the amount | `"$5"` → `'5달러'`, `"￥300"` → `'300엔'` |
| `read_unit_exceptions` | idiomatic letter+digit tokens read as a block, guarded by token boundaries so it never eats part of a longer token | `"MP3 5G"` → `'엠피쓰리 파이브쥐'`, but `"15GB"` → `'15GB'` (left to `read_units`) |
| `read_units` | digit + unit → hangul, longest unit first, case-insensitive, optional space | `"70KG"` → `'70킬로그램'`, `"3.5GHz"` → `'3.5기가헤르츠'` |
| `read_alphanum_combos` | letter+digit tokens spelled out, digits read English-style | `"H2O"` → `'에이치투오'`, `"A4 용지"` → `'에이포 용지'` |
| `read_abbreviations` | runs of 2+ capitals (and `&`) spelled out | `"NASA"` → `'엔에이에스에이'` |
| `read_special_symbols` | operators, punctuation-as-words and Greek letters | `"A+ 100%"` → `'A플러스 100퍼센트'`, `"α선"` → `'알파선'` |

Multi-digit numbers are deliberately left out of `read_alphanum_combos`: `3M` is a letter block (쓰리엠), but `220V` should be read as a numeral plus a letter (이백이십븨), so only a single leading digit triggers the block reading.

### Finders — detect without touching

Nine converters have read-only `find_` twins that report exactly what the converter would rewrite, as `(start, end, match)` tuples against the original text — `text[start:end] == match` holds for each, and `read_X(text) != text` and `find_X(text) != []` always agree. Use them to profile a corpus before deciding which normalization steps it actually needs:

```pycon
>>> from kornorm.alphanumeric import find_units, find_bound_numerals, find_time_format
>>> find_units("배터리 3400mAh 용량과 30km 구간")
[(4, 11, '3400mAh'), (16, 20, '30km')]
>>> find_bound_numerals("커피 3잔과 장갑 3켤레")
[(3, 5, '3잔'), (10, 13, '3켤레')]
>>> find_time_format("회의는 9:30, 종료는 11:00")
[(4, 8, '9:30'), (14, 19, '11:00')]
```

| Finder | Twin of |
|---|---|
| `find_currencies` | `read_currencies` |
| `find_unit_exceptions` | `read_unit_exceptions` |
| `find_units` | `read_units` |
| `find_special_symbols` | `read_special_symbols` |
| `find_phone_number` | `read_phone_number` |
| `find_date_format` | `read_date_format` |
| `find_time_format` | `read_time_format` |
| `find_interpunct_digits` | `read_interpunct_digits` |
| `find_bound_numerals` | `convert_bound_numerals` |

Each finder mirrors its converter **run standalone** — the `dealers_choice` pipeline order is not simulated. `find_units("3.5GHz")` reports `(2, 6, '5GHz')`, exactly the span `read_units` rewrites on that raw string. One deliberate touch-up: `find_phone_number` trims the leading whitespace its pattern consumes, so the reported span starts at the number itself (`read_phone_number` likewise keeps that space instead of swallowing it). Conversions that a plain regex already finds (digit runs, decimal points, all-caps abbreviations, letter+digit combos) deliberately ship no finder.

### English words — `english.py`

`read_english_words` converts CMU-dictionary words to hangul through the 외래어 표기법 English transcription rules (제3장 제1절) rather than a lookup table of loanwords.

```pycon
>>> from kornorm.alphanumeric import read_english_words
>>> read_english_words("old school")
'올드 스쿨'
>>> read_english_words("computer")
'컴퓨터'
>>> read_english_words("quick")
'퀵'
>>> read_english_words("zzzq")   # not in the dictionary — left for step 14
'zzzq'
```

- ARPABET phonemes are mapped position-by-position (onset / nucleus / coda), with the glides `[j]`/`[w]` held as placeholders until they merge with the following vowel — which is why `computer` comes out 컴퓨터 and not 컴프유터.
- Replacement is bounded by Latin-letter context, not `\b`, so `"school이야"` → `'스쿨이야'` still fires.
- The dictionary is downloaded once on first use by `_fetch_cmudict.py` — straight from [cmusphinx/cmudict](https://github.com/cmusphinx/cmudict) into `_resources/cmudict.dict` (~3.6 MB), with no nltk in the picture. If the download fails, the function returns the text untouched and step 14 reads the letters out instead.
- Both the cmusphinx distribution (lowercase) and the original 0.7b format (uppercase, `;;;` comments) parse, and for words with several pronunciations the first one wins.

### Lookup tables — `constants.py`

All the maps and compiled patterns live in one module, and nearly every function takes its map as a keyword argument, so a variant reading is a call argument rather than a fork:

```pycon
>>> read_decimal_point("3.14", point_char=" 점 ")
'3 점 일사'
>>> read_phone_number("010-1234-5678", zero_char='영')
'영일영일이삼사오육칠팔'
```

| Table | Size | Used by |
|---|---|---|
| `SINO_DIGITS` / `SINO_TENS` / `SINO_THOUSANDS` | 10 / 4 / 13 | `num_to_sino` |
| `NATIVE_DIGITS` / `NATIVE_TENS` | 9 / 9 | `num_to_native` |
| `LATIN_MAP` | 26 | `alphabet_to_hangul` |
| `ENG_DIGITS` | 10 | `read_alphanum_combos` |
| `UNITS_MAP` | 228 | `read_units` |
| `CURRENCY_MAP` | 53 | `read_currencies` |
| `GREEK_MAP` | 48 | `read_special_symbols` |
| `SPECIAL_SYMBOL_MAP` / `SYMBOL_MAP` | 9 / 8 | `read_special_symbols`, `read_unit_exceptions` |
| `BOUND_NOUNS` | 52 | `RE_BOUND_NUM`, `convert_bound_numerals` |

### Notes

- `dealers_choice` produces normalized **hangul text**, not pronunciation. Feed its output to [`apply_phonology`](../phonology/README.md) when you want pronunciation too.
- Every function above is importable from the package itself (`from kornorm.alphanumeric import read_units`), and the submodule paths work too.
- Sources for the individual conversion tables and regexes are credited per-function in the docstrings, and collected in the main README.
