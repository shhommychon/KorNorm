import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology
from kornorm.phonology.chapter2 import (
    norm5_p1, norm5_p2, norm5_p3, norm5_p4_1, norm5_p4_2
)
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm5(unittest.TestCase):
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

    # ============================================================
    # 제5항 다만 1 (져, 쪄, 쳐 -> 저, 쩌, 처)
    # ============================================================
    def test_norm5_p1_words(self):
        """개별 단어 검증: 용언의 활용형 져, 쪄, 쳐"""
        cases = {
            "가져": "가저",
            '쪄': '쩌',
            "다쳐": "다처",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                res_tokens = norm5_p1(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

        

    def test_norm5_p1_sentence(self):
        """통합 엔진 검증: 제5항 다만 1 케이스 포함 문장"""
        sentence = self._strip_punctuation("짐을 가져가다가 넘어지는 바람에 다리를 다쳐서, 결국 집에서 감자를 쪄 먹었다.")
        expected = "지믈 가저가다가 너머지는 바라메 다리를 다처서 결국 지베서 감자를 쩌 머걷따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)
        
        self.assert_kor_equal(expected, actual, log_only=False)

    # ============================================================
    # 제5항 다만 2 (예, 례 이외의 ㅖ -> ㅔ)
    # ============================================================
    def test_norm5_p2_words(self):
        """개별 단어 검증: 예, 례 이외의 ㅖ (단, 녜/셰/쎼 제외)"""
        cases = {
            "계집": "게집",
            "계시다": "게시다",
            "시계": "시게",
            "연계": "연게",
            "몌별": "메별",
            "개폐": "개페",
            "혜택": "헤택",
            "지혜": "지헤",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                res_tokens = norm5_p2(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm5_p2_sentence(self):
        """통합 엔진 검증: 제5항 다만 2 케이스 포함 문장"""
        sentence = self._strip_punctuation("오랜 몌별의 아픔을 간직하고 계시다는 할머니께, 한 계집아이가 지혜를 발휘해 출입문 개폐와 연계된 스마트 시계를 선물하며 큰 혜택을 드렸다.")
        # 참고: '몌별의', '계집아이가', '개폐와', '연계된', '시계를', '혜택을' 에서 'ㅖ'가 'ㅔ'로 변하고,
        # 이외의 연음(13항)과 '의' 발음(5항 다만 4) 등이 모두 적용된 최종 발음을 예상합니다.
        expected = "오랜 메벼레 아프믈 간지카고 게시다는 할머니께 한 게지바이가 지헤를 발휘해 추림문 개페와 연게된 스마트 시게를 선물하며 큰 헤태글 드렫따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)
        
        self.assert_kor_equal(expected, actual, log_only=False)

    # ============================================================
    # 제5항 다만 3 (자음을 첫소리로 가지는 ㅢ -> ㅣ)
    # ============================================================
    def test_norm5_p3_words(self):
        """개별 단어 검증: 자음을 첫소리로 가지는 음절의 ㅢ"""
        cases = {
            "닐리리": "닐리리", # 원형 그대로
            "닁큼": "닝큼",
            "무늬": "무니",
            "띄어쓰기": "띠어쓰기",
            "씌어": "씨어",
            "틔어": "티어",
            "희어": "히어",
            "희떱다": "히떱다",
            "희망": "히망",
            "유희": "유히",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                res_tokens = norm5_p3(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm5_p3_sentence(self):
        """통합 엔진 검증: 제5항 다만 3 케이스 포함 문장"""
        sentence = self._strip_punctuation("희망을 품고 닁큼 달려가 하얗게 희어 빛나는 무늬의 안경을 씌어 주며 희떱다고 장난을 치니, 마음이 확 틔어 마치 닐리리 가락에 맞춰 유희를 즐기듯 올바른 띄어쓰기로 글을 적었다.")
        expected = "히망을 품고 닝큼 달려가 하야케 히어 빈나는 무니의 안경을 씨어 주며 히떱따고 장나늘 치니 마으미 확 티어 마치 닐리리 가라게 마춰 유히를 즐기듣 올바른 띠어쓰기로 그럴 저걷따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)
        
        self.assert_kor_equal(expected, actual, log_only=False)

    # ============================================================
    # 제5항 다만 4-1 (단어의 첫음절 이외의 ㅢ -> ㅣ)
    # ============================================================
    def test_norm5_p4_1_words(self):
        """개별 단어 검증: 첫음절 이외의 ㅢ"""
        cases = {
            "주의": "주이",
            "협의": "협이",
            "우리의": "우리의", # '우리의'의 '의'는 조사가 아니면 이 테스트에선 일단 '이'로 바뀜
            "강의의": "강이의", # 첫음절 외의 '의' -> '이'
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                res_tokens = norm5_p4_1(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm5_p4_1_sentence(self):
        """통합 엔진 검증: 제5항 다만 4-1 케이스 포함 문장"""
        sentence = self._strip_punctuation("이번 강의의 핵심은 사소한 위험도 주의 깊게 살피고 부서 간 긴밀한 협의를 거치는 데 있습니다.")
        expected = "이번 강이에 핵시믄 사소한 위엄도 주이 깁께 살피고 부서 간 긴밀한 혀비를 거치는 데 읻씀니다"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)
        
        self.assert_kor_equal(expected, actual, log_only=False)

    # ============================================================
    # 제5항 다만 4-2 (조사 '의' -> '에')
    # ============================================================
    def test_norm5_p4_2_words(self):
        """개별 단어 검증: 조사 '의'"""
        cases = {
            "우리의": "우리에",
            "강의의": "강의에",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)
                res_tokens = norm5_p4_2(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm5_p4_2_sentence(self):
        """통합 엔진 검증: 제5항 다만 4-2 케이스 포함 문장"""
        sentence = self._strip_punctuation("우리의 최종 목표는 지난번 강의의 핵심 규정을 실무에 완벽하게 적용하는 것입니다.")
        expected = "우리에 최총 목표는 지난번 강이에 핵심 규정을 실무에 완벼카게 저굥하는 거심니다"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)
        
        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
