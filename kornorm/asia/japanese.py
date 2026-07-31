# [KorNorm 일본어 발음 변환 모듈]
#
# 텍스트 속 일본어(가나·한자)를 외래어 표기법의 일본어 가나-한글 대조표(표4)와
# 표기 세칙(촉음 받침 ㅅ, 장모음 무표기)에 따라 한글 표기로 변환합니다.
# 가나는 자체가 표음문자이므로 대조표만으로 무의존 변환이 가능하며, 한자 독음은
# janome(선택 의존성: `pip install kornorm[ja]`) 형태소 분석의 발음(phonetic)
# 필드로 확보합니다. janome가 없으면 가나만 변환하고 한자는 남깁니다.
#
# Ref:
#     외래어 표기법 제2장 표4 (일본어의 가나와 한글 대조표) / 제3장 제6절 (일본어의 표기)
#     — https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0003
#     janome (순수 파이썬 일본어 형태소 분석기, Apache-2.0)
#     — https://github.com/mocobeta/janome

import re
from typing import Optional

from kornorm.utils.jamo import C_NIEUN, C_NONE, C_SIOT, join_jamos, split_syllable_char

# 히라가나(ぁ~ゖ)·반복 기호(ゝゞ)를 가타카나로 정규화 (+0x60 오프셋)
_HIRA_TO_KATA = str.maketrans({
    chr(code): chr(code + 0x60)
    for code in [*range(0x3041, 0x3097), 0x309D, 0x309E]
})

# 표4 단자 대조표 — 어두 기준. 어두/어중이 갈리는 カ·タ행은 _KANA_MEDIAL 오버라이드 참조.
_KANA_INITIAL = {
    'ア': '아', 'イ': '이', 'ウ': '우', 'エ': '에', 'オ': '오',
    'カ': '가', 'キ': '기', 'ク': '구', 'ケ': '게', 'コ': '고',
    'サ': '사', 'シ': '시', 'ス': '스', 'セ': '세', 'ソ': '소',
    'タ': '다', 'チ': '지', 'ツ': '쓰', 'テ': '데', 'ト': '도',
    'ナ': '나', 'ニ': '니', 'ヌ': '누', 'ネ': '네', 'ノ': '노',
    'ハ': '하', 'ヒ': '히', 'フ': '후', 'ヘ': '헤', 'ホ': '호',
    'マ': '마', 'ミ': '미', 'ム': '무', 'メ': '메', 'モ': '모',
    'ヤ': '야', 'ユ': '유', 'ヨ': '요',
    'ラ': '라', 'リ': '리', 'ル': '루', 'レ': '레', 'ロ': '로',
    'ワ': '와', 'ヰ': '이', 'ヱ': '에', 'ヲ': '오',
    'ガ': '가', 'ギ': '기', 'グ': '구', 'ゲ': '게', 'ゴ': '고',
    'ザ': '자', 'ジ': '지', 'ズ': '즈', 'ゼ': '제', 'ゾ': '조',
    'ダ': '다', 'ヂ': '지', 'ヅ': '즈', 'デ': '데', 'ド': '도',
    'バ': '바', 'ビ': '비', 'ブ': '부', 'ベ': '베', 'ボ': '보',
    'パ': '파', 'ピ': '피', 'プ': '푸', 'ペ': '페', 'ポ': '포',
    'ヴ': '부',
    # 소형 가나의 단독 출현(요음·외래 음 조합에 못 낀 비정형 표기)은 온전한 모음으로 수용
    'ァ': '아', 'ィ': '이', 'ゥ': '우', 'ェ': '에', 'ォ': '오',
    'ャ': '야', 'ュ': '유', 'ョ': '요', 'ヮ': '와',
    'ヵ': '가', 'ヶ': '가',
}

# 어중·어말 오버라이드 (표4: カ·タ행은 어중·어말에서 거센소리. ツ는 위치 무관 '쓰')
_KANA_MEDIAL = dict(_KANA_INITIAL)
_KANA_MEDIAL.update({
    'カ': '카', 'キ': '키', 'ク': '쿠', 'ケ': '케', 'コ': '코',
    'タ': '타', 'チ': '치', 'テ': '테', 'ト': '토',
    'ヵ': '카', 'ヶ': '카',
})

