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
from kornorm.phonology.chapter7 import norm29, norm30
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm30(unittest.TestCase):
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
        단어 검증용 축약 파이프라인: 엔진 순서(사전 발음 선적용 -> norm20_p -> norm26 -> norm30 -> norm29 -> norm5_p2 -> norm10_p -> norm24 -> norm25 -> norm27 -> norm27_a -> LUT -> norm13 -> norm14)를 재현합니다.

        Args:
            word (str): 변환할 단어.

        Returns:
            str: 완성형 한글로 조합된 변환 결과.
        """
        tokens = self.processor._tokenize_and_tag(word)

        tokens = apply_stdict_pronunciation(tokens)
        tokens = norm20_p(tokens)
        tokens = norm26(tokens)
        tokens = norm30(tokens, keep_saisiot=False)
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
    # 제30항 1 ㄱ, ㄷ, ㅂ, ㅅ, ㅈ으로 시작하는 단어 앞에 사이시옷이 올 때는 이들 자음만을
    #          된소리로 발음하는 것을 원칙으로 하되, 사이시옷을 [ㄷ]으로 발음함도 허용
    # ================================================================================
    def test_norm30_1_words(self):
        """개별 단어 검증: 제30항 1 (사이시옷 뒤 경음화)"""
        # 냇가와 깃발은 규범이 병기한 [ㄷ] 허용형(낻까, 긷빨)으로 검증
        cases = {
            "냇가": "낻까",
            "샛길": "새낄",
            "빨랫돌": "빨래똘",
            "콧등": "코뜽",
            "깃발": "긷빨",
            "대팻밥": "대패빱",
            "햇살": "해쌀",
            "뱃속": "배쏙",
            "뱃전": "배쩐",
            "고갯짓": "고개찓",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm30_1_sentences(self):
        """통합 엔진 검증: 제30항 1 포함 문장"""
        sentence = self._strip_punctuation("샛길 냇가에서 햇살을 받으며 깃발을 든 아이가 고갯짓으로 뱃전을 가리켰다.")
        expected = "새낄 내까에서 해싸를 바드며 긷빠를 든 아이가 고개찌스로 배쩌늘 가리켣따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제30항 2 사이시옷 뒤에 ㄴ, ㅁ이 결합되는 경우에는 [ㄴ]으로 발음
    # ================================================================================
    def test_norm30_2_words(self):
        """개별 단어 검증: 제30항 2 (사이시옷의 ㄴ 동화)"""
        cases = {
            "콧날": "콘날",
            "아랫니": "아랜니",
            "툇마루": "퇸마루",
            "뱃머리": "밴머리",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm30_2_sentences(self):
        """통합 엔진 검증: 제30항 2 포함 문장"""
        sentence = self._strip_punctuation("콧날이 오뚝한 아이가 아랫니를 드러내며 툇마루에 앉아 뱃머리를 바라보았다.")
        expected = "콘나리 오뚜칸 아이가 아랜니를 드러내며 퇸마루에 안자 밴머리를 바라보앋따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제30항 3 사이시옷 뒤에 '이' 음이 결합되는 경우에는 [ㄴㄴ]으로 발음
    # ================================================================================
    def test_norm30_3_words(self):
        """개별 단어 검증: 제30항 3 (사이시옷의 ㄴㄴ 첨가)"""
        cases = {
            "베갯잇": "베갠닏",
            "깻잎": "깬닙",
            "나뭇잎": "나문닙",
            "도리깻열": "도리깬녈",
            "뒷윷": "뒨뉻",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                actual = self._word_pipeline(word)

                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm30_3_sentences(self):
        """통합 엔진 검증: 제30항 3 포함 문장"""
        sentence = self._strip_punctuation("나뭇잎과 깻잎을 따던 그는 베갯잇을 갈고 도리깻열을 말렸다.")
        expected = "나문닙꽈 깬니플 따던 그는 베갠니슬 갈고 도리깬녀를 말렫따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)

        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
