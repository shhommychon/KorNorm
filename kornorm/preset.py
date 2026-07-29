# [KorNorm 통합 프리셋 모듈]
#
# 텍스트 정규화(alphanumeric)와 표준발음법 엔진(phonology)을 한 번에 잇는
# 최상위 엔트리포인트를 제공합니다.

from typing import Literal

from kornorm.alphanumeric.preset import dealers_choice
from kornorm.phonology.engine import apply_phonology


def normalize(
    text: str,
    output_format: Literal["positional", "compat", "hangul"] = "hangul",
) -> str:
    """
    텍스트 정규화와 표준발음법 적용을 한 번에 수행합니다.

    숫자·단위·기호·영문을 한글로 정규화(`dealers_choice`)한 뒤 음운 변동 엔진을 통과시킵니다.
    정규화가 만든 수사가 음운 변동에 그대로 참여하므로, 표준 발음법 제29항의 숫자 예시
    "3 연대[삼 년대]"·"1 연대[일 련대]"와 가운뎃점 관용 독법 "6·25[유기오]"·"3·1절[사밀쩔]"이
    별도의 예외 처리 없이 규칙과 사전만으로 재현됩니다.

    Args:
        text (str): 원본 텍스트.
        output_format (str): 음운 엔진의 출력 형식 (기본값 "hangul").
            - "positional": U+11xx 위치 기반 자모 분리 상태
            - "compat": U+313x 호환 자모 분리 상태
            - "hangul": 초중종성이 결합된 완성형 한글

    Returns:
        str: 정규화와 음운 변동이 모두 적용된 문자열.
    """
    return apply_phonology(dealers_choice(text), output_format=output_format)
