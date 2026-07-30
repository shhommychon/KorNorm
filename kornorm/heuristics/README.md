## `kornorm.heuristics` — pre-cleaning for messy text

Small, opt-in helpers for text that came from somewhere real — chat logs, subtitle files, ASR output, a language model that got stuck in a loop. Nothing here is part of `dealers_choice`; you reach for these when your corpus needs them, usually as the first stage of a [pipeline](../../README.md#pipelines--corpus-scale-processing).

> [← back to the main README](../../README.md) · siblings: [`alphanumeric`](../alphanumeric/README.md) · [`phonology`](../phonology/README.md) · [`utils`](../utils/README.md)

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

### `purge_symbols` — delete every occurrence

Takes any iterable of strings (a plain string works too, since it iterates its characters) and removes all of them.

```pycon
>>> from kornorm.heuristics import purge_symbols
>>> purge_symbols("안~녕~하세요~~", '~')
'안녕하세요'
>>> purge_symbols("[음악] 안녕 (웃음)", ("[음악]", "(웃음)"))
' 안녕 '
```

### `remove_middle_symbols` — delete every occurrence but the last

Same idea, except one trailing marker survives — the one that is usually carrying the sentence's tone rather than noise.

```pycon
>>> from kornorm.heuristics import remove_middle_symbols
>>> remove_middle_symbols("안~녕~하세요~~", '~')
'안녕하세요~'
>>> remove_middle_symbols("정말!! 대박!!!", ('!',))
'정말 대박!'
```

Targets are matched longest-first, so overlapping targets (`"!!"` and `"!"`) behave predictably.

### Notes

- All three are pure `str` → `str` functions with no state, which is what both `StreamPipeline` and `BatchPipeline` require (the batch one additionally needs top-level, picklable callables — these qualify).
- Deletion leaves the surrounding spaces alone; `purge_symbols` above returns `' 안녕 '`, not `'안녕'`. Collapse whitespace yourself if you need it.
