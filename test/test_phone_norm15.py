import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter4 import norm13, norm15, norm15_p
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm15(unittest.TestCase):
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

    # ================================================================================
    # 제15항 받침 뒤에 모음 ㅏ, ㅓ, ㅗ, ㅜ, ㅟ로 시작된 실질 형태소 결합
    #        -> 대표음으로 바꾸어서 뒤 음절 첫소리로 연음
    # ================================================================================
    def test_norm15_words(self):
        """개별 단어 검증: 제15항 본항 (실질 형태소 앞 대표음 연음)"""
        cases = {
            "밭 아래": "바 다래",
            "늪 앞": "느 밥",
            "젖어미": "저더미",
            "맛없다": "마덥따",
            "겉옷": "거돋",
            "헛웃음": "허두슴",
            "꽃 위": "꼬 뒤",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                tokens = norm15(tokens)
                res_tokens = apply_phonology_lut(tokens)
                res_tokens = norm13(res_tokens)
                actual = self._tokens_to_hangul(res_tokens)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm15_sentences(self):
        """통합 엔진 검증: 제15항 본항 포함 문장"""
        sentence = self._strip_punctuation("밭 아래 늪 앞을 지나던 젖어미가 맛없다는 소리에 헛웃음을 지으며 겉옷에 붙은 꽃 위 이슬을 털었다.")
        expected = "바 다래 느 바플 지나던 저더미가 마덥따는 소리에 허두스믈 지으며 거도세 부튼 꼬 뒤 이스를 터럳따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제15항 다만 "맛있다", "멋있다" -> [마싣따], [머싣따] 허용
    # ================================================================================
    def test_norm15_proviso_words(self):
        """개별 단어 검증: 제15항 다만 (맛있다/멋있다 허용 발음)"""
        cases = {
            "맛있다": "마싣따",
            "멋있다": "머싣따",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                tokens = norm15(tokens)
                tokens = norm15_p(tokens)
                res_tokens = apply_phonology_lut(tokens)
                res_tokens = norm13(res_tokens)
                actual = self._tokens_to_hangul(res_tokens)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm15_proviso_sentences(self):
        """통합 엔진 검증: 제15항 다만 포함 문장"""
        sentence = self._strip_punctuation("새로 연 식당 음식이 참 맛있다 하니 주인장도 멋있다 생각했다.")
        expected = "새로 연 식땅 음시기 참 마싣따 하니 주인장도 머싣따 생가캗따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제15항 붙임 겹받침의 경우에는 그중 하나만을 옮겨 발음
    # ================================================================================
    def test_norm15_addendum_words(self):
        """개별 단어 검증: 제15항 붙임 (겹받침 하나만 연음)"""
        cases = {
            "넋 없다": "너 겁따",
            "닭 앞에": "다 가페",
            "값어치": "가버치",
            "값있는": "가빈는",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                tokens = norm15(tokens)
                res_tokens = apply_phonology_lut(tokens)
                res_tokens = norm13(res_tokens)
                actual = self._tokens_to_hangul(res_tokens)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm15_addendum_sentences(self):
        """통합 엔진 검증: 제15항 붙임 포함 문장"""
        sentence = self._strip_punctuation("넋 없다 소리를 듣던 그는 닭 앞에 서서 값어치 모르는 값있는 보석을 떠올렸다.")
        expected = "너 겁따 소리를 듣떤 그는 다 가페 서서 가버치 모르는 가빈는 보서글 떠올렫따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
