# [KorNorm 음운 변동 엔진 모듈]
#
# 정규식을 지양하고 O(1) 탐색 속도의 Arrow 사전과 2D LUT를 활용하는 하이브리드 음운 변동 엔진입니다.

import os
from dataclasses import dataclass
from typing import List, Literal

from kornorm.utils._patch_pecab import patch_pecab_dictionary_if_needed
from kornorm.utils.jamo import decompose, join_jamos, to_compat_jamo

from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter2 import (
    norm5_p1, norm5_p2, norm5_p3, norm5_p4_1, norm5_p4_2,
)
from kornorm.phonology.chapter4 import (
    norm10_p, norm11_p, norm12_4, norm13, norm14, norm15, norm15_p, norm16,
)
from kornorm.phonology.chapter5 import (
    norm17, norm17_a, norm20_p, norm22, norm22_a,
)
from kornorm.phonology.chapter6 import (
    norm24, norm25, norm26, norm27, norm27_a,
)
from kornorm.phonology.chapter7 import (
    norm29, norm30,
)

global_phonology_engine = None

def worker_init():
    global global_phonology_engine
    if global_phonology_engine is None:
        global_phonology_engine = PhonologicProcessor()

def apply_phonology(text: str, output_format: str = "positional") -> str:
    global global_phonology_engine
    if global_phonology_engine is None:
        global_phonology_engine = PhonologicProcessor()
    return global_phonology_engine(text, output_format=output_format)


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


