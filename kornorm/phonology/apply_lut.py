# [KorNorm 음절 경계면 상호작용 적용 모듈]
#
# 형태소와 형태소가 만나는 경계에서 발생하는 음운 변동을 2D LUT를 통해 해결합니다.
# 표준 발음법 제4장(받침의 발음), 제5장(음의 동화), 제6장(경음화)의 규칙들이 인접한 두 자모 사이에서
# 어떻게 발현되는지를 결정론적으로 처리합니다.

from typing import List
from kornorm.phonology.common import MorphToken

from kornorm.utils.jamo import (
    O_GIYEOK, O_SSANGGIYEOK, O_NIEUN, O_DIGEUT, O_SSANGDIGEUT,
    O_RIEUL, O_MIEUM, O_BIEUP, O_SSANGBIEUP, O_SIOT,
    O_SSANGSIOT, O_IEUNG, O_JIEUT, O_SSANGJIEUT, O_CHIEUT,
    O_KIEUK, O_TIEUT, O_PIEUP, O_HIEUT,

    C_NONE,
    C_GIYEOK, C_SSANGGIYEOK, C_GIYEOK_SIOT, C_NIEUN, C_NIEUN_JIEUT,
    C_NIEUN_HIEUT, C_DIGEUT, C_RIEUL, C_RIEUL_GIYEOK, C_RIEUL_MIEUM,
    C_RIEUL_BIEUP, C_RIEUL_SIOT, C_RIEUL_TIEUT, C_RIEUL_PIEUP, C_RIEUL_HIEUT,
    C_MIEUM, C_BIEUP, C_BIEUP_SIOT, C_SIOT, C_SSANGSIOT,
    C_IEUNG, C_JIEUT, C_CHIEUT, C_KIEUK, C_TIEUT,
    C_PIEUP, C_HIEUT,
)

O_EOW = "<EOW>"  # 어말 또는 뒤에 자음이 없는 상태를 의미하는 특수 초성 키

