# [KorNorm 반복 문구 제거 모듈]
#
# 딥러닝 모델의 추론 오류로 발생하는 무한 반복(열화) 현상을 탐지하고 축약합니다.

import re
from functools import lru_cache
from typing import List, Tuple

@lru_cache(maxsize=32)
def _get_degen_pattern(threshold: int) -> re.Pattern:
    """
    반복 횟수 임계치에 따른 정규식 패턴을 생성하고 캐싱합니다.
    threshold가 5라면, 특정 단위가 1번 나오고 그 뒤에 4번 이상 더 반복되는 패턴을 찾습니다.
    """
    # (.+?) : 최소 한 글자 이상의 반복 단위
    # \1{threshold-1,} : 해당 단위가 (threshold-1)번 이상 추가로 반복됨
    return re.compile(rf"(.+?)\1{{{threshold - 1},}}")

def fix_text_degeneration(text: str, repeat_count: int = 5, replace_char: str = '〃', rpad_space: bool = True) -> str:
    """
    텍스트 내의 비정상적인 반복 패턴을 탐지하여 축약합니다.
    
    Args:
        text (str): 정규화할 원본 텍스트.
        repeat_count (int): 허용할 최대 반복 횟수. 이 횟수를 넘어가면 축약 대상이 됩니다.
        replace_char (str): 축약된 위치를 표시할 구분자 (기본값: U+3003 〃).
        rpad_space (bool): 패턴 탐지 전 텍스트 끝에 공백을 추가할지 여부.
                          "으 으 으"와 같이 공백을 포함한 반복을 정확히 탐지하기 위해 사용합니다.
        
    Returns:
        str: 반복이 적절히 제어된 텍스트.
    """
    if repeat_count < 1 or len(text) < repeat_count:
        return text
    
    # 문장 끝 공백 패딩 처리: "으 으 으"를 "으 으 으 "로 만들어 "으 " 패턴 매칭 유도
    is_padded = False
    if rpad_space and not text.endswith(' '):
        text += ' '
        is_padded = True
    
    pattern = _get_degen_pattern(repeat_count)
    
    def replace_func(match: re.Match) -> str:
        repeating_unit = match.group(1)
        # 설정된 repeat_count 만큼만 반복을 남기고 구분자를 붙임
        return (repeating_unit * repeat_count) + replace_char
    
    text = pattern.sub(replace_func, text)

    # 임시로 추가했던 공백이 결과물 끝에 남지 않게 제거
    if replace_char != ' ' and text[-1] == ' ' and is_padded: text = text[:-1]

    return text

def find_text_degeneration(
    text: str, repeat_count: int = 5, rpad_space: bool = True
) -> List[Tuple[int, int, str, int]]:
    """
    텍스트 내의 비정상적인 반복 패턴을 탐지하여 위치와 함께 보고합니다.

    fix_text_degeneration이 축약하는 바로 그 매치들을 텍스트 무변경으로 돌려주는
    조회 전용 짝꿍입니다. fix(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.
        repeat_count (int): 허용할 최대 반복 횟수. 이 횟수를 넘어가면 탐지 대상이 됩니다.
        rpad_space (bool): 패턴 탐지 전 텍스트 끝에 공백을 추가할지 여부.
                          "으 으 으"와 같이 공백을 포함한 반복을 정확히 탐지하기 위해 사용합니다.

    Returns:
        List[Tuple[int, int, str, int]]: 매치별 (시작, 끝, 반복 단위, 반복 횟수) 목록.
            시작·끝은 원본 텍스트 기준 오프셋이며(패딩 공백 미포함으로 클램프),
            반복 횟수는 원본 안에서 단위가 통째로 나타난 횟수입니다.
    """
    if repeat_count < 1 or len(text) < repeat_count:
        return []

    original_len = len(text)
    if rpad_space and not text.endswith(' '):
        text += ' '

    pattern = _get_degen_pattern(repeat_count)

    results = []
    for match in pattern.finditer(text):
        unit = match.group(1)
        start = match.start()
        end = min(match.end(), original_len)
        results.append((start, end, unit, (end - start) // len(unit)))
    return results
