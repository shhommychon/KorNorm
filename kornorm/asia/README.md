## `kornorm.asia` — neighboring-language text → hangul readings

Korean text in the wild quotes its neighbors — a Japanese shop name in a review, a song title, a place name — and a TTS front-end has to say them somehow. This package converts those runs into hangul the way a Korean speaker would, following the official loanword transcription rules (외래어 표기법). Japanese is the first resident; the package name leaves room for more. Nothing here is part of `dealers_choice` — chain it yourself when your corpus needs it.

> [← back to the main README](../../README.md) · siblings: [`alphanumeric`](../alphanumeric/README.md) · [`phonology`](../phonology/README.md) · [`heuristics`](../heuristics/README.md) · [`utils`](../utils/README.md)

### `read_japanese` — Japanese → how a Korean would say it

Kana is already phonetic, so it converts straight through the official kana–hangul correspondence table (표4) with the transcription rules on top: word-initial か/た-row syllables come out unaspirated (도쿄, not 토쿄), the sokuon っ becomes a ㅅ batchim (삿포로), ん becomes ㄴ (센다이), and long vowels are not written out (규슈, 라멘). Kanji needs readings — those come from the `janome` morphological analyzer's pronunciation field when it is installed, which also fixes the particles whose spelling and sound differ (は read as 와, へ as 에).

```pycon
>>> from kornorm.asia import read_japanese
>>> read_japanese("カラオケ")
'가라오케'
>>> read_japanese("サッポロ")
'삿포로'
>>> read_japanese("오늘 ラーメン 먹었다")
'오늘 라멘 먹었다'
>>> read_japanese("私は東京へ行きます")     # with janome installed
'와타시와토쿄에이키마스'
>>> read_japanese("新幹線で京都まで")
'신칸센데쿄토마데'
>>> read_japanese("こんにちは")
'곤니치와'
```

| Argument | Default | Meaning |
|---|---|---|
| `convert_lone_kanji` | `False` | whether to read runs of kanji with no kana around them — in Korean text a bare CJK-ideograph run is usually hanja quoted in a Korean sentence, not Japanese, so they pass through unless you opt in (needs janome) |

```pycon
>>> read_japanese("東京")
'東京'
>>> read_japanese("東京", convert_lone_kanji=True)
'도쿄'
```

### The optional dependency

Kanji readings require [janome](https://github.com/mocobeta/janome), a pure-Python morphological analyzer (Apache-2.0, IPADIC bundled). It is deliberately not a hard dependency — most Korean corpora contain no Japanese:

```bash
pip install kornorm[ja]     # or kornorm[all]
```

Without it, kana still converts fine, but three things degrade — kanji stay untouched (`私は…` keeps its `私`), particles read literally (は as 하 instead of 와), and dictionary-resolved idioms are lost. A one-time notice explains exactly this when the fallback path first runs.

### Notes

- **Word-initial is judged once per Japanese run.** A standalone word matches the norm's examples (도쿄, 교토, 오사카); the same word mid-sentence keeps its aspirated onsets (와타시와**토**쿄에…), which is how the running speech actually sounds.
- Iteration marks expand before conversion: ゝ/ヽ repeat the previous kana, ゞ/ヾ repeat it voiced (いすゞ → 이스즈). The kanji mark 々 is left to the dictionary when janome is present (時々 → 도키도키) and expanded to the previous kanji otherwise (時々 → 時時), so the leftover is real kanji rather than a symbol.
- Everything is a pure top-level function — safe for `StreamPipeline` and `BatchPipeline`.
- There is no `find_japanese` twin: a Unicode-range regex already finds Japanese script, and the finders exist for the cases a plain regex cannot express.
