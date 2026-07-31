# [KorNorm 기호 및 노이즈 정규화 모듈]
#
# 텍스트 내 불필요한 기호나 전사 노이즈를 선택적으로 제거하여 문장을 정규화합니다.
# 단순 삭제와 문장 끝 강조 표현 보존 기능을 제공합니다.

import re
from typing import Iterable, List, Tuple, Union


# 문장부호 제거용 기본 세트 (분류별 튜플 — 필요한 분류만 골라 조합할 수 있습니다)
SENTENCE_PUNCTUATION = ('.', ',', '!', '?', '…', '‥', ':', ';', '~')
BRACKET_PUNCTUATION = ('(', ')', '[', ']', '{', '}', '〈', '〉', '《', '》', '「', '」', '『', '』')
QUOTE_PUNCTUATION = ('"', "'", '“', '”', '‘', '’')
DASH_PUNCTUATION = ('—', '–', '―')
DEFAULT_PUNCTUATION = SENTENCE_PUNCTUATION + BRACKET_PUNCTUATION + QUOTE_PUNCTUATION + DASH_PUNCTUATION

# 공백 연속 축약용 패턴: 다음에 또 공백·탭이 오는 공백·탭(= 연속의 마지막 하나만 남김).
# 개행은 라인 기반 파이프라인의 단위이므로 건드리지 않습니다.
_RE_REDUNDANT_WHITESPACE = re.compile(r"[ \t](?=[ \t])")


def purge_symbols(text: str, targets: Iterable[Union[str, re.Pattern]]) -> str:
    """
    텍스트 내의 모든 대상(targets)을 예외 없이 제거합니다.

    Args:
        text (str): 원본 텍스트.
        targets (Iterable[str | re.Pattern]): 제거할 대상들의 모음.
            리터럴 문자열과 컴파일된 정규식 패턴을 섞어 넘길 수 있습니다.

    Returns:
        str: 대상이 완전히 제거된 텍스트.
    """
    for target in targets:
        if isinstance(target, re.Pattern):
            text = target.sub('', text)
        elif target:
            text = text.replace(target, '')
    return text

def remove_middle_symbols(text: str, targets: Iterable[Union[str, re.Pattern]]) -> str:
    """
    텍스트 내의 대상들을 제거하되, 문장 맨 끝에 붙어 있는 경우는 단 1개만 유지합니다.
    (예: "안~녕~하세요~~" -> "안녕하세요~")

    처리 순서는 리터럴(긴 것부터) -> 정규식 패턴(전달 순서)입니다. 문장 끝 보존은
    리터럴이면 접미 일치로, 패턴이면 마지막 매치가 문장 끝에 닿는 경우로 판정합니다.

    Args:
        text (str): 원본 텍스트.
        targets (Iterable[str | re.Pattern]): 제거할 대상들의 모음.
            리터럴 문자열과 컴파일된 정규식 패턴을 섞어 넘길 수 있습니다.

    Returns:
        str: 마지막 1개를 제외한 나머지 대상이 제거된 텍스트.
    """
    if not text:
        return text

    literals = [t for t in targets if not isinstance(t, re.Pattern)]
    patterns = [t for t in targets if isinstance(t, re.Pattern)]

    # 긴 문자열부터 매칭하기 위해 길이순 정렬
    sorted_literals = sorted(literals, key=len, reverse=True)

    # 문장 끝에서 딱 한 번만 매칭되는 타겟을 찾음 (단 1개만 유지하기 위함)
    suffix = ''
    prefix = text

    for target in sorted_literals:
        if not target:
            continue
        if text.endswith(target):
            suffix = target
            prefix = text[:-len(target)]
            break

    if not suffix:
        # 리터럴 접미가 없으면 패턴 매치 중 문장 끝에 닿는 것을 접미로 채택
        for pattern in patterns:
            last_match = None
            for match in pattern.finditer(text):
                last_match = match
            if last_match is not None and last_match.end() == len(text) and last_match.group():
                suffix = last_match.group()
                prefix = text[:last_match.start()]
                break

    # 나머지 앞부분에서는 대상들을 모두 제거
    for target in sorted_literals:
        if not target:
            continue
        prefix = prefix.replace(target, '')
    for pattern in patterns:
        prefix = pattern.sub('', prefix)

    return prefix + suffix

def find_symbols(
    text: str, targets: Iterable[Union[str, re.Pattern]]
) -> List[Tuple[int, int, str]]:
    """
    텍스트 내의 대상(targets) 매치를 위치와 함께 보고합니다.

    purge_symbols가 제거하는 바로 그 대상들을 텍스트 무변경으로 돌려주는 조회 전용
    짝꿍입니다. purge(text, targets) != text와 find(text, targets) != [] 는 동치입니다.
    remove_middle_symbols가 보존하는 문장 끝 1개도 여기서는 매치로 포함됩니다.

    Args:
        text (str): 검사할 원본 텍스트.
        targets (Iterable[str | re.Pattern]): 탐지할 대상들의 모음.
            리터럴 문자열과 컴파일된 정규식 패턴을 섞어 넘길 수 있습니다.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록.
            시작 위치순으로 정렬되며, text[시작:끝] == 매치 문자열이 성립합니다.
    """
    results = []
    for target in targets:
        if isinstance(target, re.Pattern):
            for match in target.finditer(text):
                if match.group():
                    results.append((match.start(), match.end(), match.group()))
        elif target:
            start = text.find(target)
            while start != -1:
                results.append((start, start + len(target), target))
                start = text.find(target, start + len(target))
    return sorted(results)

def strip_punctuation(text: str, targets: Iterable[Union[str, re.Pattern]] = DEFAULT_PUNCTUATION) -> str:
    """
    문장부호를 제거합니다. 기본 세트는 문장부호·괄호·인용부호·줄표입니다.

    기본 세트에서 의도적으로 제외한 것: ASCII 하이픈 '-'(전화번호·구간 등 의미 보유),
    가운뎃점 '·'(6·25 등 관용 독법의 재료), '%'·'+' 등 말로 읽는 기호
    (alphanumeric의 read_special_symbols 소관). 필요하면 targets로 직접 넘기십시오.

    Args:
        text (str): 원본 텍스트.
        targets (Iterable[str | re.Pattern]): 제거할 대상들의 모음 (기본값 DEFAULT_PUNCTUATION).

    Returns:
        str: 대상 문장부호가 제거된 텍스트.
    """
    return purge_symbols(text, targets)

def collapse_whitespace(text: str) -> str:
    """
    연속된 공백·탭을 하나로 축약하고 양 끝 공백을 정리합니다. 개행은 보존합니다.

    strip_punctuation이 부호를 지운 자리에 남는 이중 공백을 정리하는 짝꿍 함수로,
    보통 collapse_whitespace(strip_punctuation(text)) 형태로 이어 씁니다.

    Args:
        text (str): 원본 텍스트.

    Returns:
        str: 공백이 정돈된 텍스트.
    """
    return purge_symbols(text, (_RE_REDUNDANT_WHITESPACE,)).strip(" \t")
