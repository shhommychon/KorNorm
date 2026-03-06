# [KorNorm 자모 분해 및 합성 모듈]
# 
# 초성, 중성, 종성을 엄격히 구분하는 위치 기반 유니코드(U+11xx)를 사용합니다.
# G2P 정규식 및 Trie 치환 엔진에서 초성과 종성이 섞이는 오류를 원천 차단합니다.

# 초성 (Onset) - 19개
O_GIYEOK       = "\u1100"  # ㄱ
O_SSANGGIYEOK  = "\u1101"  # ㄲ
O_NIEUN        = "\u1102"  # ㄴ
O_DIGEUT       = "\u1103"  # ㄷ
O_SSANGDIGEUT  = "\u1104"  # ㄸ
O_RIEUL        = "\u1105"  # ㄹ
O_MIEUM        = "\u1106"  # ㅁ
O_BIEUP        = "\u1107"  # ㅂ
O_SSANGBIEUP   = "\u1108"  # ㅃ
O_SIOT         = "\u1109"  # ㅅ
O_SSANGSIOT    = "\u110a"  # ㅆ
O_IEUNG        = "\u110b"  # ㅇ
O_JIEUT        = "\u110c"  # ㅈ
O_SSANGJIEUT   = "\u110d"  # ㅉ
O_CHIEUT       = "\u110e"  # ㅊ
O_KIEUK        = "\u110f"  # ㅋ
O_TIEUT        = "\u1110"  # ㅌ
O_PIEUP        = "\u1111"  # ㅍ
O_HIEUT        = "\u1112"  # ㅎ

# 중성 (Nucleus) - 21개
N_A    = "\u1161"  # ㅏ
N_AE   = "\u1162"  # ㅐ
N_YA   = "\u1163"  # ㅑ
N_YAE  = "\u1164"  # ㅒ
N_EO   = "\u1165"  # ㅓ
N_E    = "\u1166"  # ㅔ
N_YEO  = "\u1167"  # ㅕ
N_YE   = "\u1168"  # ㅖ
N_O    = "\u1169"  # ㅗ
N_WA   = "\u116a"  # ㅘ
N_WAE  = "\u116b"  # ㅙ
N_OE   = "\u116c"  # ㅚ
N_YO   = "\u116d"  # ㅛ
N_U    = "\u116e"  # ㅜ
N_WEO  = "\u116f"  # ㅝ
N_WE   = "\u1170"  # ㅞ
N_WI   = "\u1171"  # ㅟ
N_YU   = "\u1172"  # ㅠ
N_EU   = "\u1173"  # ㅡ
N_UI   = "\u1174"  # ㅢ
N_I    = "\u1175"  # ㅣ

# 종성 (Coda) - 27개 + 종성 없음 1개 = 28개
C_NONE         = "\u3164"  # 종성 없음; Hangul Filler; 선언해야 3단위 슬라이싱이 안 깨짐
C_GIYEOK       = "\u11a8"  # ㄱ
C_SSANGGIYEOK  = "\u11a9"  # ㄲ
C_GIYEOK_SIOT  = "\u11aa"  # ㄳ
C_NIEUN        = "\u11ab"  # ㄴ
C_NIEUN_JIEUT  = "\u11ac"  # ㄵ
C_NIEUN_HIEUT  = "\u11ad"  # ㄶ
C_DIGEUT       = "\u11ae"  # ㄷ
C_RIEUL        = "\u11af"  # ㄹ
C_RIEUL_GIYEOK = "\u11b0"  # ㄺ
C_RIEUL_MIEUM  = "\u11b1"  # ㄻ
C_RIEUL_BIEUP  = "\u11b2"  # ㄼ
C_RIEUL_SIOT   = "\u11b3"  # ㄽ
C_RIEUL_TIEUT  = "\u11b4"  # ㄾ
C_RIEUL_PIEUP  = "\u11b5"  # ㄿ
C_RIEUL_HIEUT  = "\u11b6"  # ㅀ
C_MIEUM        = "\u11b7"  # ㅁ
C_BIEUP        = "\u11b8"  # ㅂ
C_BIEUP_SIOT   = "\u11b9"  # ㅄ
C_SIOT         = "\u11ba"  # ㅅ
C_SSANGSIOT    = "\u11bb"  # ㅆ
C_IEUNG        = "\u11bc"  # ㅇ
C_JIEUT        = "\u11bd"  # ㅈ
C_CHIEUT       = "\u11be"  # ㅊ
C_KIEUK        = "\u11bf"  # ㅋ
C_TIEUT        = "\u11c0"  # ㅌ
C_PIEUP        = "\u11c1"  # ㅍ
C_HIEUT        = "\u11c2"  # ㅎ

