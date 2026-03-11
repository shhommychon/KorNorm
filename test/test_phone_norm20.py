import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology, apply_stdict_pronunciation
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter2 import norm5_p2
from kornorm.phonology.chapter4 import norm13, norm14
from kornorm.phonology.chapter5 import norm20_p
from kornorm.phonology.chapter6 import norm26
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm20(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """테스트 전체에서 한 번만 사전(Arrow)과 토크나이저를 로드합니다."""
        cls.processor = PhonologicProcessor()
        cls.g2pk = G2p()

    def _strip_punctuation(self, text: str) -> str:
        """
        형태소 분석 오류(IndexError) 방지를 위해 입력 문자열에서 특정 구두점을 제거합니다.

        Args:
            text (str): 원본 입력 문자열

        Returns:
            str: 마침표(.)와 쉼표(,)가 제거된 문자열
        """
        return text.replace('.', '').replace(',', '').replace('?', '')

    def _tokens_to_hangul(self, tokens) -> str:
        """
        MorphToken 객체 리스트를 조합하여 완성형 한글 문자열로 변환합니다.

        Args:
            tokens (list): 변환할 MorphToken 객체 리스트

        Returns:
            str: 조합된 완성형 한글 문자열
        """
        result = []
        for t in tokens:
            if t.pos == "SP":
                result.append(' ')
                continue
            jamo = t.jamo_str
            for i in range(0, len(jamo), 3):
                result.append(join_jamos(jamo[i], jamo[i+1], jamo[i+2]))
        return ''.join(result)

    def _align_marker(self, text_line: str, marker_line: str) -> str:
        """
        한글(2칸)과 영문/기호(1칸)의 터미널 출력 폭을 계산하여 difflib의 마커 라인을 정렬합니다.

        Args:
            text_line (str): difflib에서 생성된 텍스트 라인
            marker_line (str): difflib에서 생성된 마커 라인 ("? "로 시작)

        Returns:
            str: 출력 폭이 보정된 마커 문자열
        """
        aligned_marker = "? "
        text_content = text_line[2:]     # "- " 또는 "+ " 제거
        marker_content = marker_line[2:] # "? " 제거

        for i, char in enumerate(text_content):
            # difflib이 생성한 마커 문자(공백, ^, -, +) 확인
            m_char = marker_content[i] if i < len(marker_content) else ' '

            # 문자의 화면 표시 폭 계산 (한글 등 넓은 문자는 2, 나머지는 1)
            width = 2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1

            if m_char != ' ':
                aligned_marker += m_char * width # 불일치 마커(^) 폭 보정
            else:
                aligned_marker += ' ' * width    # 일치 부분 공백 폭 보정

        return aligned_marker

    def _get_smart_diff(self, expected: str, actual: str) -> str:
        """
        터미널 출력 폭이 보정된 diff 문자열을 생성합니다.

        Args:
            expected (str): 예상 결과 문자열
            actual (str): 실제 결과 문자열

        Returns:
            str: 포맷팅이 완료된 diff 문자열
        """
        # 단일 문자열을 리스트로 전달하여 라인 단위가 아닌 문자 단위 diff 수행
        raw_diff = list(difflib.ndiff([actual], [expected]))
        output = []

        i = 0
        while i < len(raw_diff):
            line = raw_diff[i].rstrip('\n')

            # 다음 줄이 마커 라인("? ")인지 확인
            if i + 1 < len(raw_diff) and raw_diff[i+1].startswith('?'):
                marker_line = raw_diff[i+1].rstrip('\n')
                # 폭이 보정된 마커로 교체
                aligned_marker = self._align_marker(line, marker_line)
                output.extend([line, aligned_marker])
                i += 2 # 원본 마커 라인 건너뛰기
            else:
                output.append(line)
                i += 1

        return '\n'.join(output)

    def assert_kor_equal(self, expected: str, actual: str, log_only: bool = False):
        """
        기대 변환 결과와 엔진의 실제 변환 결과를 비교하여 차이점을 분석합니다.

        한국어 특성을 고려하여 음절 단위의 차이를 시각화한 diff를 생성하고,
        검증 모드(log_only)에 따라 단순히 로그로 출력하거나 AssertionError를 발생시킵니다.

        Args:
            expected (str): 예상 결과 문자열
            actual (str): 실제 결과 문자열
            log_only (bool): True일 경우 예외를 발생시키지 않고 diff 로그만 출력합니다.

        Raises:
            AssertionError: log_only가 False이고 두 문자열이 일치하지 않을 때 발생합니다.
        """
        if expected == actual:
            return

        diff_str = self._get_smart_diff(expected, actual)

        if log_only:
            print('\n' + '-' * 70)
            print(f"[{self._testMethodName}] [DIFF_LOG] 비교 대상 불일치")
            print(diff_str)
            print('-' * 70)
        else:
            error_msg = f"비교 대상 불일치\n{diff_str}"
            raise AssertionError(error_msg)

    def _word_pipeline(self, word: str) -> str:
        """
        단어 검증용 축약 파이프라인: 엔진 순서(사전 발음 선적용 -> norm20_p -> norm26 -> norm5_p2 -> LUT -> norm13 -> norm14)를 재현합니다.

        Args:
            word (str): 변환할 단어.

        Returns:
            str: 완성형 한글로 조합된 변환 결과.
        """
        tokens = self.processor._tokenize_and_tag(word)

        tokens = apply_stdict_pronunciation(tokens)
        tokens = norm20_p(tokens)
        tokens = norm26(tokens)
        tokens = norm5_p2(tokens)
        res_tokens = apply_phonology_lut(tokens)
        res_tokens = norm13(res_tokens)
        res_tokens = norm14(res_tokens)
        return self._tokens_to_hangul(res_tokens)

    # ================================================================================
    # 제20항 ㄴ은 ㄹ의 앞이나 뒤에서 [ㄹ]로 발음 (유음화)
    # ================================================================================
    def test_norm20_words(self):
        """개별 단어 검증: 제20항 본항 (유음화)"""
        cases = {
            "난로": "날로",
            "신라": "실라",
            "천리": "철리",
            "광한루": "광할루",
            "대관령": "대괄령",
            "칼날": "칼랄",
            "물난리": "물랄리",
            "줄넘기": "줄럼끼",
            "할는지": "할른지",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm20_sentences(self):
        """통합 엔진 검증: 제20항 본항 포함 문장"""
        sentence = self._strip_punctuation("난로 옆에서 신라 지도를 보던 아이는 천리 길을 달려 광한루에 도착한 뒤, 대관령 칼날 바람을 맞으며 물난리 소식에 줄넘기를 멈췄다.")
        expected = "날로 여페서 실라 지도를 보던 아이는 철리 기를 달려 광할루에 도차칸 뒤 대괄령 칼랄 바라믈 마즈며 물랄리 소시게 줄럼끼를 멈춷따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제20항 붙임 첫소리 ㄴ이 ㄶ, ㅀ 뒤에 연결되는 경우에도 이에 준함
    # ================================================================================
    def test_norm20_addendum_words(self):
        """개별 단어 검증: 제20항 붙임 (ㄶ, ㅀ 뒤 ㄴ의 유음화)"""
        cases = {
            "앓는": "알른",
            "뚫는": "뚤른",
            "핥네": "할레",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm20_addendum_sentences(self):
        """통합 엔진 검증: 제20항 붙임 포함 문장"""
        sentence = self._strip_punctuation("몸살을 앓는 사람이 구멍을 뚫는 동안 아이는 엿을 핥네 마네 투정을 부렸다.")
        expected = "몸사를 알른 사라미 구멍을 뚤른 동안 아이는 여슬 할레 마네 투정을 부렫따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제20항 다만 다음과 같은 단어들은 ㄹ을 [ㄴ]으로 발음
    #        (2음절 한자어 + ㄹ계 한자 접미 결합 -> stdict 한자어 판별 휴리스틱)
    # ================================================================================
    def test_norm20_proviso_words(self):
        """개별 단어 검증: 제20항 다만 (한자어 유음화 예외)"""
        cases = {
            "의견란": "의견난",
            "임진란": "임진난",
            "생산량": "생산냥",
            "결단력": "결딴녁",
            "공권력": "공꿘녁",
            "동원령": "동원녕",
            "상견례": "상견녜",
            "횡단로": "횡단노",
            "이원론": "이원논",
            "입원료": "이붠뇨",
            "구근류": "구근뉴",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm20_proviso_sentences(self):
        """통합 엔진 검증: 제20항 다만 포함 문장"""
        sentence = self._strip_punctuation("의견란에 실린 생산량 통계를 본 대표는 결단력 있게 횡단로 정비와 구근류 수출을 마무리했다.")
        expected = "의견나네 실린 생산냥 통게를 본 대표는 결딴녁 읻께 횡단노 정비와 구근뉴 수추를 마무리핻따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
