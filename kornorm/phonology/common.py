from kornorm.utils.jamo import (
    O_GIYEOK, O_DIGEUT, O_BIEUP, O_SIOT, O_JIEUT,
    O_SSANGGIYEOK, O_SSANGDIGEUT, O_SSANGBIEUP, O_SSANGSIOT, O_SSANGJIEUT,
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
