from dataclasses import dataclass

from kornorm.utils.jamo import (
    O_GIYEOK, O_DIGEUT, O_BIEUP, O_SIOT, O_JIEUT, O_IEUNG,
    O_SSANGGIYEOK, O_SSANGDIGEUT, O_SSANGBIEUP, O_SSANGSIOT, O_SSANGJIEUT,

    N_A, N_EO, N_YEO, N_EU, N_I,
)

# 경음화(된소리) 매핑 (예사소리 -> 된소리)
FORTIS_MAPPING = {
    O_GIYEOK: O_SSANGGIYEOK,
    O_DIGEUT: O_SSANGDIGEUT,
    O_BIEUP: O_SSANGBIEUP,
    O_SIOT: O_SSANGSIOT,
    O_JIEUT: O_SSANGJIEUT
}

# 파생 접미사 판별용 튜플
DERIV_SUFFIX_TAGS = ("XSN", "XSV", "XSA")

# 실질 형태소 판별용 튜플
SUBSTANTIVE_TAGS = (
    "N",    # 체언 전체 (NNG, NNP, NNB, NNBC, NR, NP)

    "M",    # 수식언 전체 (MM, MAG, MAJ)

    "VV",   # 동사
    "VA",   # 형용사
    "VX",   # 보조 용언
    "VCN",  # 부정 지정사 (아니다)
            # 주의: 긍정 지정사 "VCP"(이다)는 서술격 조사로 연음 대상이므로 제외

    "XR",   # 어근

    "IC",   # 감탄사

    "SN",   # 숫자 (예: 3 연대[삼년대])
    "SL",   # 외국어/알파벳
    "SH",   # 한자
)

@dataclass
class MorphToken:
    """형태소 단위의 데이터와 메타정보를 담는 순수 메모리 객체"""
    surface: str
    pos: str
    start_offset: int
    end_offset: int
    jamo_str: str
    is_hanja: bool = False
    compound_structure: str = ''


# 연음(제12항 4, 제13항, 제14항)·절음(제15항)·자모 이름(제16항)·구개음화(제17항)는 모두
# "뒤 형태소가 형식 형태소인지"를 기준으로 갈라지므로, 판별 로직을 하나로 모아 규칙 간 불일치를 방지한다.
_FUNCTIONAL_ONSET_VOWELS = (N_A, N_EO, N_YEO, N_EU, N_I)  # 실제 어미가 취할 수 있는 어두 모음 (아/어/여/으/이 계열)
def _is_functional(curr_token: MorphToken, next_token: MorphToken) -> bool:
    """
    뒤 토큰이 형식 형태소(조사, 어미, 접미사, 서술격 조사)인지 판별합니다.

    pecab의 대표적인 태깅 이상 두 가지를 함께 보정합니다:
    - 모음으로 시작하는 어미(E*) 태그가 ㅏ, ㅓ, ㅕ, ㅡ, ㅣ 이외의 모음으로 시작하면 실질 형태소의
      오태깅으로 간주합니다 (예: "겉옷" -> 겉/VA + 옷/EC. 실제 어미는 그런 모음으로 시작하지 않음).
    - 용언 어간 바로 뒤의 단음절 '음'/'이'가 명사(NNG)·부사(MAG)·감탄사(IC) 등으로 오분석되면
      전성어미(-음)나 파생 접미사(-이)로 간주합니다
      (예: "헛웃음을" -> 웃/VV+EP + 음/NNG, "벼훑이" -> 훑/VV + 이/IC).

    Args:
        curr_token (MorphToken): 판별 문맥이 되는 앞 토큰.
        next_token (MorphToken): 형식 형태소 여부를 판별할 뒤 토큰.

    Returns:
        bool: 형식 형태소로 판단되면 True.
    """
    next_jamo = next_token.jamo_str
    if next_token.pos.startswith('E') and len(next_jamo) >= 2:
        if next_jamo[0] == O_IEUNG and next_jamo[1] not in _FUNCTIONAL_ONSET_VOWELS:
            return False

    if next_token.pos.startswith(('J', 'E', "VCP")) or next_token.pos in DERIV_SUFFIX_TAGS:
        return True

    if next_token.surface in ('음', '이') and curr_token.pos.startswith('V'):
        return True

    return False
    
