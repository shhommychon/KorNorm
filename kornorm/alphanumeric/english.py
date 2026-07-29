# [KorNorm 영어 단어 발음 변환 모듈]
#
# CMU 발음 사전(ARPABET)과 외래어 표기법 영어 표기 세칙을 이용해 텍스트 속 영어 단어를
# 한글 표기로 변환합니다 ("old school" -> "올드 스쿨"). 사전 미등재 단어는 건드리지 않고
# 남겨 후속 단계(낱자 읽기)로 넘깁니다.
#
# 발음 사전은 최초 실행 시 `_fetch_cmudict`가 1회 내려받아 패키지 리소스로 자가 설치합니다

import re
from typing import List, Optional

from kornorm.alphanumeric._fetch_cmudict import fetch_cmudict_if_needed
from kornorm.utils.jamo import (
    O_GIYEOK, O_NIEUN, O_DIGEUT, O_RIEUL, O_MIEUM, O_BIEUP, O_SIOT, O_IEUNG,
    O_JIEUT, O_CHIEUT, O_KIEUK, O_TIEUT, O_PIEUP, O_HIEUT,
    N_A, N_AE, N_YA, N_YAE, N_EO, N_E, N_YEO, N_YE, N_O, N_WA, N_WAE,
    N_YO, N_U, N_WEO, N_WE, N_WI, N_YU, N_EU, N_UI, N_I,
    C_GIYEOK, C_NIEUN, C_DIGEUT, C_RIEUL, C_MIEUM, C_BIEUP, C_SIOT,
    C_IEUNG, C_JIEUT, C_CHIEUT, C_TIEUT, C_PIEUP, C_HIEUT,
    join_jamos,
)

# 반모음 [j](Y)·[w](W)는 뒤따르는 모음과 합쳐질 때까지 ASCII 자리표시자로 남겨 둔다.
_ARPABET_ONSETS = {
    'B': O_BIEUP, "CH": O_CHIEUT, 'D': O_DIGEUT, "DH": O_DIGEUT, "DZ": O_JIEUT,
    'F': O_PIEUP, 'G': O_GIYEOK, "HH": O_HIEUT, "JH": O_JIEUT, 'K': O_KIEUK,
    'L': O_RIEUL, 'M': O_MIEUM, 'N': O_NIEUN, "NG": O_IEUNG, 'P': O_PIEUP,
    'R': O_RIEUL, 'S': O_SIOT, "SH": O_SIOT, 'T': O_TIEUT, "TH": O_SIOT,
    "TS": O_CHIEUT, 'V': O_BIEUP, 'W': 'W', 'Y': 'Y', 'Z': O_JIEUT, "ZH": O_JIEUT,
}

_ARPABET_NUCLEI = {
    "AA": N_A,
    "AE": N_AE,
    "AH": N_EO,
    "AO": N_O,
    "AW": N_A + O_IEUNG + N_U,          # 아우
    "AWER": N_A + O_IEUNG + N_WEO,      # 아워 (외래어 표기법 8항: [auə])
    "AY": N_A + O_IEUNG + N_I,          # 아이
    "EH": N_E,
    "ER": N_EO,
    "EY": N_E + O_IEUNG + N_I,          # 에이
    "IH": N_I,
    "IY": N_I,
    "OW": N_O,                          # 8항: [ou]는 '오'
    "OY": N_O + O_IEUNG + N_I,          # 오이
    "UH": N_U,
    "UW": N_U,
}

_ARPABET_CODAS = {
    'B': C_BIEUP, "CH": C_CHIEUT, 'D': C_DIGEUT, "DH": C_DIGEUT, 'F': C_PIEUP,
    'G': C_GIYEOK, "HH": C_HIEUT, "JH": C_JIEUT, 'K': C_GIYEOK, 'L': C_RIEUL,
    'M': C_MIEUM, 'N': C_NIEUN, "NG": C_IEUNG, 'P': C_BIEUP, 'R': C_RIEUL,
    'S': C_SIOT, "SH": C_SIOT, 'T': C_SIOT, "TH": C_SIOT, 'V': C_BIEUP,
    'W': C_IEUNG, 'Y': C_IEUNG, 'Z': C_JIEUT, "ZH": C_JIEUT,
}

