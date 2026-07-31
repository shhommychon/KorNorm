from kornorm.heuristics.eraser import (
    purge_symbols, remove_middle_symbols, find_symbols,
    strip_punctuation, collapse_whitespace,
    SENTENCE_PUNCTUATION, BRACKET_PUNCTUATION, QUOTE_PUNCTUATION, DASH_PUNCTUATION,
    DEFAULT_PUNCTUATION,
)
from kornorm.heuristics.repetition import fix_text_degeneration, find_text_degeneration
