import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology, apply_stdict_pronunciation
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter2 import norm5_p2
from kornorm.phonology.chapter4 import norm10_p, norm13, norm14
from kornorm.phonology.chapter5 import norm20_p
from kornorm.phonology.chapter6 import norm24, norm25, norm26, norm27, norm27_a
from kornorm.phonology.chapter7 import norm29
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm29(unittest.TestCase):
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
        단어 검증용 축약 파이프라인: 엔진 순서(사전 발음 선적용 -> norm20_p -> norm26 -> norm29 -> norm5_p2 -> norm10_p -> norm24 -> norm25 -> norm27 -> norm27_a -> LUT -> norm13 -> norm14)를 재현합니다.

        Args:
            word (str): 변환할 단어.

        Returns:
            str: 완성형 한글로 조합된 변환 결과.
        """
        tokens = self.processor._tokenize_and_tag(word)

        tokens = apply_stdict_pronunciation(tokens)
        tokens = norm20_p(tokens)
        tokens = norm26(tokens)
        tokens = norm29(tokens)
        tokens = norm5_p2(tokens)
        tokens = norm10_p(tokens)
        tokens = norm24(tokens)
        tokens = norm25(tokens)
        tokens = norm27(tokens, ignore_space_as_pause=True)
        tokens = norm27_a(tokens)
        res_tokens = apply_phonology_lut(tokens)
        res_tokens = norm13(res_tokens)
        res_tokens = norm14(res_tokens)
        return self._tokens_to_hangul(res_tokens)

    # ================================================================================
    # 제29항 합성어 및 파생어에서, 앞 단어나 접두사의 끝이 자음이고 뒤 단어나 접미사의
    #        첫음절이 이, 야, 여, 요, 유인 경우에는 ㄴ 음을 첨가하여 [니, 냐, 녀, 뇨, 뉴]로 발음
    # ================================================================================
    def test_norm29_words(self):
        """개별 단어 검증: 제29항 본항 (합성어·파생어의 ㄴ 첨가)"""
        cases = {
            "솜이불": "솜니불",
            "홑이불": "혼니불",
            "막일": "망닐",
            "삯일": "상닐",
            "맨입": "맨닙",
            "꽃잎": "꼰닙",
            "내복약": "내봉냑",
            "한여름": "한녀름",
            "남존여비": "남존녀비",
            "신여성": "신녀성",
            "색연필": "생년필",
            "직행열차": "지캥녈차",
            "늑막염": "능망념",
            "콩엿": "콩녇",
            "담요": "담뇨",
            "눈요기": "눈뇨기",
            "영업용": "영엄뇽",
            "식용유": "시굥뉴",
            "백분율": "백뿐뉼",
            "밤윷": "밤뉻",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm29_sentences(self):
        """통합 엔진 검증: 제29항 본항 포함 문장"""
        sentence = self._strip_punctuation("한여름 밤 색연필로 그림을 그리던 아이는 솜이불 위에서 콩엿을 먹으며 담요를 덮었다.")
        expected = "한녀름 밤 생년필로 그리믈 그리던 아이는 솜니불 위에서 콩녀슬 머그며 담뇨를 더펃따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제29항 다만 다음 말들은 ㄴ 음을 첨가하여 발음하되, 표기대로 발음할 수 있다
    #        (본 엔진은 사전의 첫 번째 발음인 ㄴ 첨가형을 채택)
    # ================================================================================
    def test_norm29_proviso_words(self):
        """개별 단어 검증: 제29항 다만 1 (ㄴ 첨가형과 표기형이 모두 허용되는 단어)"""
        cases = {
            "이죽이죽": "이중니죽",
            "야금야금": "야금냐금",
            "검열": "검녈",
            "욜랑욜랑": "욜랑뇰랑",
            "금융": "금늉",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm29_proviso_sentences(self):
        """통합 엔진 검증: 제29항 다만 1 포함 문장"""
        sentence = self._strip_punctuation("야금야금 저축한 덕에 금융 시험과 검열을 통과했다.")
        expected = "야금냐금 저추칸 더게 금늉 시험과 검녀를 통과핻따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제29항 다만 다음과 같은 단어에서는 ㄴ(ㄹ) 음을 첨가하여 발음하지 않는다
    #        (사전 발음이 표기와 동일한 단어는 표기대로 발음 -- 6·25, 3·1절은 alphanumeric 소관)
    # ================================================================================
    def test_norm29_proviso2_words(self):
        """개별 단어 검증: 제29항 다만 2 (ㄴ(ㄹ) 첨가 없이 발음하는 단어)"""
        cases = {
            "송별연": "송벼련",
            "등용문": "등용문",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm29_proviso2_sentences(self):
        """통합 엔진 검증: 제29항 다만 2 포함 문장"""
        sentence = self._strip_punctuation("등용문을 지난 사람들이 송별연에 모였다.")
        expected = "등용무늘 지난 사람드리 송벼려네 모엳따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제29항 붙임 1 ㄹ 받침 뒤에 첨가되는 ㄴ 음은 [ㄹ]로 발음
    # ================================================================================
    def test_norm29_addendum1_words(self):
        """개별 단어 검증: 제29항 붙임 1 (ㄹ 받침 뒤 ㄴ 첨가의 유음화)"""
        cases = {
            "들일": "들릴",
            "솔잎": "솔립",
            "설익다": "설릭따",
            "물약": "물략",
            "불여우": "불려우",
            "서울역": "서울력",
            "물엿": "물렫",
            "휘발유": "휘발류",
            "유들유들": "유들류들",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm29_addendum1_sentences(self):
        """통합 엔진 검증: 제29항 붙임 1 포함 문장"""
        sentence = self._strip_punctuation("물약을 먹은 불여우가 솔잎 사이로 사라지자 휘발유 냄새가 났다.")
        expected = "물랴글 머근 불려우가 솔립 사이로 사라지자 휘발류 냄새가 낟따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제29항 붙임 2 두 단어를 이어서 한 마디로 발음하는 경우에는 이에 준한다
    #        (공백을 넘는 ㄴ(ㄹ) 첨가는 어절 결속도 판단이 필요 -- 통합 단계 인수 기준)
    # ================================================================================
    def test_norm29_addendum2_words(self):
        """개별 단어 검증: 제29항 붙임 2 (두 단어를 한 마디로 발음하는 ㄴ(ㄹ) 첨가)"""
        cases = {
            "서른여섯": "서른녀섣",
            "스물여섯": "스물려섣",
            "한 일": "한 닐",
            "옷 입다": "온 닙따",
            "먹은 엿": "머근 녇",
            "할 일": "할 릴",
            "잘 입다": "잘 립따",
            "먹을 엿": "머글 렫",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = apply_phonology(word, output_format="hangul")

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm29_addendum2_sentences(self):
        """통합 엔진 검증: 제29항 붙임 2 포함 문장"""
        sentence = self._strip_punctuation("할 일을 마친 그는 옷 입다 말고 먹을 엿을 찾았다.")
        expected = "할 리를 마친 그는 온 닙따 말고 머글 려슬 차잗따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