O_BASE = ord(O_GIYEOK)      # 0x1100 (초성 시작점)
O_END  = ord(O_HIEUT)       # 0x1112 (초성 끝점)

N_BASE = ord(N_A)           # 0x1161 (중성 시작점)
N_END  = ord(N_I)           # 0x1175 (중성 끝점)

C_BASE = ord(C_GIYEOK) - 1  # 0x11A7 (종성 시작점, 인덱스 계산용으로만 사용)
# 주의: 0x11A7은 모음(ᆧ)이므로 C_BASE를 문자로 변환하여 C_NONE으로 쓰면 안됩니다.
C_END  = ord(C_HIEUT)       # 0x11C2 (종성 끝점)

HANGUL_BASE = ord('가')     # 0xAC00
HANGUL_END  = ord('힣')     # 0xD7A3

def split_syllable_char(char: str) -> tuple:
    """
    단일 한글 문자를 위치 기반 자모(U+11xx)로 분리합니다.

    Ref:
        https://github.com/JDongian/python-jamo/blob/master/jamo/jamo.py#L52-L69
    
    Args:
        char (str): 분리할 단일 문자입니다.
        
    Returns:
        tuple: (초성, 중성, 종성)으로 구성된 튜플을 반환합니다. 
               종성이 없는 경우 세 번째 요소는 빈 문자열('')이 되며, 
               입력된 문자가 한글 음절(U+AC00~U+D7A3)이 아닐 경우 (char, '', '')를 반환합니다.
    """
    if not (HANGUL_BASE <= ord(char) <= HANGUL_END):
        return char, '', ''

    offset = ord(char) - HANGUL_BASE
    cho_idx = offset // 588
    joong_idx = (offset % 588) // 28
    jong_idx = offset % 28

    # U+1100: 초성 시작, U+1161: 중성 시작, U+11A7: 종성 시작(0은 종성 없음)
    cho = chr(O_BASE + cho_idx)
    joong = chr(N_BASE + joong_idx)
    jong = chr(C_BASE + jong_idx) if jong_idx > 0 else C_NONE   # C_NONE을 반환하여 길이가 3의 배수가 되도록 강제
    
    return cho, joong, jong


def decompose(text: str) -> str:
    """
    문자열 전체를 위치 기반 자모(U+11xx)로 평탄화(Flatten)합니다.

    Ref:
        https://github.com/JDongian/python-jamo/blob/master/jamo/jamo.py#L243-L266
    
    Args:
        text (str): 평탄화할 원본 문자열입니다.
        
    Returns:
        str: 한글 음절이 모두 초/중/종성으로 분해되어 나열된 문자열입니다. 
             한글 음절이 아닌 기호, 공백, 영문 등은 원본 그대로 유지됩니다.
    """
    result = []
    for char in text:
        if HANGUL_BASE <= ord(char) <= HANGUL_END:
            result.extend(split_syllable_char(char))
        else:
            result.append(char)
    return "".join(result)


def join_jamos(cho: str, joong: str, jong: str = '') -> str:
    """
    위치 기반 자모(U+11xx)를 다시 하나의 한글 문자로 결합합니다.

    Ref:
        https://github.com/JDongian/python-jamo/blob/master/jamo/jamo.py#L269-L305
    
    Args:
        cho (str): 초성 문자 (U+1100 ~ U+1112)입니다.
        joong (str): 중성 문자 (U+1161 ~ U+1175)입니다.
        jong (str, optional): 종성 문자 (U+11A8 ~ U+11C2) 또는 C_NONE(U+3164)입니다. 기본값은 빈 문자열('')입니다.
        
    Returns:
        str: 결합된 단일 한글 문자(음절)를 반환합니다. 
             만약 입력된 자모가 유효한 위치 기반 자모 영역이 아니라면, 
             조합하지 않고 입력받은 인자들을 그대로 이어 붙인 문자열을 반환합니다.
    """
    if not (O_BASE <= ord(cho) <= O_END and N_BASE <= ord(joong) <= N_END):
        return cho + joong + jong
        
    cho_idx = ord(cho) - O_BASE
    joong_idx = ord(joong) - N_BASE
    
    # 종성이 빈 문자열('')이거나 채움 문자(C_NONE)일 경우 0으로 처리
    if jong == '' or jong == C_NONE:
        jong_idx = 0
    elif C_BASE < ord(jong) <= C_END:
        jong_idx = ord(jong) - C_BASE
    else:
        # 유효하지 않은 종성이 들어오면 합치지 않고 그대로 반환
        return cho + joong + jong

    code = HANGUL_BASE + (cho_idx * 588) + (joong_idx * 28) + jong_idx
    return chr(code)