PHONOLOGY_LUT = {
    C_GIYEOK: {
        O_GIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "23항"),
        O_NIEUN: (C_IEUNG, O_NIEUN, "18항"),
        O_DIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "23항"),
        O_MIEUM: (C_IEUNG, O_MIEUM, "18항"),
        O_BIEUP: (C_GIYEOK, O_SSANGBIEUP, "23항"),
        O_SIOT: (C_GIYEOK, O_SSANGSIOT, "23항"),
        O_JIEUT: (C_GIYEOK, O_SSANGJIEUT, "23항"),
        O_HIEUT: (C_NONE, O_KIEUK, "12항"),
        O_RIEUL: (C_IEUNG, O_NIEUN, "19항|18항"),
    },
    C_KIEUK: {
        O_GIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_GIYEOK, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_IEUNG, O_NIEUN, "18항"),
        O_DIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_GIYEOK, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_IEUNG, O_MIEUM, "9항|18항"),
        O_BIEUP: (C_GIYEOK, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_GIYEOK, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_GIYEOK, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_GIYEOK, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_GIYEOK, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_GIYEOK, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_GIYEOK, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_GIYEOK, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_KIEUK, "Kyubyong/g2pK"),
        O_RIEUL: (C_IEUNG, O_NIEUN, "9항|18항"),
        O_EOW: (C_GIYEOK, O_EOW, "9항"),
    },
    C_SSANGGIYEOK: {
        O_GIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_GIYEOK, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_IEUNG, O_NIEUN, "18항"),
        O_DIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_GIYEOK, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_IEUNG, O_MIEUM, "18항"),
        O_BIEUP: (C_GIYEOK, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_GIYEOK, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_GIYEOK, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_GIYEOK, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_GIYEOK, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_GIYEOK, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_GIYEOK, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_GIYEOK, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_KIEUK, "Kyubyong/g2pK"),
        O_RIEUL: (C_IEUNG, O_NIEUN, "Kyubyong/g2pK"),
        O_EOW: (C_GIYEOK, O_EOW, "9항"),
    },
    C_GIYEOK_SIOT: {
        O_GIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_GIYEOK, O_KIEUK, "10항"),
        O_SSANGGIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_IEUNG, O_NIEUN, "18항"),
        O_DIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_GIYEOK, O_TIEUT, "10항"),
        O_SSANGDIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_IEUNG, O_MIEUM, "18항"),
        O_BIEUP: (C_GIYEOK, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_GIYEOK, O_PIEUP, "10항"),
        O_SSANGBIEUP: (C_GIYEOK, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_GIYEOK, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_GIYEOK, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_GIYEOK, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_GIYEOK, O_CHIEUT, "10항"),
        O_SSANGJIEUT: (C_GIYEOK, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_NONE, O_KIEUK, "Kyubyong/g2pK"),
        O_RIEUL: (C_IEUNG, O_NIEUN, "Kyubyong/g2pK"),
        O_EOW: (C_GIYEOK, O_EOW, "10항"),
    },
    C_NIEUN: {
        O_RIEUL: (C_RIEUL, O_RIEUL, "20항"),
    },
    C_DIGEUT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "23항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "23항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "23항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "23항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "23항"),
        O_HIEUT: (C_NONE, O_TIEUT, "12항"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "Kyubyong/g2pK"),
    },
    C_TIEUT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_DIGEUT, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_DIGEUT, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_DIGEUT, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_DIGEUT, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_DIGEUT, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_TIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_EOW: (C_DIGEUT, O_EOW, "9항"),
    },
    C_NIEUN_JIEUT: {
        O_GIYEOK: (C_NIEUN, O_GIYEOK, "10항"),
        O_KIEUK: (C_NIEUN, O_KIEUK, "10항"),
        O_SSANGGIYEOK: (C_NIEUN, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "10항"),
        O_DIGEUT: (C_NIEUN, O_DIGEUT, "10항"),
        O_TIEUT: (C_NIEUN, O_TIEUT, "10항"),
        O_SSANGDIGEUT: (C_NIEUN, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "10항"),
        O_BIEUP: (C_NIEUN, O_BIEUP, "10항"),
        O_PIEUP: (C_NIEUN, O_PIEUP, "10항"),
        O_SSANGBIEUP: (C_NIEUN, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_NIEUN, O_SIOT, "10항"),
        O_SSANGSIOT: (C_NIEUN, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_NIEUN, O_JIEUT, "10항"),
        O_CHIEUT: (C_NIEUN, O_CHIEUT, "10항"),
        O_SSANGJIEUT: (C_NIEUN, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_NIEUN, O_CHIEUT, "12항"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "10항|20항"),
        O_EOW: (C_NIEUN, O_EOW, "10항"),
    },
    C_NIEUN_HIEUT: {
        O_GIYEOK: (C_NIEUN, O_KIEUK, "12항"),
        O_KIEUK: (C_NIEUN, O_KIEUK, "Kyubyong/g2pK"),
        O_SSANGGIYEOK: (C_NIEUN, O_SSANGGIYEOK, "Kyubyong/g2pK"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "12항"),
        O_DIGEUT: (C_NIEUN, O_TIEUT, "12항"),
        O_TIEUT: (C_NIEUN, O_TIEUT, "Kyubyong/g2pK"),
        O_SSANGDIGEUT: (C_NIEUN, O_SSANGDIGEUT, "Kyubyong/g2pK"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "Kyubyong/g2pK"),
        O_BIEUP: (C_NIEUN, O_BIEUP, "Kyubyong/g2pK"),
        O_PIEUP: (C_NIEUN, O_PIEUP, "Kyubyong/g2pK"),
        O_SSANGBIEUP: (C_NIEUN, O_SSANGBIEUP, "Kyubyong/g2pK"),
        O_SIOT: (C_NIEUN, O_SSANGSIOT, "12항"),
        O_SSANGSIOT: (C_NIEUN, O_SSANGSIOT, "Kyubyong/g2pK"),
        O_JIEUT: (C_NIEUN, O_CHIEUT, "12항"),
        O_CHIEUT: (C_NIEUN, O_CHIEUT, "Kyubyong/g2pK"),
        O_SSANGJIEUT: (C_NIEUN, O_SSANGJIEUT, "Kyubyong/g2pK"),
        O_HIEUT: (C_NIEUN, O_HIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "Kyubyong/g2pK"),
        O_EOW: (C_NIEUN, O_EOW, "Kyubyong/g2pK"),
    },
    C_MIEUM: {
        O_RIEUL: (C_MIEUM, O_NIEUN, "19항"),
    },
    C_BIEUP: {
        O_GIYEOK: (C_BIEUP, O_SSANGGIYEOK, "23항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "18항"),
        O_DIGEUT: (C_BIEUP, O_SSANGDIGEUT, "23항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "18항"),
        O_BIEUP: (C_BIEUP, O_SSANGBIEUP, "23항"),
        O_SIOT: (C_BIEUP, O_SSANGSIOT, "23항"),
        O_JIEUT: (C_BIEUP, O_SSANGJIEUT, "23항"),
        O_HIEUT: (C_NONE, O_PIEUP, "12항"),
        O_RIEUL: (C_MIEUM, O_NIEUN, "19항|18항"),
    },
    C_PIEUP: {
        O_GIYEOK: (C_BIEUP, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_BIEUP, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_BIEUP, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "18항"),
        O_DIGEUT: (C_BIEUP, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_BIEUP, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_BIEUP, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "18항"),
        O_BIEUP: (C_BIEUP, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_BIEUP, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_BIEUP, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_BIEUP, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_BIEUP, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_BIEUP, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_BIEUP, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_BIEUP, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_PIEUP, "Kyubyong/g2pK"),
        O_RIEUL: (C_MIEUM, O_NIEUN, "9항|18항"),                    # g2pK 원본 정규식("ᆫ\1ᄂ(9/18)") 수정. 9항 선적용 후("ᆸ\1ᄂ") 18항을 거쳐 최종적으로 "ᆷ\1ᄂ"가 되는 논리로 다이렉트 매핑.
        O_EOW: (C_BIEUP, O_EOW, "9항"),
    },
    C_BIEUP_SIOT: {
        O_GIYEOK: (C_BIEUP, O_SSANGGIYEOK, "10항|23항"),
        O_KIEUK: (C_BIEUP, O_KIEUK, "10항"),                        # g2pK 원본 정규식("ᆸ\1ᄑ") 수정. 10항에 기반한 "ᆸ\1ᄏ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGGIYEOK: (C_BIEUP, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "10항|18항"),
        O_DIGEUT: (C_BIEUP, O_SSANGDIGEUT, "10항|23항"),
        O_TIEUT: (C_BIEUP, O_TIEUT, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆸ\1ᄐ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGDIGEUT: (C_BIEUP, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "10항|18항"),
        O_BIEUP: (C_BIEUP, O_SSANGBIEUP, "10항|23항"),
        O_PIEUP: (C_BIEUP, O_PIEUP, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆸ\1ᄑ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGBIEUP: (C_BIEUP, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_BIEUP, O_SSANGSIOT, "10항|23항"),
        O_SSANGSIOT: (C_BIEUP, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_BIEUP, O_SSANGJIEUT, "10항|23항"),
        O_CHIEUT: (C_BIEUP, O_CHIEUT, "10항"),                      # g2pK 원본 정규식("ᆸ\1ᄎ(1ᄐ(10)") 수정. 원본 엔진의 괄호 파싱 로직에 의해 "ᆸ\1ᄎ"로 작동하던 것을 계승하여 매핑.
        O_SSANGJIEUT: (C_BIEUP, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_BIEUP, O_PIEUP, "10항"),
        O_RIEUL: (C_MIEUM, O_NIEUN, "10항|19항|18항"),
        O_EOW: (C_BIEUP, O_EOW, "10항"),
    },
    C_SIOT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_DIGEUT, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_DIGEUT, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "9항|18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_DIGEUT, O_PIEUP, "9항|tenebo/g2pk2"),           # g2pK 원본 정규식("ᆮ1ᄑ(9)") 수정. 백레퍼런스 누락을 수정한 tenebo/g2pk2@7140979의 "ᆮ\1ᄑ(9)" 패치 논리를 반영.
        O_SSANGBIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_DIGEUT, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_DIGEUT, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_TIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_EOW: (C_DIGEUT, O_EOW, "9항"),
    },
    C_SSANGSIOT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_DIGEUT, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_DIGEUT, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "9항|18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_DIGEUT, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_DIGEUT, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_DIGEUT, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_TIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_EOW: (C_DIGEUT, O_EOW, "9항"),
    },
    C_JIEUT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_DIGEUT, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_DIGEUT, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_DIGEUT, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_DIGEUT, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_DIGEUT, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_CHIEUT, "12항"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_EOW: (C_DIGEUT, O_EOW, "9항"),
    },
    C_CHIEUT: {
        O_GIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항|23항"),
        O_KIEUK: (C_DIGEUT, O_KIEUK, "9항"),
        O_SSANGGIYEOK: (C_DIGEUT, O_SSANGGIYEOK, "9항"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "18항"),
        O_DIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항|23항"),
        O_TIEUT: (C_DIGEUT, O_TIEUT, "9항"),
        O_SSANGDIGEUT: (C_DIGEUT, O_SSANGDIGEUT, "9항"),
        O_MIEUM: (C_NIEUN, O_MIEUM, "18항"),
        O_BIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항|23항"),
        O_PIEUP: (C_DIGEUT, O_PIEUP, "9항"),
        O_SSANGBIEUP: (C_DIGEUT, O_SSANGBIEUP, "9항"),
        O_SIOT: (C_DIGEUT, O_SSANGSIOT, "9항|23항"),
        O_SSANGSIOT: (C_DIGEUT, O_SSANGSIOT, "9항"),
        O_JIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항|23항"),
        O_CHIEUT: (C_DIGEUT, O_CHIEUT, "9항"),
        O_SSANGJIEUT: (C_DIGEUT, O_SSANGJIEUT, "9항"),
        O_HIEUT: (C_NONE, O_TIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_NIEUN, O_NIEUN, "9항|18항"),
        O_EOW: (C_DIGEUT, O_EOW, "9항"),
    },
    C_IEUNG: {
        O_RIEUL: (C_IEUNG, O_NIEUN, "19항"),
    },
    C_HIEUT: {
        O_GIYEOK: (C_NONE, O_KIEUK, "12항"),
        O_KIEUK: (C_NONE, O_KIEUK, "Kyubyong/g2pK"),
        O_SSANGGIYEOK: (C_NONE, O_SSANGGIYEOK, "Kyubyong/g2pK"),
        O_NIEUN: (C_NIEUN, O_NIEUN, "12항"),
        O_DIGEUT: (C_NONE, O_TIEUT, "12항"),
        O_TIEUT: (C_NONE, O_TIEUT, "Kyubyong/g2pK"),
        O_SSANGDIGEUT: (C_NONE, O_SSANGDIGEUT, "Kyubyong/g2pK"),
        O_MIEUM: (C_NONE, O_MIEUM, "Kyubyong/g2pK"),
        O_BIEUP: (C_NONE, O_BIEUP, "Kyubyong/g2pK"),
        O_PIEUP: (C_NONE, O_PIEUP, "Kyubyong/g2pK"),
        O_SSANGBIEUP: (C_NONE, O_SSANGBIEUP, "Kyubyong/g2pK"),
        O_SIOT: (C_NONE, O_SSANGSIOT, "12항"),
        O_SSANGSIOT: (C_NONE, O_SSANGSIOT, "Kyubyong/g2pK"),
        O_JIEUT: (C_NONE, O_CHIEUT, "12항"),
        O_CHIEUT: (C_NONE, O_CHIEUT, "Kyubyong/g2pK"),
        O_SSANGJIEUT: (C_NONE, O_SSANGJIEUT, "Kyubyong/g2pK"),
        O_HIEUT: (C_NONE, O_HIEUT, "Kyubyong/g2pK"),
        O_RIEUL: (C_NONE, O_RIEUL, "Kyubyong/g2pK"),
        O_EOW: (C_DIGEUT, O_EOW, "Kyubyong/g2pK"),
    },
    C_RIEUL: {
        O_NIEUN: (C_RIEUL, O_RIEUL, "20항"),
    },
    C_RIEUL_GIYEOK: {
        O_GIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "11항|23항"),
        O_KIEUK: (C_GIYEOK, O_KIEUK, "11항"),                       # g2pK 원본 정규식("1)") 수정. tenebo/g2pk2@7140979는 이를 "ᆯ\1ᄏ(12)"로 패치하였으나, KorNorm에서는 11항에 기반한 "ᆨ\1ᄏ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGGIYEOK: (C_GIYEOK, O_SSANGGIYEOK, "11항"),
        O_NIEUN: (C_IEUNG, O_NIEUN, "11항|18항"),
        O_DIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "11항|23항"),
        O_TIEUT: (C_GIYEOK, O_TIEUT, "11항"),                       # g2pK 원본 정규식("ᆨ\1ᄑ(11)") 수정. 11항에 기반한 "ᆨ\1ᄐ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGDIGEUT: (C_GIYEOK, O_SSANGDIGEUT, "11항"),
        O_MIEUM: (C_IEUNG, O_MIEUM, "11항|18항"),
        O_BIEUP: (C_GIYEOK, O_SSANGBIEUP, "11항|23항"),
        O_PIEUP: (C_GIYEOK, O_PIEUP, "11항"),                       # g2pK 원본 누락 케이스 보완. 11항에 기반한 "ᆨ\1ᄑ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGBIEUP: (C_GIYEOK, O_SSANGBIEUP, "11항"),
        O_SIOT: (C_GIYEOK, O_SSANGSIOT, "11항|23항"),
        O_SSANGSIOT: (C_GIYEOK, O_SSANGSIOT, "11항"),
        O_JIEUT: (C_GIYEOK, O_SSANGJIEUT, "11항|23항"),
        O_CHIEUT: (C_GIYEOK, O_CHIEUT, "11항"),
        O_SSANGJIEUT: (C_GIYEOK, O_SSANGJIEUT, "11항"),
        O_HIEUT: (C_RIEUL, O_KIEUK, "12항"),
        O_RIEUL: (C_IEUNG, O_NIEUN, "11항|18항"),
        O_EOW: (C_GIYEOK, O_EOW, "11항"),
    },
    C_RIEUL_TIEUT: {
        O_GIYEOK: (C_RIEUL, O_GIYEOK, "10항"),
        O_KIEUK: (C_RIEUL, O_KIEUK, "10항"),
        O_SSANGGIYEOK: (C_RIEUL, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_RIEUL, O_RIEUL, "10항|20항"),
        O_DIGEUT: (C_RIEUL, O_DIGEUT, "10항"),
        O_TIEUT: (C_RIEUL, O_TIEUT, "10항"),
        O_SSANGDIGEUT: (C_RIEUL, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_RIEUL, O_MIEUM, "10항"),
        O_BIEUP: (C_RIEUL, O_BIEUP, "10항"),
        O_PIEUP: (C_RIEUL, O_PIEUP, "10항"),
        O_SSANGBIEUP: (C_RIEUL, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_RIEUL, O_SIOT, "10항"),
        O_SSANGSIOT: (C_RIEUL, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_RIEUL, O_JIEUT, "10항"),
        O_CHIEUT: (C_RIEUL, O_CHIEUT, "10항"),
        O_SSANGJIEUT: (C_RIEUL, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_RIEUL, O_HIEUT, "10항"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "10항"),
        O_EOW: (C_RIEUL, O_EOW, "10항"),
    },
    C_RIEUL_MIEUM: {
        O_GIYEOK: (C_MIEUM, O_GIYEOK, "11항"),
        O_KIEUK: (C_MIEUM, O_KIEUK, "11항"),
        O_SSANGGIYEOK: (C_MIEUM, O_SSANGGIYEOK, "11항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "11항"),
        O_DIGEUT: (C_MIEUM, O_DIGEUT, "11항"),
        O_TIEUT: (C_MIEUM, O_TIEUT, "11항"),
        O_SSANGDIGEUT: (C_MIEUM, O_SSANGDIGEUT, "11항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "11항"),
        O_BIEUP: (C_MIEUM, O_BIEUP, "11항"),
        O_PIEUP: (C_MIEUM, O_PIEUP, "11항"),
        O_SSANGBIEUP: (C_MIEUM, O_SSANGBIEUP, "11항"),
        O_SIOT: (C_MIEUM, O_SIOT, "11항"),
        O_SSANGSIOT: (C_MIEUM, O_SSANGSIOT, "11항"),
        O_JIEUT: (C_MIEUM, O_JIEUT, "11항"),
        O_CHIEUT: (C_MIEUM, O_CHIEUT, "11항"),
        O_SSANGJIEUT: (C_MIEUM, O_SSANGJIEUT, "11항"),
        O_HIEUT: (C_MIEUM, O_HIEUT, "11항"),
        O_RIEUL: (C_MIEUM, O_RIEUL, "11항"),
        O_EOW: (C_MIEUM, O_EOW, "11항"),
    },
    C_RIEUL_BIEUP: {
        O_GIYEOK: (C_RIEUL, O_SSANGGIYEOK, "10항|23항"),
        O_KIEUK: (C_RIEUL, O_KIEUK, "10항"),                        # g2pK 원본 정규식("ᆯ\1ᄏ(10)0)") 수정. 원본 엔진의 괄호 파싱 로직에 의해 "ᆯ\1ᄏ"로 작동하던 것을 계승하여 매핑.
        O_SSANGGIYEOK: (C_RIEUL, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "18항"),
        O_DIGEUT: (C_RIEUL, O_SSANGDIGEUT, "10항|23항"),
        O_TIEUT: (C_RIEUL, O_TIEUT, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆯ\1ᄐ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGDIGEUT: (C_RIEUL, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "18항"),
        O_BIEUP: (C_RIEUL, O_SSANGBIEUP, "10항|23항"),
        O_PIEUP: (C_RIEUL, O_PIEUP, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆯ\1ᄑ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGBIEUP: (C_RIEUL, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_RIEUL, O_SSANGSIOT, "10항|23항"),
        O_SSANGSIOT: (C_RIEUL, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_RIEUL, O_SSANGJIEUT, "10항|23항"),
        O_CHIEUT: (C_RIEUL, O_CHIEUT, "10항"),
        O_SSANGJIEUT: (C_RIEUL, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_RIEUL, O_PIEUP, "12항"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "10항"),
        O_EOW: (C_RIEUL, O_EOW, "10항"),
    },
    C_RIEUL_PIEUP: {
        O_GIYEOK: (C_BIEUP, O_SSANGGIYEOK, "11항|23항"),
        O_KIEUK: (C_BIEUP, O_KIEUK, "11항"),                        # g2pK 원본 정규식("ᆸ\1ᆸ\1ᄑ") 수정. 11항에 기반한 "ᆸ\1ᄏ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGGIYEOK: (C_BIEUP, O_SSANGGIYEOK, "11항"),
        O_NIEUN: (C_MIEUM, O_NIEUN, "18항"),
        O_DIGEUT: (C_BIEUP, O_SSANGDIGEUT, "11항|23항"),
        O_TIEUT: (C_BIEUP, O_TIEUT, "11항"),                        # g2pK 원본 누락 케이스 보완. 11항에 기반한 "ᆸ\1ᄐ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGDIGEUT: (C_BIEUP, O_SSANGDIGEUT, "11항"),
        O_MIEUM: (C_MIEUM, O_MIEUM, "11항|18항"),
        O_BIEUP: (C_BIEUP, O_SSANGBIEUP, "11항|23항"),
        O_PIEUP: (C_BIEUP, O_PIEUP, "11항"),                        # g2pK 원본 누락 케이스 보완. 11항에 기반한 "ᆸ\1ᄑ(11)" 정규식과 동일한 논리를 적용.
        O_SSANGBIEUP: (C_BIEUP, O_SSANGBIEUP, "11항"),
        O_SIOT: (C_BIEUP, O_SSANGSIOT, "11항|23항"),
        O_SSANGSIOT: (C_BIEUP, O_SSANGSIOT, "11항"),
        O_JIEUT: (C_BIEUP, O_SSANGJIEUT, "11항|23항"),
        O_CHIEUT: (C_BIEUP, O_CHIEUT, "11항"),
        O_SSANGJIEUT: (C_BIEUP, O_SSANGJIEUT, "11항"),
        O_HIEUT: (C_BIEUP, O_PIEUP, "11항|12항"),
        O_RIEUL: (C_MIEUM, O_RIEUL, "11항"),
        O_EOW: (C_BIEUP, O_EOW, "11항"),
    },
    C_RIEUL_SIOT: {
        O_GIYEOK: (C_RIEUL, O_SSANGGIYEOK, "10항|23항"),
        O_KIEUK: (C_RIEUL, O_KIEUK, "10항"),                        # g2pK 원본 정규식("ᆯ\1ᄏ(ᄑ(10)") 수정. 원본 엔진의 괄호 파싱 로직에 의해 "ᆯ\1ᄏ"로 작동하던 것을 계승하여 매핑.
        O_SSANGGIYEOK: (C_RIEUL, O_SSANGGIYEOK, "10항"),
        O_NIEUN: (C_RIEUL, O_RIEUL, "10항|20항"),
        O_DIGEUT: (C_RIEUL, O_SSANGDIGEUT, "10항|23항"),
        O_TIEUT: (C_RIEUL, O_TIEUT, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆯ\1ᄐ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGDIGEUT: (C_RIEUL, O_SSANGDIGEUT, "10항"),
        O_MIEUM: (C_RIEUL, O_MIEUM, "10항"),
        O_BIEUP: (C_RIEUL, O_SSANGBIEUP, "10항|23항"),
        O_PIEUP: (C_RIEUL, O_PIEUP, "10항"),                        # g2pK 원본 누락 케이스 보완. 10항에 기반한 "ᆯ\1ᄑ(10)" 정규식과 동일한 논리를 적용.
        O_SSANGBIEUP: (C_RIEUL, O_SSANGBIEUP, "10항"),
        O_SIOT: (C_RIEUL, O_SSANGSIOT, "10항|23항"),
        O_SSANGSIOT: (C_RIEUL, O_SSANGSIOT, "10항"),
        O_JIEUT: (C_RIEUL, O_SSANGJIEUT, "10항|23항"),
        O_CHIEUT: (C_RIEUL, O_CHIEUT, "10항"),
        O_SSANGJIEUT: (C_RIEUL, O_SSANGJIEUT, "10항"),
        O_HIEUT: (C_RIEUL, O_HIEUT, "10항"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "10항"),
        O_EOW: (C_RIEUL, O_EOW, "10항"),
    },
    C_RIEUL_HIEUT: {
        O_GIYEOK: (C_RIEUL, O_KIEUK, "12항"),
        O_KIEUK: (C_RIEUL, O_KIEUK, "Kyubyong/g2pK"),
        O_SSANGGIYEOK: (C_RIEUL, O_SSANGGIYEOK, "Kyubyong/g2pK"),
        O_NIEUN: (C_RIEUL, O_RIEUL, "12항|20항"),
        O_DIGEUT: (C_RIEUL, O_TIEUT, "12항"),
        O_TIEUT: (C_RIEUL, O_TIEUT, "Kyubyong/g2pK"),
        O_SSANGDIGEUT: (C_RIEUL, O_SSANGDIGEUT, "Kyubyong/g2pK"),
        O_MIEUM: (C_RIEUL, O_MIEUM, "Kyubyong/g2pK"),
        O_BIEUP: (C_RIEUL, O_BIEUP, "Kyubyong/g2pK"),
        O_PIEUP: (C_RIEUL, O_PIEUP, "Kyubyong/g2pK"),
        O_SSANGBIEUP: (C_RIEUL, O_SSANGBIEUP, "Kyubyong/g2pK"),
        O_SIOT: (C_RIEUL, O_SSANGSIOT, "12항"),
        O_SSANGSIOT: (C_RIEUL, O_SSANGSIOT, "Kyubyong/g2pK"),
        O_JIEUT: (C_RIEUL, O_CHIEUT, "12항"),
        O_CHIEUT: (C_RIEUL, O_CHIEUT, "Kyubyong/g2pK"),
        O_SSANGJIEUT: (C_RIEUL, O_SSANGJIEUT, "Kyubyong/g2pK"),
        O_HIEUT: (C_RIEUL, O_HIEUT, "10항"),
        O_RIEUL: (C_RIEUL, O_RIEUL, "Kyubyong/g2pK"),
        O_EOW: (C_RIEUL, O_EOW, "Kyubyong/g2pK"),                   # g2pK 원본 정규식("ᆯ") 수정. 문장 부호(\W)나 어말($)이 증발하는 오류를 막기 위해 O_EOW를 명시적으로 보존.
    },
}

def apply_phonology_lut(
    tokens: List[MorphToken],
    cross_word_boundary: bool = False,
) -> List[MorphToken]:
    """
    2D LUT(PHONOLOGY_LUT)를 기반으로 O(1) 복잡도의 인접 종성-초성 간 음운 변동을 수행합니다.

    본 엔진의 핵심인 LUT 아키텍처는 박규병 님의 `g2pK` 및 Lucas Jo, et al.의 `zeroth` 프로젝트에서
    증명된 "연쇄 동화의 단일화" 철학을 계승합니다. 정규식 기반 엔진에서는 제19항(ㄹ의 비음화)을 선행하고
    제18항(역행 비음화)을 후행하는 등 규칙 간의 엄격한 순서 제어가 필수적이었습니다.
    (예: "법리" -> 19항 적용 [법니] -> 18항 적용 [범니]).

    본 엔진은 이러한 다단계 변동의 최종 종착지를 2차원 배열의 단일 노드로 사전 계산하여 압축했습니다.
    이를 통해 파이프라인의 순서 의존성을 제거하고, 단 한 번의 참조만으로 결과를 도출하는
    O(1) 복잡도를 지향합니다.

    `cross_word_boundary` 파라미터가 `False`일 때는 공백을 경계로 음운 변동을 차단하여 보수적으로 적용하며,
    `True`일 때는 띄어쓰기를 무시하고 원칙에 맞게 일괄 적용합니다.

    국어국문학적 원칙이나 빠른 구어체에서는 단어 사이에도 연음 및 동화가 발생하는 것이 표준발음법에 맞습니다.
    (예: "옷 안" -> [오단]). g2pK 원작자 역시 공백 유무와 무관하게 음운 변동을 적용하도록 구현한 바 있습니다.

    하지만 음성 합성이나 음성 인식 과제에서는 띄어쓰기(공백)가 곧 짧은 휴지(pause)를 의미하는 경우가 많습니다.
    이 경우 단어 간 변동을 막아 개별 발음을 또렷하게 유지하는 것(예: "옷 안" -> [옫 안])이 더 적합한
    텍스트 전처리일 수 있으므로 본 엔진은 기본값을 `False`로 설정합니다. 타겟 도메인과 사용하시는
    텍스트의 특성을 종합적으로 고려하여 해당 파라미터를 설정하시기 바랍니다.

    Ref:
        g2pk.utils.parse_table()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/utils.py#L136-L159
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L246-L820

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.
        cross_word_boundary (bool): 띄어쓰기(공백)를 넘어 단어 간 음운 변동을 적용할지 여부. (기본값: False)

    Returns:
        List[MorphToken]: 인접한 종성과 초성 간의 동화, 탈락, 경음화 등 음운 변동 규칙이 적용된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]

        if curr_token.pos == "SP":
            continue

        # 1. 단일 토큰 내부의 음운 변동 처리
        # 형태소 분석기가 쪼개지 않은 복합어나 미분석어 내부의 음절 경계에서 변동을 수행합니다.
        if len(curr_token.jamo_str) >= 6:  # 2음절(6자모) 이상인 경우에만 내부 경계 존재
            jamo_list = list(curr_token.jamo_str)
            # 초-중-종(3단위)씩 이동하며 현재 음절 종성과 다음 음절 초성 비교
            for j in range(0, len(jamo_list) - 3, 3):
                intra_jong = jamo_list[j + 2]
                intra_cho = jamo_list[j + 3]

                if intra_jong == C_NONE:
                    continue

                rule_info = PHONOLOGY_LUT.get(intra_jong, {}).get(intra_cho)
                if rule_info:
                    new_jong, new_cho, _ = rule_info
                    jamo_list[j + 2] = new_jong
                    jamo_list[j + 3] = new_cho
            
            curr_token.jamo_str = "".join(jamo_list)

        # 2. 인접 토큰 간의 음운 변동 처리 (Inter-token)
        curr_jong = curr_token.jamo_str[-1]

        # 종성이 없으면(C_NONE) 충돌할 일도 없으니 패스
        if curr_jong == C_NONE:
            continue

        # 2-1. 다음 토큰의 인덱스 및 초성 탐색
        next_idx = i + 1

        if next_idx < len(tokens) and tokens[next_idx].pos == "SP":
            if not cross_word_boundary:
                # 공백 경계를 넘지 않도록 설정된 경우, 어말(EOW)로 처리
                next_cho = O_EOW
            else:
                # 공백을 건너뛰어 다음 형태소 탐색
                next_idx += 1
                if next_idx >= len(tokens):
                    next_cho = O_EOW
                else:
                    next_cho = tokens[next_idx].jamo_str[0]
        elif next_idx >= len(tokens):
            # 토큰 배열의 끝에 도달한 경우 어말(EOW)로 처리
            next_cho = O_EOW
        else:
            # 공백 없이 인접한 토큰인 경우
            next_cho = tokens[next_idx].jamo_str[0]

        # 2-2. 2D LUT 매트릭스 조회 및 적용
        rule_info = PHONOLOGY_LUT.get(curr_jong, {}).get(next_cho)

        if rule_info:
            new_jong, new_cho, rule_id = rule_info

            # 선행 토큰의 종성 업데이트
            curr_token.jamo_str = curr_token.jamo_str[:-1] + new_jong

            # 후행 토큰의 초성 업데이트 (어말 O_EOW 상태가 아닐 때만 적용)
            if next_cho != O_EOW and new_cho != O_EOW:
                next_token = tokens[next_idx]
                next_token.jamo_str = new_cho + next_token.jamo_str[1:]

    return tokens
