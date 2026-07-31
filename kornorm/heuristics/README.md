## `kornorm.heuristics` — pre-cleaning for messy text

Small, opt-in helpers for text that came from somewhere real — chat logs, subtitle files, ASR output, a language model that got stuck in a loop. Nothing here is part of `dealers_choice`; you reach for these when your corpus needs them, usually as the first stage of a [pipeline](../../README.md#pipelines--corpus-scale-processing).

> [← back to the main README](../../README.md) · siblings: [`alphanumeric`](../alphanumeric/README.md) · [`phonology`](../phonology/README.md) · [`asia`](../asia/README.md) · [`utils`](../utils/README.md)

### `fix_text_degeneration` — collapse runaway repetitions

Finds any repeating unit (a character, a syllable, a word, a word plus its space) that repeats past a threshold, keeps the first `repeat_count` copies, and marks the cut with a separator.

```pycon
>>> from kornorm.heuristics import fix_text_degeneration
>>> fix_text_degeneration("아아아아아아아아아아아아아아아아아아아악 놀랐잖아")
'아아아아아〃악 놀랐잖아'
>>> fix_text_degeneration("으 으 으 으 으 으 으 으")
'으 으 으 으 으 〃'
>>> fix_text_degeneration("ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ", repeat_count=3)
'ㅋㅋㅋ〃'
>>> fix_text_degeneration("ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ", repeat_count=3, replace_char='')
'ㅋㅋㅋ'
```

| Argument | Default | Meaning |
|---|---|---|
| `repeat_count` | `5` | how many copies of the unit survive; anything beyond is collapsed |
| `replace_char` | `'〃'` (U+3003) | the mark left where the collapse happened — pass `''` to leave no trace |
| `rpad_space` | `True` | temporarily pads a trailing space so that space-separated repetitions (`"으 으 으"`) match as a unit; the padding is removed from the result |

The pattern is `(.+?)\1{n-1,}` — the repeating unit is discovered, not configured — and it is compiled once per threshold and cached.

### `find_text_degeneration` — detect without touching

The read-only twin: it reports exactly the matches `fix_text_degeneration` would collapse, as `(start, end, unit, count)` tuples against the original text, and changes nothing. `fix(text) != text` and `find(text) != []` always agree.

```pycon
>>> from kornorm.heuristics import find_text_degeneration
>>> find_text_degeneration("으아아아아아아아아악")
[(1, 9, '아', 8)]
>>> find_text_degeneration("정상 문장입니다")
[]
```

### `purge_symbols` — delete every occurrence

Takes any iterable of targets (a plain string works too, since it iterates its characters) and removes all of them. Targets may be literal strings or **compiled regex patterns**, mixed freely — which is how corpus-specific boilerplate (broadcast sign-offs, bracketed stage directions) gets handled without KorNorm shipping anyone's list:

```pycon
>>> from kornorm.heuristics import purge_symbols
>>> purge_symbols("안~녕~하세요~~", '~')
'안녕하세요'
>>> purge_symbols("[음악] 안녕 (웃음)", ("[음악]", "(웃음)"))
' 안녕 '
>>> import re
>>> purge_symbols("지금까지 강남에서 ABC 뉴스 홍길동입니다", (re.compile(r"ABC 뉴스 \S+입니다"),))
'지금까지 강남에서 '
```

### `remove_middle_symbols` — delete every occurrence but the last

Same idea, except one trailing marker survives — the one that is usually carrying the sentence's tone rather than noise. Regex targets work here too (a pattern match ending exactly at the end of the text is the one kept).

```pycon
>>> from kornorm.heuristics import remove_middle_symbols
>>> remove_middle_symbols("안~녕~하세요~~", '~')
'안녕하세요~'
>>> remove_middle_symbols("정말!! 대박!!!", ('!',))
'정말 대박!'
```

Literal targets are matched longest-first, so overlapping targets (`"!!"` and `"!"`) behave predictably; patterns run after literals, in the order given.

### `find_symbols` — detect without touching

The read-only twin of `purge_symbols`: same targets interface (literals and compiled patterns, mixed freely), reporting every match as `(start, end, match)` tuples against the original text, sorted by position — `text[start:end] == match` holds for each. `purge(text, targets) != text` and `find(text, targets) != []` always agree. The one trailing marker `remove_middle_symbols` would preserve is still reported here.

```pycon
>>> from kornorm.heuristics import find_symbols
>>> find_symbols("안~녕~하세요~~", '~')
[(1, 2, '~'), (3, 4, '~'), (7, 8, '~'), (8, 9, '~')]
>>> find_symbols("잠시... [음악] 만요...", ("...", re.compile(r"\[[^\]]+\]")))
[(2, 5, '...'), (6, 10, '[음악]'), (13, 16, '...')]
>>> find_symbols("정상 문장입니다", ('~', '!'))
[]
```

### `strip_punctuation` · `collapse_whitespace` — the pre-cleaning pair

`strip_punctuation` is `purge_symbols` with batteries: a default set of sentence punctuation, brackets, quotes and dashes, exposed as composable constants (`SENTENCE_PUNCTUATION`, `BRACKET_PUNCTUATION`, `QUOTE_PUNCTUATION`, `DASH_PUNCTUATION`, and their union `DEFAULT_PUNCTUATION`). Deliberately **not** in the default set: the ASCII hyphen (phone numbers, ranges), the interpunct `·` (6·25 readings), and spoken symbols like `%` and `+` — those belong to [`alphanumeric`](../alphanumeric/README.md), not the eraser.

`collapse_whitespace` squeezes runs of spaces and tabs down to one and trims the ends, leaving newlines alone (lines are the pipeline unit). It is itself a `purge_symbols` call with a whitespace-run pattern as the target. The two chain naturally:

```pycon
>>> from kornorm.heuristics import strip_punctuation, collapse_whitespace
>>> strip_punctuation('"인용" 부호와 「괄호」, — 줄표')
'인용 부호와 괄호  줄표'
>>> collapse_whitespace(strip_punctuation('"인용" 부호와 「괄호」, — 줄표'))
'인용 부호와 괄호 줄표'
>>> strip_punctuation("6·25는 1950-06-25, 100% 확실")   # meaning-bearing symbols survive
'6·25는 1950-06-25 100% 확실'
```

### Notes

- Everything here is a pure function with no state, which is what both `StreamPipeline` and `BatchPipeline` require (the batch one additionally needs top-level, picklable callables — these qualify).
- Deletion leaves the surrounding spaces alone; `purge_symbols` above returns `' 안녕 '`, not `'안녕'`. That is what `collapse_whitespace` is for.