_POS_TO_COMPAT = {
    # 초성
    O_GIYEOK: 'ㄱ',
    O_SSANGGIYEOK: 'ㄲ',
    O_NIEUN: 'ㄴ',
    O_DIGEUT: 'ㄷ',
    O_SSANGDIGEUT: 'ㄸ',
    O_RIEUL: 'ㄹ',
    O_MIEUM: 'ㅁ',
    O_BIEUP: 'ㅂ',
    O_SSANGBIEUP: 'ㅃ',
    O_SIOT: 'ㅅ',
    O_SSANGSIOT: 'ㅆ',
    O_IEUNG: 'ㅇ',
    O_JIEUT: 'ㅈ',
    O_SSANGJIEUT: 'ㅉ',
    O_CHIEUT: 'ㅊ',
    O_KIEUK: 'ㅋ',
    O_TIEUT: 'ㅌ',
    O_PIEUP: 'ㅍ',
    O_HIEUT: 'ㅎ',

    # 중성
    N_A: 'ㅏ',
    N_AE: 'ㅐ',
    N_YA: 'ㅑ',
    N_YAE: 'ㅒ',
    N_EO: 'ㅓ',
    N_E: 'ㅔ',
    N_YEO: 'ㅕ',
    N_YE: 'ㅖ',
    N_O: 'ㅗ',
    N_WA: 'ㅘ',
    N_WAE: 'ㅙ',
    N_OE: 'ㅚ',
    N_YO: 'ㅛ',
    N_U: 'ㅜ',
    N_WEO: 'ㅝ',
    N_WE: 'ㅞ',
    N_WI: 'ㅟ',
    N_YU: 'ㅠ',
    N_EU: 'ㅡ',
    N_UI: 'ㅢ',
    N_I: 'ㅣ',

    # 종성
    C_GIYEOK: 'ㄱ',
    C_SSANGGIYEOK: 'ㄲ',
    C_GIYEOK_SIOT: 'ㄳ',
    C_NIEUN: 'ㄴ',
    C_NIEUN_JIEUT: 'ㄵ',
    C_NIEUN_HIEUT: 'ㄶ',
    C_DIGEUT: 'ㄷ',
    C_RIEUL: 'ㄹ',
    C_RIEUL_GIYEOK: 'ㄺ',
    C_RIEUL_MIEUM: 'ㄻ',
    C_RIEUL_BIEUP: 'ㄼ',
    C_RIEUL_SIOT: 'ㄽ',
    C_RIEUL_TIEUT: 'ㄾ',
    C_RIEUL_PIEUP: 'ㄿ',
    C_RIEUL_HIEUT: 'ㅀ',
    C_MIEUM: 'ㅁ',
    C_BIEUP: 'ㅂ',
    C_BIEUP_SIOT: 'ㅄ',
    C_SIOT: 'ㅅ',
    C_SSANGSIOT: 'ㅆ',
    C_IEUNG: 'ㅇ',
    C_JIEUT: 'ㅈ',
    C_CHIEUT: 'ㅊ',
    C_KIEUK: 'ㅋ',
    C_TIEUT: 'ㅌ',
    C_PIEUP: 'ㅍ',
    C_HIEUT: 'ㅎ',

    # 종성 없음
    C_NONE: ''
}
def to_compat_jamo(jamo_str: str) -> str:
    """
    위치 기반 자모(U+11xx) 문자열을 일반적인 호환 자모(U+313x)로 변환합니다.
    
    종성 없음(C_NONE) 기호는 빈 문자열로 치환하여 제거합니다.
    """
    return ''.join(_POS_TO_COMPAT.get(c, c) for c in jamo_str)
