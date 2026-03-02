# [KorNorm 자모 분해 및 합성 모듈]
# 
# 초성, 중성, 종성을 엄격히 구분하는 위치 기반 유니코드(U+11xx)를 사용합니다.
# G2P 정규식 및 Trie 치환 엔진에서 초성과 종성이 섞이는 오류를 원천 차단합니다.

HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3

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
    cho = chr(0x1100 + cho_idx)
    joong = chr(0x1161 + joong_idx)
    jong = chr(0x11A7 + jong_idx) if jong_idx > 0 else ''
    
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
        jong (str, optional): 종성 문자 (U+11A8 ~ )입니다. 기본값은 빈 문자열('')입니다.
        
    Returns:
        str: 결합된 단일 한글 문자(음절)를 반환합니다. 
             만약 입력된 `cho`와 `joong`이 유효한 위치 기반 자모 영역이 아니라면, 
             조합하지 않고 입력받은 인자들을 그대로 이어 붙인 문자열을 반환합니다.
    """
    # 유효한 U+11xx 영역인지 검증
    if not (0x1100 <= ord(cho) <= 0x1112 and 0x1161 <= ord(joong) <= 0x1175):
        return cho + joong + jong
        
    cho_idx = ord(cho) - 0x1100
    joong_idx = ord(joong) - 0x1161
    jong_idx = ord(jong) - 0x11A7 if jong else 0

    code = HANGUL_BASE + (cho_idx * 588) + (joong_idx * 28) + jong_idx
    return chr(code)