# 반모음 자리표시자를 실제 모음과 병합하는 후처리 쌍 (적용 순서 유지).
_GLIDE_MERGES = (
    # [gw]/[hw]/[kw] 앞에 삽입된 'ᅳ'를 걷어내 '과·화·콰' 계열로 합친다 (quick -> 퀵)
    (O_GIYEOK + N_EU + 'W', O_GIYEOK + 'W'),
    (O_HIEUT + N_EU + 'W', O_HIEUT + 'W'),
    (O_KIEUK + N_EU + 'W', O_KIEUK + 'W'),
    # 치조음+[jə]는 '이어'로 풀어 적는다 (외래어 표기법 9항 2)
    (O_NIEUN + 'Y' + N_EO, O_NIEUN + N_I + O_IEUNG + N_EO),
    (O_DIGEUT + 'Y' + N_EO, O_DIGEUT + N_I + O_IEUNG + N_EO),
    (O_RIEUL + 'Y' + N_EO, O_RIEUL + N_I + O_IEUNG + N_EO),
    ('Y' + N_I, N_I),
    ('Y' + N_A, N_YA),
    ('Y' + N_AE, N_YAE),
    ('Y' + N_EO, N_YEO),
    ('Y' + N_E, N_YE),
    ('Y' + N_O, N_YO),
    ('Y' + N_U, N_YU),
    ('W' + N_A, N_WA),
    ('W' + N_AE, N_WAE),
    ('W' + N_EO, N_WEO),
    ('W' + N_O, N_WEO),
    ('W' + N_U, N_U),
    ('W' + N_E, N_WE),
    ('W' + N_I, N_WI),
    (N_EU + N_I, N_UI),
    ('Y', N_I),
    ('W', N_U),
)

# 짧은 모음 (외래어 표기법 1항 1: 짧은 모음 뒤 어말 무성 파열음은 받침)
_SHORT_VOWELS = ("AE", "AH", "AX", "EH", "IH", "IX", "UH")
_VOWEL_INITIALS = "AEIOUY"
_CONSONANT_INITIALS = "BCDFGHJKLMNPQRSTVWXZ"
# 반모음 [j](Y)는 자음 취급에서 제외해 '으' 삽입 없이 뒤 모음과 합쳐지게 한다
# (computer -> 컴퓨터. g2pK는 Y를 자음으로 취급해 [컴프유터]가 되는 것을 바로잡음).
_FINAL_OR_CONSONANTS = "$BCDFGHJKLMNPQRSTVWXZ"

_cmu_dict = None