# 표4 요음(2글자) 대조표 — 어두 기준 + 외래 음 표기용 관용 확장
_DIGRAPHS_INITIAL = {
    "キャ": '갸', "キュ": '규', "キョ": '교',
    "ギャ": '갸', "ギュ": '규', "ギョ": '교',
    "シャ": '샤', "シュ": '슈', "ショ": '쇼',
    "ジャ": '자', "ジュ": '주', "ジョ": '조',
    "チャ": '자', "チュ": '주', "チョ": '조',
    "ニャ": '냐', "ニュ": '뉴', "ニョ": '뇨',
    "ヒャ": '햐', "ヒュ": '휴', "ヒョ": '효',
    "ビャ": '뱌', "ビュ": '뷰', "ビョ": '뵤',
    "ピャ": '퍄', "ピュ": '퓨', "ピョ": '표',
    "ミャ": '먀', "ミュ": '뮤', "ミョ": '묘',
    "リャ": '랴', "リュ": '류', "リョ": '료',
    # 표4 외 확장 — 외래 음 전사용 가나 조합의 통용 표기
    "シェ": '셰', "ジェ": '제', "チェ": '제',
    "ティ": '디', "ディ": '디', "トゥ": '두', "ドゥ": '두', "デュ": '듀',
    "ファ": '파', "フィ": '피', "フェ": '페', "フォ": '포', "フュ": '퓨',
    "ヴァ": '바', "ヴィ": '비', "ヴェ": '베', "ヴォ": '보',
    "ウィ": '위', "ウェ": '웨', "ウォ": '워',
}
_DIGRAPHS_MEDIAL = dict(_DIGRAPHS_INITIAL)
_DIGRAPHS_MEDIAL.update({
    "キャ": '캬', "キュ": '큐', "キョ": '쿄',
    "チャ": '차', "チュ": '추', "チョ": '초',
    "チェ": '체', "ティ": '티', "トゥ": '투',
})

# 청음 → 탁음 (탁점 반복 기호 ヾ 전개용)
_KATA_VOICING = {
    plain: voiced
    for plains, voiceds in (
        ("カキクケコ", "ガギグゲゴ"), ("サシスセソ", "ザジズゼゾ"),
        ("タチツテト", "ダヂヅデド"), ("ハヒフヘホ", "バビブベボ"), ('ウ', 'ヴ'),
    )
    for plain, voiced in zip(plains, voiceds)
}

# 장모음 축약 판정용 모음 열(段) — 요음 소자·소형 모음 포함 (ヵ·ヶ는 카/가로 읽혀 ア단)
_VOWEL_COLUMNS = {
    'a': set("アカガサザタダナハバパマヤラワャァヮヵヶ"),
    'i': set("イキギシジチヂニヒビピミリヰィ"),
    'u': set("ウヴクグスズツヅヌフブプムユルュゥ"),
    'e': set("エケゲセゼテデネヘベペメレヱェ"),
    'o': set("オコゴソゾトドノホボポモヨロヲョォ"),
}
_PURE_VOWELS = {'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o'}

# 일본어 스팬(가나·장음·반복 기호·한자 연속 구간)과 판정용 부분 패턴
_RE_JAPANESE_SPAN = re.compile(
    "[ぁ-ゖゝゞ"        # 히라가나·반복 기호(ゝゞ)
    "ァ-ヺー-ヾ"        # 가타카나·장음(ー)·반복 기호(ヽヾ)
    "々〆"                      # 반복 기호(々)·〆
    "一-鿿㐀-䶿]+"      # 한자 (CJK 통합·확장 A)
)
_RE_KANA = re.compile("[ぁ-ゖァ-ヺ]")
_RE_KANJI = re.compile("[一-鿿㐀-䶿々]")

_tokenizer = None
_janome_notified = False


def _load_janome():
    """
    janome 형태소 분석기를 지연 로딩합니다.

    미설치 환경에서는 최초 1회 열화 내용을 경고로 출력하고 None을 반환합니다
    (호출 측은 한자 독음 없이 가나만 변환하는 폴백 경로를 탑니다).

    Returns:
        Optional[janome.tokenizer.Tokenizer]: 분석기 인스턴스. 미설치 시 None.
    """
    global _tokenizer, _janome_notified
    if _tokenizer is not None:
        return _tokenizer

    try:
        from janome.tokenizer import Tokenizer
    except ImportError:
        if not _janome_notified:
            print("KorNorm: janome가 설치되어 있지 않아 일본어를 가나 대조표만으로 "
                  "변환합니다. 한자는 변환되지 않고 조사 발음(は→와, へ→에)도 "
                  "반영되지 않습니다. 전체 기능: pip install kornorm[ja] (또는 kornorm[all])")
            _janome_notified = True
        return None

    _tokenizer = Tokenizer()
    return _tokenizer