class PhonologicProcessor:
    """
    KorNorm 메인 음운 변동 엔진

    본 프로세서는 한국어 음운 변동의 표준 모델을 지향하며, 국내 자연어 처리 분야의 준거 모델인
    g2pK 아키텍처 및 그 근간인 zeroth 프로젝트의 설계 철학을 계승하여 재구현되었습니다.

    만약 본 클래스의 정책을 변경하여 국립국어원의 다른 허용 조항이나 연음을 켜고 싶다면,
    본 클래스를 상속받아 `__call__` 파이프라인의 파라미터를 직접 오버라이딩하십시오.
    """

    def __init__(self):
        patch_pecab_dictionary_if_needed()

        import pecab
        self.tokenizer = pecab.PeCab()

        self.hanja_set = set()
        self.compound_set = set()

        self._load_stdict_arrow()
        self._load_2d_lut()

    def _load_stdict_arrow(self):
        """
        Arrow IPC를 로드하여 DoubleArrayTrie 구조로 복원합니다.

        PyArrow의 Native 리스트 변환(to_pylist)을 사용하여 Zero-copy에 가까운 빠른 메모리 로딩을 수행합니다.
        """
        import pyarrow as pa
        from pecab._datrie import DoubleArrayTrie

        words_path = os.path.join(os.path.dirname(__file__), "_resources", "stdict_words.arrow")
        arrays_path = os.path.join(os.path.dirname(__file__), "_resources", "stdict_arrays.arrow")

        if os.path.exists(words_path) and os.path.exists(arrays_path):
            with pa.memory_map(words_path, 'r') as source_w, pa.memory_map(arrays_path, 'r') as source_a:
                words_table = pa.ipc.open_file(source_w).read_all()
                arrays_table = pa.ipc.open_file(source_a).read_all()

                # DoubleArrayTrie 객체 복원
                self.stdict_trie = DoubleArrayTrie({})

                # RecordBatch를 Python dict list로 직행 (Zero-overhead 접근)
                self.stdict_trie._value = words_table.to_pylist()

                self.stdict_trie._base = arrays_table["base"].to_pylist()
                self.stdict_trie._check = arrays_table["check"].to_pylist()

    def _load_2d_lut(self):
        """2D LUT를 메모리에 바인딩합니다."""
        from kornorm.phonology.apply_lut import PHONOLOGY_LUT
        self.lut = PHONOLOGY_LUT

    def _tokenize_and_tag(self, text: str) -> List[MorphToken]:
        """
        Pecab의 내부 API를 호출하여 토큰을 생성하고,
        표준국어대사전(stdict_trie)을 조회하여 한자어 여부 및 복합어 결합 구조를 주입합니다.
        """
        raw_output = self.tokenizer._tokenize(text)

        tokens = []
        for term, pos, offset in zip(
            raw_output["terms"],
            raw_output["pos_tags"],
            raw_output["offsets"]
        ):
            is_h = False
            comp_str = ''

            # 사전 조회를 통한 메타데이터 확보
            if self.stdict_trie is not None and term in self.stdict_trie:
                dict_info = self.stdict_trie[term]
                is_h = (dict_info.get("is_hanja") == '1')
                comp_str = dict_info.get("compound_structure", "")

            token = MorphToken(
                surface=term,
                pos=pos,
                start_offset=offset[0],
                end_offset=offset[1],
                jamo_str=decompose(term),
                is_hanja=is_h,
                compound_structure=comp_str,
            )
            tokens.append(token)

        return tokens

    def __call__(
        self,
        text: str,
        output_format: Literal["positional", "compat", "hangul"] = "positional"
    ) -> str:
        """
        텍스트를 입력받아 표준발음법이 적용된 결과를 반환합니다.

        Args:
            text (str): 전처리가 완료된 원본 텍스트
            output_format (str):
                - "positional": (기본값) U+11xx 형태의 위치 기반 자모 분리 상태 (예: ᄆ​ᅥ​ᆨ)
                - "compat": U+313x 형태의 호환 자모 분리 상태 (예: ㅁ​ㅓ​ㄱ)
                - "hangul": 초중종성이 결합된 완성형 한글 (예: 먹)
        """
        tokens = self._tokenize_and_tag(text)

        # 1. 한자어 처리
        tokens = norm20_p(tokens)
        tokens = norm26(tokens)

        # 2. 복합어/파생어 처리
        tokens = norm30(tokens, keep_saisiot=False) # 사이시옷의 발음(ㄷ)을 탈락시키고 뒤 자음의 변동만 취합
        tokens = norm29(tokens)

        # 3. 종성 규칙 선적용
        tokens = norm15(tokens)
        tokens = norm15_p(tokens)

        # 4. 표준 발음 규칙 적용
        tokens = norm5_p1(tokens)
        tokens = norm5_p2(tokens)
        tokens = norm5_p3(tokens)
        tokens = norm5_p4_1(tokens)
        tokens = norm5_p4_2(tokens)
        tokens = norm22(tokens)
        tokens = norm22_a(tokens)

        tokens = norm10_p(tokens)
        tokens = norm11_p(tokens)
        tokens = norm16(tokens)

        tokens = norm24(tokens)
        tokens = norm25(tokens)
        tokens = norm27(tokens, ignore_space_as_pause=True) # 띄어쓰기에도 강건하게 변동 적용
        tokens = norm27_a(tokens)

        tokens = norm17(tokens)
        tokens = norm17_a(tokens)

        # 5. 메인 O(1) 2D LUT 적용 (일반 자음 동화, 비음화, 유음화 등)
        tokens = apply_phonology_lut(tokens, cross_word_boundary=False) # 공백을 경계로 음운 변동을 차단하여 보수적으로 적용

        # 6. 연음 및 탈락 적용
        tokens = norm13(tokens)
        tokens = norm14(tokens)
        tokens = norm12_4(tokens)

        # 출력 포맷팅
        result_chars = []
        for token in tokens:
            if token.pos == "SP":
                result_chars.append(token.surface)
            else:
                if output_format == "positional":
                    # C_NONE과 같은 플레이스홀더를 제거하여 순수 자모만 리턴
                    result_chars.append(token.jamo_str.replace('\u3164', ''))
                elif output_format == "compat":
                    result_chars.append(to_compat_jamo(token.jamo_str))
                elif output_format == "hangul":
                    jamo_len = len(token.jamo_str)
                    for i in range(0, jamo_len, 3):
                        cho = token.jamo_str[i]
                        joong = token.jamo_str[i+1]
                        jong = token.jamo_str[i+2]
                        result_chars.append(join_jamos(cho, joong, jong))
                else:
                    raise ValueError("output_format must be \"positional\", \"compat\", or \"hangul\"")

        return ''.join(result_chars)
