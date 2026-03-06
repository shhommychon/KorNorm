# [KorNorm 기호 및 노이즈 정규화 모듈]
# 
# 텍스트 내 불필요한 기호나 전사 노이즈를 선택적으로 제거하여 문장을 정규화합니다.
# 단순 삭제와 문장 끝 강조 표현 보존 기능을 제공합니다.

from typing import Iterable


def purge_symbols(text: str, targets: Iterable[str]) -> str:
    """
    텍스트 내의 모든 대상 문자열(targets)을 예외 없이 제거합니다.
    
    Args:
        text (str): 원본 텍스트.
        targets (Iterable[str]): 제거할 대상 문자열들의 모음.
        
    Returns:
        str: 대상 문자가 완전히 제거된 텍스트.
    """
    for target in targets:
        if not target:
            continue
        text = text.replace(target, '')
    return text

def remove_middle_symbols(text: str, targets: Iterable[str]) -> str:
    """
    텍스트 내의 대상 문자열들을 제거하되, 문장 맨 끝에 붙어 있는 경우는 단 1개만 유지합니다.
    (예: "안~녕~하세요~~" -> "안녕하세요~")
    
    Args:
        text (str): 원본 텍스트.
        targets (Iterable[str]): 제거할 대상 문자열들의 모음.
        
    Returns:
        str: 마지막 1개를 제외한 나머지 대상 문자가 제거된 텍스트.
    """
    if not text:
        return text

    # 긴 문자열부터 매칭하기 위해 길이순 정렬
    sorted_targets = sorted(list(targets), key=len, reverse=True)
    
    # 문장 끝에서 딱 한 번만 매칭되는 타겟을 찾음 (단 1개만 유지하기 위함)
    suffix = ''
    prefix = text
    
    for target in sorted_targets:
        if not target:
            continue
        if text.endswith(target):
            suffix = target
            prefix = text[:-len(target)]
            break
            
    # 나머지 앞부분에서는 대상 문자열들을 모두 제거
    for target in sorted_targets:
        if not target:
            continue
        prefix = prefix.replace(target, '')
        
    return prefix + suffix