def _is_kanji(char: str) -> bool:
    """
    단일 문자가 한자(CJK 통합·확장 A)인지 판정합니다.

    Args:
        char (str): 판정할 단일 문자.

    Returns:
        bool: 한자면 True.
    """
    return '一' <= char <= '鿿' or '㐀' <= char <= '䶿'


def _vowel_column(kana: str) -> Optional[str]:
    """
    가타카나 한 글자가 속한 모음 열(ア단~オ단)을 판정합니다.

    Args:
        kana (str): 판정할 단일 가타카나.

    Returns:
        Optional[str]: 'a'/'i'/'u'/'e'/'o'. 가나가 아니거나 모음 열이 없으면 None.
    """
    for column, members in _VOWEL_COLUMNS.items():
        if kana in members:
            return column
    return None


def _expand_iteration_marks(kata: str) -> str:
    """
    반복 기호를 직전 문자의 반복으로 전개합니다.

    ヽ는 직전 가나 복사, ヾ는 직전 가나의 탁음형 복사(いすゞ -> いすず),
    々는 직전 한자 복사(時々 -> 時時)입니다. 직전 문자의 종류가 맞지 않으면
    기호를 그대로 둡니다. 형태소 사전 등재어(時々 -> トキドキ 등)는 janome가
    전개 없이 통째로 읽으므로, 이 함수는 미등재 표면형과 무분석기 폴백
    경로에서만 실제로 동작합니다.

    Args:
        kata (str): 가타카나로 정규화된 문자열.

    Returns:
        str: 반복 기호가 전개된 문자열.
    """
    result = []
    for char in kata:
        if result:
            prev = result[-1]
            if char in "ヽヾ" and 'ァ' <= prev <= 'ヺ':
                result.append(_KATA_VOICING.get(prev, prev) if char == 'ヾ' else prev)
                continue
            if char == '々' and _is_kanji(prev):
                result.append(prev)
                continue
        result.append(char)
    return "".join(result)


def _collapse_long_vowels(kata: str) -> str:
    """
    장모음을 축약합니다 (표기 세칙 제2항: 장모음은 따로 표기하지 않는다).

    장음 기호(ー)를 제거하고, 직전 가나와 같은 모음 열의 순수 모음 글자
    (オオサカ -> オサカ)와 オ단 뒤의 ウ(トウキョウ -> トキョウ)를 걷어냅니다.
    エ단 뒤의 イ는 통용 표기를 따라 유지합니다 (ゲイシャ -> 게이샤).

    Args:
        kata (str): 가타카나로 정규화된 문자열 (단어 경계를 넘는 축약 오판정을
            피하려면 형태소 토큰 단위로 적용해야 합니다).

    Returns:
        str: 장모음이 축약된 문자열.
    """
    result = []
    for char in kata:
        if char == 'ー':
            continue
        if result and char in _PURE_VOWELS:
            prev_column = _vowel_column(result[-1])
            if prev_column == _PURE_VOWELS[char]:
                continue
            if char == 'ウ' and prev_column == 'o':
                continue
        result.append(char)
    return "".join(result)


def _kana_to_hangul(kata: str, word_initial: bool = True) -> str:
    """
    가타카나 문자열을 표4 대조표에 따라 한글 표기로 변환합니다.

    カ·タ행은 어두에서 예사소리, 어중·어말에서 거센소리로 갈리며(도쿄·요코하마),
    촉음(ッ)은 받침 ㅅ, 발음(ン)은 받침 ㄴ으로 직전 음절에 붙습니다(삿포로·센다이).
    대조표 밖 문자(한자·문장부호)는 그대로 통과하고, 그 다음 가나는 새 어두로 봅니다.

    Args:
        kata (str): 가타카나로 정규화되고 장모음이 축약된 문자열.
        word_initial (bool): 문자열 시작을 어두로 볼지 여부 (기본값 True).

    Returns:
        str: 한글 표기로 변환된 문자열.
    """
    result = []
    i = 0
    while i < len(kata):
        char = kata[i]

        # 촉음(ッ)·발음(ン)은 직전 음절의 받침이 된다 (세칙 제1항·표4)
        if char in "ッン":
            if result:
                cho, joong, jong = split_syllable_char(result[-1])
                if joong and jong == C_NONE:
                    coda = C_SIOT if char == 'ッ' else C_NIEUN
                    result[-1] = join_jamos(cho, joong, coda)
                    i += 1
                    continue
            result.append(char)     # 받침을 붙일 음절이 없으면 그대로 통과
            i += 1
            continue

        digraphs = _DIGRAPHS_INITIAL if word_initial else _DIGRAPHS_MEDIAL
        singles = _KANA_INITIAL if word_initial else _KANA_MEDIAL

        digraph = kata[i:i + 2]
        if len(digraph) == 2 and digraph in digraphs:
            result.append(digraphs[digraph])
            word_initial = False
            i += 2
            continue
        if char in singles:
            result.append(singles[char])
            word_initial = False
            i += 1
            continue

        # 대조표 밖 문자(한자·문장부호 등)는 통과, 다음 가나는 새 어두
        result.append(char)
        word_initial = True
        i += 1

    return "".join(result)


