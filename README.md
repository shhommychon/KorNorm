<p align="center">
  <img src=".assets/image/kornorm_banner.png" alt="고놈 KorNorm" width="600">
</p>

<p align="center">
  <b>Korean text preprocessing</b> — yet another Korean normalizer, probably unmaintained from initial commit<br>
  <i>text normalization + a G2P engine built on the Standard Korean Pronunciation rules</i>
</p>

---

KorNorm (고놈) turns raw Korean text — digits, units, symbols, English words and all — into hangul that reads the way a Korean speaker would actually say it out loud. It was built with TTS front-ends in mind, but it is just as much at home normalizing ASR transcripts, building pronunciation dictionaries, or anywhere else Korean text needs to match speech.

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

Both steps write into `site-packages`, so make the first call in an environment with write access (see [Known limitations](#known-limitations-alpha)).

## Usage

### `kornorm.heuristics` — an appetizer

To get a taste of the kind of features bundled in, here is one of the small helpers for messy real-world text — collapsing degenerate character repetitions before they reach the analyzer:

```pycon
>>> from kornorm.heuristics import fix_text_degeneration
>>> fix_text_degeneration("아아아아아아아아아아아아아아아아아아아악 놀랐잖아")
'아아아아아〃악 놀랐잖아'
```

The main course is below.

### Two functions, one chain

KorNorm keeps its two jobs as two functions: `dealers_choice` normalizes text into hangul, `apply_phonology` turns hangul into pronunciation. Chain them when you want both:

```python
from kornorm import dealers_choice, apply_phonology

apply_phonology(dealers_choice("몸무게가 70.5kg 나간다"), output_format="hangul")
# '몸무게가 칠씹 쩜 오킬로그램 나간다'
```

### `dealers_choice` — text normalization

<img src=".assets/image/kornorm_dealers_choice.png" alt="the dealer" align="right" width="200">

The house special: a 14-step preset that rewrites numbers, currencies, phone numbers, dates & times, interpunct readings (6·25 → 육이오), units, decimals, alphanumeric combos (MP3 → 엠피쓰리), English words (CMU dict + 외래어 표기법), and leftover Latin letters into hangul.

```pycon
>>> from kornorm import dealers_choice
>>> dealers_choice("무게 70.5kg, 첫차는 오전 5시 30분")
'무게 칠십 쩜 오킬로그램, 첫차는 오전 다섯시 삼십분'
>>> dealers_choice("45,000원짜리 5G 요금제")
'사만오천원짜리 파이브쥐 요금제'
```

Every step is also available as an individual function under `kornorm.alphanumeric` if you want to deal your own hand.

<br clear="right">

### `apply_phonology` — Standard-Pronunciation G2P

The phonology engine implements 표준발음법 rule by rule on top of morphological analysis, with lexical pronunciations from the Standard Korean Language Dictionary (표준국어대사전) applied first through an O(1) trie lookup.

```pycon
>>> from kornorm import apply_phonology
>>> apply_phonology("맑게 갠 하늘과 꽃잎", output_format="hangul")
'말께 갠 하늘과 꼰닙'
>>> apply_phonology("옷 입고 한 일", output_format="hangul")
'온 닙꼬 한 닐'
```

Three output formats, matching common speech-model input conventions:

| `output_format` | `apply_phonology("독립문", …)` | |
|---|---|---|
| `"hangul"` | `동님문` | composed syllables, for human reading |
| `"positional"` | `동님문` | U+11xx conjoining jamo (default; most fonts render it composed) |
| `"compat"` | `ㄷㅗㅇㄴㅣㅁㅁㅜㄴ` | U+313x compatibility jamo |

What sets it apart from existing libraries in the g2pK lineage:

- **Dictionary-first**: lexical pronunciations (대관령[대괄령], 공권력[공꿘녁], …) come from a compiled 표준국어대사전 lookup, not a hardcoded exception list.
- **Per-rule word-boundary policy**: each rule decides whether it may cross a space, and cross-word rules fire only on cohesive word pairs — 옷 입고 한 일 → [온 닙꼬 한 닐] above.
- **Morpheme-aware rules**: functional vs. lexical morpheme distinctions resolve classic edge cases (꽂히다[꼬치다] vs. 낮 한때[나탄때]).

```pycon
>>> apply_phonology("옆라인 동기가 감성 시나 읊코 있는 걸 보니 우리도 완전 늙크크였다", output_format="hangul")
'염나인 동기가 감성 시나 읍코 인는 걸 보니 우리도 완전 늑크크엳따'
>>> from g2pk import G2p  # g2pK 0.9.4, for comparison
>>> G2p()("옆라인 동기가 감성 시나 읊코 있는 걸 보니 우리도 완전 늙크크였다")
'연나인 동기가 감성 시나 읍ᆸ포 인는 걸 보니 우리도 완전 느1)으크엳따'
```

If you would rather hold the engine yourself than call the module-level wrapper, instantiate — or subclass — `PhonologicProcessor` directly (subclassing is how the 허용 allowed-variant rules are enabled). The instance is callable, so it handles just like g2pK's `G2p` class:

```python
from kornorm import PhonologicProcessor

processor = PhonologicProcessor()
processor("독립문", output_format="hangul")  # '동님문'
```

### Pipelines — corpus-scale processing

<img src=".assets/image/kornorm_fullbody_tall.png" alt="StreamPipeline" align="right" width="200">

Both pipelines take any `str` → `str` function. Define your recipe once, at module top level (that keeps it picklable for multiprocessing):

```python
from kornorm import dealers_choice, apply_phonology

def preprocess(line: str) -> str:
    return apply_phonology(dealers_choice(line), output_format="hangul")
```

**`StreamPipeline`** sweeps through your corpus one line at a time — a lazy generator with minimal memory footprint, for when the file is bigger than your RAM:

```python
from kornorm import StreamPipeline

pipe = StreamPipeline(preprocess)
with open("corpus.txt") as f:
    for line in pipe(f):
        ...
```

<br clear="right">

<img src=".assets/image/kornorm_fullbody_short.png" alt="BatchPipeline" align="right" width="200">

**`BatchPipeline`** puts its back into it — multiprocessing across CPU cores for when you want the whole corpus done now. Each worker loads its own copy of the engine:

```python
from kornorm import BatchPipeline

pipe = BatchPipeline(preprocess, max_workers=8)
results = pipe(lines)
```

<br clear="right">

## Module guides

The four packages each ship their own reference — every function they expose, what it does, and an example that was actually run through it:

| | |
|---|---|
| [`kornorm.alphanumeric`](kornorm/alphanumeric/README.md) | numbers, units, currencies, symbols, abbreviations and English words → hangul; the 14 steps of `dealers_choice` and how to use them one at a time |
| [`kornorm.phonology`](kornorm/phonology/README.md) | the 표준발음법 engine — rule-by-rule coverage, pipeline order, the 2D LUT, the dictionary-first pass, word-boundary policy |
| [`kornorm.heuristics`](kornorm/heuristics/README.md) | pre-cleaning helpers for text that came from somewhere real |
| [`kornorm.utils`](kornorm/utils/README.md) | positional-jamo primitives and the one-time pecab dictionary patch |

## Known limitations (alpha)

- The first-run setup cannot complete in read-only environments (e.g. locked-down Docker images) — make the first call once with write access to `site-packages`.
- Symbols outside the conversion tables (`…`, `½`, emoji) pass through unread, and the unit table — broad as it is — is not exhaustive: a compound unit it cannot match is read as best the later steps can (`120km/h` → `백이십킬로미터슬래쉬에이치`).
- Context-dependent homographs (잠자리 bed/dragonfly, …) are resolved by a cue-word vote, which is an approximation.
- Not yet implemented: email/URL reading, spacing correction, sentence-ending unification.

## Credits

This repository is born out of nostalgia for a decent in-house Korean normalizer the author used during a brief stint at an AI speech startup — rebuilt clean-room style on top of the openly published work below.

<details>
<summary><b>Sources & inspirations</b></summary>

- 표준국어대사전 — National Institute of Korean Language, lexical pronunciation data
- [jamo](https://github.com/jdongian/python-jamo) : [Joshua Dong](https://github.com/JDongian)'s foundational jamo package
- Korean G2P libraries
  - [Kyubyong/g2pK](https://github.com/Kyubyong/g2pK) : the original g2pK by [Kyubyong Park](https://github.com/Kyubyong) (TUNiB)
  - [harmlessman/g2pkk](https://github.com/harmlessman/g2pkk) : cross-OS fork
  - [tenebo/g2pk2](https://github.com/tenebo/g2pk2) : latest fork
  - [SMART-G2P](https://github.com/SMART-TTS/SMART-G2P)
- [pecab](https://github.com/hyunwoongko/pecab) : pure-Python MeCab by [Hyunwoong Ko](https://github.com/hyunwoongko) (Kakao)
- Korean TTS cleaner functions
  - [carpedm20/multi-speaker-tacotron-tensorflow](https://github.com/carpedm20/multi-speaker-tacotron-tensorflow/tree/master/text) by [Taehoon Kim](https://carpedm30.notion.site/me)
  - [hash2430/pitchtron](https://github.com/hash2430/pitchtron/blob/hard/text/korean.py) by [Sunghee Jung](https://jsh-tts.tistory.com/)
  - [keonlee9420/Expressive-FastSpeech2](https://github.com/keonlee9420/Expressive-FastSpeech2/blob/main/text/korean.py) by [Keon Lee](https://sites.google.com/view/keonlee9420) (Krafton)
  - [jwj7140/Bert-VITS2-Korean](https://github.com/jwj7140/Bert-VITS2-Korean/blob/main/text/korean.py) by [Woojun Jung](https://github.com/jwj7140)
  - [ORI-Muchim/MB-iSTFT-VITS-Korean](https://github.com/ORI-Muchim/MB-iSTFT-VITS-Korean/blob/main/text/korean.py) by [Minhyung Cho](https://ori-muchim.github.io/)
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/text/korean.py)
- [zeroth](https://github.com/goodatlas/zeroth) : foundational Korean ASR project
- [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) : English word pronunciations

</details>

## License

Released under the *MOST OF IT IS NOT MY CODE PUBLIC LICENSE* — see [LICENSE](LICENSE). It means what it says: wherever a source is credited above, the upstream license (MIT, GPL, Apache-2.0, …) remains in force. Everything else — the parts that are the author's own ideas — is basically [0BSD](https://opensource.org/license/0bsd): the author didn't exactly write the code anyway (an AI coding agent did), so feel free to use it however you like.

## AI Acknowledgment

Pursuant to Article 31, Paragraph 2 of the Act on the Promotion of Artificial Intelligence Industry and Framework for Establishing Trust (Framework Act on Artificial Intelligence) of the Republic of Korea, acknowledgement is hereby given that this Python package was generated by generative artificial intelligence.
