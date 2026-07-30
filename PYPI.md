# 고놈 KorNorm

Korean text preprocessing — text normalization plus a G2P engine built on the Standard Korean Pronunciation rules (표준발음법).

KorNorm turns raw Korean text — digits, units, symbols, English words and all — into hangul that reads the way a Korean speaker would actually say it out loud. It was built with TTS front-ends in mind, but it is just as much at home normalizing ASR transcripts, building pronunciation dictionaries, or anywhere else Korean text needs to match speech.

```pycon
>>> from kornorm import dealers_choice, apply_phonology
>>> apply_phonology(dealers_choice("6·25 전쟁은 1950년에 일어났다"), output_format="hangul")
'유기오 전쟁은 천구배고심녀네 이러낟따'
>>> apply_phonology(dealers_choice("이 old school 감성의 MP3 파일은 3.5MB밖에 안 한다"), output_format="hangul")
'이 올드 스쿨 감성의 엠피쓰리 파이른 삼 쩜 오메가바이트바께 안 한다'
```

## Installation

```bash
pip install kornorm
```

Pure Python (3.10+). The only dependencies are [pecab](https://github.com/hyunwoongko/pecab) and pyarrow — no C toolchain, no MeCab install.

**On first use**, KorNorm performs a one-time setup:

- it patches and rebuilds pecab's bundled dictionary (takes about a minute), and
- it downloads the CMU Pronouncing Dictionary (~3.6 MB) for English word conversion. If the download fails (e.g. offline), everything else still works — English words are simply left as spelled-out letters.

Both steps write into `site-packages`, so run the first call in an environment with write access (see Known limitations).

## Usage

Two layers, used separately or chained:

```pycon
>>> from kornorm import dealers_choice, apply_phonology
>>> dealers_choice("45,000원짜리 5G 요금제")          # normalization only
'사만오천원짜리 파이브쥐 요금제'
>>> apply_phonology("맑게 갠 하늘과 꽃잎", output_format="hangul")  # G2P only
'말께 갠 하늘과 꼰닙'
>>> apply_phonology(dealers_choice("몸무게가 70.5kg 나간다"), output_format="hangul")
'몸무게가 칠씹 쩜 오킬로그램 나간다'
```

- **`dealers_choice`** — a 14-step normalization preset: numbers, currencies, phone numbers, dates & times, interpunct readings (6·25), units, decimals, alphanumeric combos (MP3), English words (via CMU dict + 외래어 표기법), leftover Latin letters.
- **`apply_phonology`** — the phonology engine. Implements 표준발음법 rule by rule on top of morphological analysis, with pronunciations from the Standard Korean Language Dictionary (표준국어대사전) applied first through an O(1) trie lookup. Output formats: `"hangul"` (composed syllables), `"positional"` / `"compat"` (decomposed jamo for speech-model token inputs). It wraps a module-level `PhonologicProcessor` — instantiate or subclass that class directly for more control; the instance is callable, so it handles just like g2pK's `G2p`.
- **`StreamPipeline` / `BatchPipeline`** — lazy generator or multiprocessing wrappers for corpus-scale processing.

What sets the G2P apart from existing libraries in the g2pK lineage:

- **Dictionary-first**: lexical pronunciations (대관령[대괄령], 공권력[공꿘녁], …) come from a compiled 표준국어대사전 lookup instead of a hardcoded exception list.
- **Per-rule word-boundary policy**: each rule decides whether it may cross a space, and cross-word rules fire only on cohesive word pairs (옷 입고 한 일 → [온 닙꼬 한 닐]).
- **Morpheme-aware rules**: functional vs. lexical morpheme distinctions resolve classic edge cases (꽂히다[꼬치다] vs. 낮 한때[나탄때]).

## Known limitations (alpha)

- The first-run setup cannot complete in read-only environments (e.g. locked-down Docker images) — trigger the first call once with write access to `site-packages`.
- Symbols outside the conversion tables (`…`, `½`, emoji) pass through unread, and the unit table — broad as it is — is not exhaustive: a compound unit it cannot match is read as best the later steps can (`120km/h` → `백이십킬로미터슬래쉬에이치`).
- Context-dependent homographs (잠자리 bed/dragonfly …) are resolved by a cue-word vote, which is an approximation.
- Not yet implemented: email/URL reading, spacing correction, sentence-ending unification.

## Changelog

- **0.0.0a2** — removed the `normalize` wrapper: compose the two layers yourself (`apply_phonology(dealers_choice(text), output_format="hangul")`). Fixed `output_format="hangul"` crashing on any non-hangul character (punctuation included) and bare `0` disappearing from numbers; numbers with a leading zero now read as codes (`007` → 공공칠). Added `pos()` (morphological tags as the engine sees them), `strip_punctuation`/`collapse_whitespace`, `find_text_degeneration`, regex targets for the symbol removers, and charge/energy compound units (`mAh`, `kWh`, `%p`, …).
- **0.0.0a1** — first release.

## Credits

Built on the shoulders of: 표준국어대사전 (National Institute of Korean Language), [pecab](https://github.com/hyunwoongko/pecab) by Hyunwoong Ko, [g2pK](https://github.com/Kyubyong/g2pK) by Kyubyong Park and its descendants, [python-jamo](https://github.com/jdongian/python-jamo) by Joshua Dong, and the [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict). See the [repository](https://github.com/shhommychon/KorNorm) for the full lineage.

## License

Released under the *MOST OF IT IS NOT MY CODE PUBLIC LICENSE* — see the LICENSE file. It means what it says: wherever a source is credited, the upstream license (MIT, GPL, Apache-2.0, …) remains in force. Everything else — the parts that are the author's own ideas — is basically [0BSD](https://opensource.org/license/0bsd): the author didn't exactly write the code anyway (an AI coding agent did), so feel free to use it however you like.
