# [KorNorm 문맥 동형어 판별 모듈]
#
# 표기가 같지만 발음이 갈리는 동형어를 문맥 단서(공기 어휘)로 판별합니다.
# 사전 리소스(stdict arrow)는 표면형당 발음 하나만 실을 수 있으므로, 문맥에 따라
# 발음이 달라지는 표면형만 여기에 등재합니다. 단서 표는 언어적 근거를 병기한
# 폐쇄 목록으로 유지하며, 판별은 양측 단서의 출현 수 비교(동수·무단서 시 default)로
# 수행합니다.

from typing import List, Optional

from kornorm.phonology.common import MorphToken

# 표면형별 판별 정보:
#   marked / unmarked: 유표(발음≠표기) / 무표(발음==표기) 독법.
#   *_cues: 해당 독법을 지지하는 공기 토큰 표면형 (형태소 분석 후의 어간·명사 형태).
#   default: 단서가 없거나 동수일 때 채택할 발음.
CONTEXT_HOMOGRAPHS = {
    # 잘 자리(침구) [잠짜리] vs 곤충 [잠자리]
    "잠자리": {
        "marked": "잠짜리",
        "unmarked": "잠자리",
        "marked_cues": ('펴', '눕', '들', '자', "이불", "침대", "베개", "숙소"),
        "unmarked_cues": ("난다", '날', "날아", '잡', '채', "곤충", "여름", "날개"),
        "default": "잠짜리",
    },
}


def resolve_homograph(surface: str, tokens: List[MorphToken]) -> Optional[str]:
    """
    문맥 단서를 집계하여 동형어 표면형의 발음을 판별합니다.

    문장 안 토큰 표면형과 단서 목록의 교집합 크기를 양측에서 세어 큰 쪽의 독법을
    채택하고, 동수(무단서 포함)면 default를 반환합니다.

    Args:
        surface (str): 판별 대상 표면형.
        tokens (List[MorphToken]): 같은 입력에 속한 전체 토큰 리스트 (문맥 창).

    Returns:
        Optional[str]: 판별된 발음. 등재되지 않은 표면형이면 None.
    """
    entry = CONTEXT_HOMOGRAPHS.get(surface)
    if entry is None:
        return None

    surfaces = {t.surface for t in tokens if not t.pos.startswith('S')}
    marked_hits = len(surfaces & set(entry["marked_cues"]))
    unmarked_hits = len(surfaces & set(entry["unmarked_cues"]))

    if marked_hits > unmarked_hits:
        return entry["marked"]
    if unmarked_hits > marked_hits:
        return entry["unmarked"]
    return entry["default"]