def _convert_span_with_janome(span: str, tokenizer) -> str:
    """
    일본어 스팬을 janome 형태소 분석을 거쳐 한글 표기로 변환합니다.

    토큰별 발음(phonetic) 필드를 우선 사용해 조사 발음(は -> 와, へ -> 에)과
    장모음 정규화(トウキョウ -> トーキョー)를 사전에서 확보하고, 미등재('*')
    토큰은 표면형의 가나만 변환합니다. 장모음 축약은 단어 경계를 넘는 오판정을
    막기 위해 토큰 단위로 적용하며, 어두 판정은 스팬 시작 한 곳입니다
    (스팬은 붙여 쓴 연속 발화이므로 토큰 경계마다 어두로 되돌리지 않습니다).

    Args:
        span (str): 일본어 스크립트 연속 구간.
        tokenizer (janome.tokenizer.Tokenizer): 로딩된 형태소 분석기.

    Returns:
        str: 한글 표기로 변환된 스팬.
    """
    kata_parts = []
    for token in tokenizer.tokenize(span):
        kata = token.phonetic
        if not kata or kata == '*':
            kata = token.reading
        if not kata or kata == '*':
            kata = token.surface.translate(_HIRA_TO_KATA)
        kata = _expand_iteration_marks(kata)
        kata_parts.append(_collapse_long_vowels(kata))
    return _kana_to_hangul("".join(kata_parts))


def _convert_span_kana_only(span: str) -> str:
    """
    일본어 스팬의 가나만 대조표로 변환합니다 (janome 미설치 폴백).

    형태소 정보가 없으므로 조사 발음 구분(は -> 와)이 불가능해 글자 그대로
    변환하며(は -> 하), 한자는 건드리지 않고 남깁니다. 한자 반복 기호는
    직전 한자의 복사로 전개해(時々 -> 時時) 잔류물에 기호가 남지 않게 합니다.

    Args:
        span (str): 일본어 스크립트 연속 구간.

    Returns:
        str: 가나만 한글 표기로 변환된 스팬.
    """
    kata = span.translate(_HIRA_TO_KATA)
    kata = _expand_iteration_marks(kata)
    kata = _collapse_long_vowels(kata)
    return _kana_to_hangul(kata)


def read_japanese(text: str, convert_lone_kanji: bool = False) -> str:
    """
    텍스트 속 일본어를 외래어 표기법에 따라 한글 표기로 변환합니다.

    가나가 하나라도 포함된 스크립트 연속 구간을 일본어로 판정해 변환합니다.
    한자만의 구간("中國" 등)은 한국어 문맥의 한자 원문일 수 있으므로 기본값에서는
    건드리지 않습니다. 한자 독음은 janome(`pip install kornorm[ja]`)가 있을 때만
    확보되며, 없으면 가나만 변환하고 한자는 원문 그대로 남습니다.

    Args:
        text (str): 원본 텍스트.
        convert_lone_kanji (bool): 한자만의 구간도 일본어로 읽을지 여부
            (기본값 False, janome 필요).

    Returns:
        str: 일본어가 한글 표기로 변환된 텍스트.
    """
    def _repl(match):
        span = match.group(0)
        if not _RE_KANA.search(span):
            if not (convert_lone_kanji and _RE_KANJI.search(span)):
                return span

        tokenizer = _load_janome()
        if tokenizer is not None:
            return _convert_span_with_janome(span, tokenizer)
        return _convert_span_kana_only(span)

    return _RE_JAPANESE_SPAN.sub(_repl, text)