def _load_cmu_dict() -> Optional[dict]:
    """
    CMU 발음 사전 파일을 지연 파싱하여 {단어: 음소 리스트} 사전을 만듭니다.

    cmusphinx 배포본(소문자)과 원본 0.7b(대문자·';;;' 주석) 서식을 모두 수용하며,
    복수 발음 변형("word(2)")은 첫 발음만 채택합니다.

    Returns:
        Optional[dict]: {소문자 단어: ARPABET 음소 리스트}. 사전 확보 실패 시 None.
    """
    global _cmu_dict
    if _cmu_dict is not None:
        return _cmu_dict

    dict_path = fetch_cmudict_if_needed()
    if dict_path is None:
        return None

    cmu = {}
    with open(dict_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(";;;"):
                continue
            # 행 끝 주석 제거 (예: "aachen AA1 K AH0 N # place, german")
            line = line.split(" #")[0]

            parts = line.split()
            if len(parts) < 2:
                continue
            word = parts[0].lower()
            if word.endswith(')') and '(' in word:
                continue
            cmu[word] = parts[1:]

    _cmu_dict = cmu
    return _cmu_dict


def _adjust_arpabet(arpabets: List[str]) -> List[str]:
    """
    CMU 사전의 ARPABET 나열을 변환 규칙에 맞게 손질합니다.

    강세 숫자를 제거하고, 파찰음(T+S, D+Z)과 [auə]류(AW+ER)를 한 음소로 병합하며,
    어말 [ɪr]/[ɛr]은 '이어'/'에어'로 풀리도록 ER를 분리합니다.

    Ref:
        g2pK utils.py adjust
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/utils.py#L6-L17

    Args:
        arpabets (List[str]): CMU 사전이 반환한 ARPABET 리스트 (예: ["K", "AH0", "M"]).

    Returns:
        List[str]: 손질이 끝난 음소 리스트.
    """
    joined = ' ' + " ".join(arpabets) + " $"
    joined = re.sub(r"\d", '', joined)
    joined = joined.replace(" T S ", " TS ")
    joined = joined.replace(" D Z ", " DZ ")
    joined = joined.replace(" AW ER ", " AWER ")
    joined = joined.replace(" IH R $", " IH ER ")
    joined = joined.replace(" EH R $", " EH ER ")
    return joined.strip("$ ").split()


def _arpabet_to_jamo(phonemes: List[str]) -> str:
    """
    음소 나열을 외래어 표기법 영어 표기 세칙에 따라 자모 스트림으로 변환합니다.

    반모음(Y·W)은 ASCII 자리표시자로 남겨 두었다가 `_GLIDE_MERGES`가 병합합니다.

    Ref:
        g2pK english.py convert_eng (표기 세칙 분기 구조)
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/english.py#L12-L146
        외래어 표기법 제3장 제1절 (영어의 표기)
        — https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0003&regltn_no=225

    Args:
        phonemes (List[str]): `_adjust_arpabet`을 거친 음소 리스트.

    Returns:
        str: 초·중·종성 자모와 반모음 자리표시자가 섞인 스트림.
    """
    ret = ""
    for i, p in enumerate(phonemes):
        p_prev = phonemes[i - 1] if i > 0 else '^'
        p_next = phonemes[i + 1] if i < len(phonemes) - 1 else '$'
        # g2pK 원본은 이 자리에서 i+1을 다시 읽는 오프바이원이 있어 바로잡았다.
        p_next2 = phonemes[i + 2] if i < len(phonemes) - 2 else '$'

        # 1항. 무성 파열음 [p], [t], [k]
        if p in "PTK":
            if p_prev[:2] in _SHORT_VOWELS and p_next == '$':
                ret += _ARPABET_CODAS[p]           # 1항 1: 짧은 모음 뒤 어말은 받침
            elif p_prev[:2] in _SHORT_VOWELS and p_next[0] not in "AEIOULRMN":
                ret += _ARPABET_CODAS[p]           # 1항 2: 짧은 모음과 자음 사이도 받침
            elif p_next[0] in _FINAL_OR_CONSONANTS:
                ret += _ARPABET_ONSETS[p] + N_EU   # 1항 3: 그 외 어말·자음 앞은 '으' 첨가
            else:
                ret += _ARPABET_ONSETS[p]

        # 2항. 유성 파열음 [b], [d], [g] — 어말·자음 앞은 '으' 첨가
        elif p in "BDG":
            ret += _ARPABET_ONSETS[p]
            if p_next[0] in _FINAL_OR_CONSONANTS:
                ret += N_EU

        # 3항. 마찰음 [s], [z], [f], [v], [θ], [ð], [ʃ], [ʒ]
        elif p in ('S', 'Z', 'F', 'V', "TH", "DH", "SH", "ZH"):
            ret += _ARPABET_ONSETS[p]
            if p in ('S', 'Z', 'F', 'V', "TH", "DH"):
                if p_next[0] in _FINAL_OR_CONSONANTS:
                    ret += N_EU                    # 3항 1: 어말·자음 앞은 '으' 첨가
            elif p == "SH":
                if p_next[0] == '$':
                    ret += N_I                     # 3항 2: 어말 [ʃ]는 '시'
                elif p_next[0] in _CONSONANT_INITIALS:
                    ret += N_YU                    # 3항 2: 자음 앞 [ʃ]는 '슈'
                else:
                    ret += 'Y'                     # 3항 2: 모음 앞은 뒤 모음 따라 샤·셔...
            elif p == "ZH":
                if p_next[0] in _FINAL_OR_CONSONANTS:
                    ret += N_I                     # 3항 3: 어말·자음 앞 [ʒ]는 '지'

        # 4항. 파찰음 [ʦ], [ʣ], [ʧ], [ʤ]
        elif p in ("TS", "DZ", "CH", "JH"):
            ret += _ARPABET_ONSETS[p]
            if p_next[0] in _FINAL_OR_CONSONANTS:
                ret += N_EU if p in ("TS", "DZ") else N_I

        # 5항. 비음 [m], [n], [ŋ] — 어말·자음 앞은 받침, 모음 앞 [m]/[n]은 초성
        elif p in ('M', 'N', "NG"):
            if p in "MN" and p_next[0] in _VOWEL_INITIALS:
                ret += _ARPABET_ONSETS[p]
            else:
                ret += _ARPABET_CODAS[p]

        # 6항. 유음 [l]
        elif p == 'L':
            if p_prev == '^':
                ret += _ARPABET_ONSETS[p]
            elif p_next[0] in "$BCDFGHJKLPQRSTVWXZ":
                ret += _ARPABET_CODAS[p]           # 6항 1: 어말·자음 앞은 받침
            elif p_prev in "MN":
                ret += _ARPABET_ONSETS[p]          # 6항 3: 비음 뒤는 모음 앞이라도 'ㄹ'
            elif p_next[0] in _VOWEL_INITIALS:
                ret += C_RIEUL + O_RIEUL           # 6항 2: 어중 [l]+모음은 'ㄹㄹ'
            elif p_next in "MN" and p_next2[0] not in _VOWEL_INITIALS:
                ret += C_RIEUL + O_RIEUL + N_EU    # 6항 2: 모음 없는 비음 앞은 'ㄹ르'

        # [ər]/[r] 관용 처리 (g2pK custom 분기 계승)
        elif p == "ER":
            if p_prev[0] in _VOWEL_INITIALS:
                ret += O_IEUNG
            ret += _ARPABET_NUCLEI[p]
            if p_next[0] in _VOWEL_INITIALS:
                ret += O_RIEUL
        elif p == 'R':
            if p_next[0] in _VOWEL_INITIALS:
                ret += _ARPABET_ONSETS[p]

        # 8항. 모음·중모음
        elif p[0] in "AEIOU":
            ret += _ARPABET_NUCLEI.get(p, p)

        else:
            ret += _ARPABET_ONSETS.get(p, p)

    return ret


def _compose_jamo_stream(stream: str) -> str:
    """
    자모 스트림에 반모음 병합을 적용하고 완성형 한글로 조립합니다.

    Args:
        stream (str): `_arpabet_to_jamo`가 만든 자모·자리표시자 스트림.

    Returns:
        str: 완성형 한글 문자열. (조립되지 못한 잔류 자모는 제거.)
    """
    for src, dst in _GLIDE_MERGES:
        stream = stream.replace(src, dst)

    # 초성 없는 중성 앞에 'ㅇ'을 채워 음절화한다
    stream = re.sub(
        "(^|[^ᄀ-ᄒ])([ᅡ-ᅵ])",
        lambda m: m.group(1) + O_IEUNG + m.group(2),
        stream,
    )
    stream = re.sub(
        "[ᄀ-ᄒ][ᅡ-ᅵ][ᆨ-ᇂ]",
        lambda m: join_jamos(m.group(0)[0], m.group(0)[1], m.group(0)[2]),
        stream,
    )
    stream = re.sub(
        "[ᄀ-ᄒ][ᅡ-ᅵ]",
        lambda m: join_jamos(m.group(0)[0], m.group(0)[1]),
        stream,
    )
    return re.sub("[ᄀ-ᇿ]", '', stream)


def read_english_words(text: str) -> str:
    """
    텍스트 속 CMU 사전 등재 영어 단어를 한글 표기로 변환합니다.

    한 글자 단어와 사전 미등재 단어는 그대로 두어 후속 단계(낱자 읽기)가 처리하게 합니다.

    Ref:
        g2pK english.py convert_eng
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/english.py#L12-L146

    Args:
        text (str): 원본 텍스트.

    Returns:
        str: 영어 단어가 한글 표기로 치환된 텍스트.
    """
    cmu = _load_cmu_dict()
    if cmu is None:
        return text

    for eng_word in set(re.findall(r"[A-Za-z']{2,}", text)):
        arpabets = cmu.get(eng_word.lower())
        if not arpabets:
            continue

        phonemes = _adjust_arpabet(arpabets)
        hangul = _compose_jamo_stream(_arpabet_to_jamo(phonemes))
        # 다른 단어 내부의 동일 철자를 오염시키지 않도록 라틴 문자 경계로 치환한다
        # (정규식 \b는 한글도 단어 문자로 보아 "school이야"의 경계를 놓치므로 쓰지 않는다)
        text = re.sub(
            rf"(?<![A-Za-z]){re.escape(eng_word)}(?![A-Za-z])", hangul, text)

    return text
