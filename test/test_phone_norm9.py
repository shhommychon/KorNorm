import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm9(unittest.TestCase):
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
        return text.replace('.', '').replace(',', '')

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

    # ======================================================================
    # 제9항 (어말 또는 자음 앞의 ㄲ, ㅋ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅍ 대표음화)
    # ======================================================================
    def test_norm9_words(self):
        """개별 단어 검증: 제9항 받침 대표음 교체 (어말 및 자음 앞)"""
        cases = {
            "닦다": "닥따",
            "키윽": "키윽",
            "키윽과": "키윽꽈",
            '옷': '옫',
            "웃다": "욷따",
            "있다": "읻따",
            '젖': '젇',
            "빚다": "빋따",
            '꽃': '꼳',
            "쫓다": "쫃따",
            '솥': '솓',
            "뱉다": "밷따",
            '앞': '압',
            "덮다": "덥따"
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                
                res_tokens = apply_phonology_lut(tokens, cross_word_boundary=False)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm9_sentences(self):
        """통합 엔진 검증: 제9항 어말 및 자음 앞 조건 포함 문장"""
        sentence = self._strip_punctuation("마침 앞 로비에서 경계 중이던 신입 형사가 있폼없폼 다 잡으며 시든 꽃 장식과 낡은 솥 뚜껑을 살펴보는 바람에, 결국 진지하게 수첩을 덮다 말고 다들 배를 잡고 웃다가 마시던 커피를 훅 뱉다.")
        expected = "마침 압 로비에서 경게 중이던 시닙 형사가 읻폼업폼 다 자브며 시든 꼳 장식꽈 날근 솓 뚜껑을 살펴보는 바라메 결국 진지하게 수처블 덥따 말고 다들 배를 잡꼬 욷따가 마시던 커피를 훅 밷따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
