import unittest

import difflib
import unicodedata

from g2pk import G2p

from kornorm.phonology.engine import PhonologicProcessor, apply_phonology
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter4 import norm12_1_c, norm12_1_a2, norm12_4
from kornorm.utils.jamo import join_jamos

class TestPhoneNorm12(unittest.TestCase):
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
    # 제12항 1 ㅎ(ㄶ, ㅀ) 뒤에 ㄱ, ㄷ, ㅈ 결합 -> [ㅋ, ㅌ, ㅊ]
    # ================================================================================
    def test_norm12_1_words(self):
        """개별 단어 검증: 제12항 1 본항 (ㅎ 뒤에 ㄱ, ㄷ, ㅈ 결합)"""
        cases = {
            "놓고": "노코",
            "좋던": "조턴",
            "쌓지": "싸치",
            "많고": "만코",
            "않던": "안턴",
            "닳지": "달치",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_1_sentences(self):
        """통합 엔진 검증: 제12항 1 본항 포함 문장"""
        sentence = self._strip_punctuation("짐을 내려 놓고 좋던 시절을 떠올리며 지식을 쌓지 않으면, 결국 남는 것이 많고 적음을 떠나 아무것도 않던 것과 같아 마음만 닳지 않겠는가.")
        expected = "지믈 내려 노코 조턴 시저를 떠올리며 지시글 싸치 아느면 결국 남는 거시 만코 저그믈 떠나 아무걷또 안턴 것꽈 가타 마음만 달치 안켄는가"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)
    
    # ================================================================================
    # 제12항 1 해설 "ㅎ(ㄶ, ㅀ)" 뒤에 한자어 "-증(症)" 결합 -> [ㅉ]
    # ================================================================================
    def test_norm12_1_commentary_words(self):
        """개별 단어 검증: 제12항 1 해설 ("-증(症)" 예외 처리)"""
        cases = {
            "싫증": "실쯩",
            # "귀찮증": "귀찬쯩",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                tokens = norm12_1_c(tokens)
                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_1_commentary_sentences(self):
        """통합 엔진 검증: 제12항 1 해설 포함 문장"""
        sentence = self._strip_punctuation("건조증에 손에 염증이 나는게 아주 그냥 싫증이 난다.")
        expected = "건조쯩에 소네 염쯩이 나는게 아주 그냥 실쯩이 난다"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 1 붙임 1 ㄱ(ㄺ), ㄷ, ㅂ(ㄼ), ㅈ(ㄵ) 뒤에 'ㅎ' 결합 -> [ㅋ, ㅌ, ㅍ, ㅊ]
    # ================================================================================
    def test_norm12_1_addendum1_words(self):
        """개별 단어 검증: 제12항 1 붙임 1 (자음 뒤 ㅎ 결합)"""
        cases = {
            "각하": "가카",
            "먹히다": "머키다",
            "밝히다": "발키다",
            "맏형": "마텽",
            "좁히다": "조피다",
            "넓히다": "널피다",
            "꽂히다": "꼬치다",
            "앉히다": "안치다",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_1_addendum1_sentences(self):
        """통합 엔진 검증: 제12항 1 붙임 1 포함 문장"""
        sentence = self._strip_punctuation("대통령 각하께서 어둠을 밝히다 말고 맏형에게 자리를 좁히다 핀잔을 듣고는, 결국 시야를 넓히다 소파에 푹 꽂히다시피 앉히다.")
        expected = "대통녕 가카께서 어두믈 발키다 말고 마텽에게 자리를 조피다 핀자늘 듣꼬는 결국 시야를 널피다 소파에 푹 꼬치다시피 안치다"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 1 붙임 2 ㅅ, ㅈ, ㅊ, ㅌ 뒤에 'ㅎ' 결합 -> [ㅌ]
    # ================================================================================
    def test_norm12_1_addendum2_words(self):
        """개별 단어 검증: 제12항 1 붙임 2 (ㅅ, ㅈ, ㅊ, ㅌ 뒤 ㅎ 결합)"""
        cases = {
            "옷 한 벌": "오 탄 벌",
            "낮 한때": "나 탄때",
            "꽃 한 송이": "꼬 탄 송이",
            "숱하다": "수타다",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                tokens = norm12_1_a2(tokens)
                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_1_addendum2_sentences(self):
        """통합 엔진 검증: 제12항 1 붙임 2 포함 문장"""
        sentence = self._strip_punctuation("옷 한 벌 사기 위해 낮 한때 거리를 헤매다 꽃 한 송이 못 샀지만, 그 숱하다는 사람들 사이에서 따뜻하다 못해 훈훈한 정을 느꼈다.")
        expected = "오 탄 벌 사기 위해 나 탄때 거리를 헤매다 꼬 탄 송이 몯 삳찌만 그 수타다는 사람들 사이에서 따뜨타다 모태 훈훈한 정을 느껻따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 2 ㅎ(ㄶ, ㅀ) 뒤에 'ㅅ' 결합 -> [ㅆ]
    # ================================================================================
    def test_norm12_2_words(self):
        """개별 단어 검증: 제12항 2 (ㅎ 뒤에 ㅅ 결합)"""
        cases = {
            "닿소": "다쏘",
            "많소": "만쏘",
            "싫소": "실쏘",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_2_sentences(self):
        """통합 엔진 검증: 제12항 2 포함 문장"""
        sentence = self._strip_punctuation("손이 닿소? 아니면 말이 많소? 그것도 아니면 그냥 일하기가 싫소?")
        expected = "소니 다쏘 아니면 마리 만쏘 그걷또 아니면 그냥 일하기가 실쏘"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 3 'ㅎ' 뒤에 'ㄴ' 결합 -> [ㄴ]
    # ================================================================================
    def test_norm12_3_words(self):
        """개별 단어 검증: 제12항 3 본항 (ㅎ 뒤에 ㄴ 결합)"""
        cases = {
            "놓는": "논는",
            "쌓네": "싼네",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_3_sentences(self):
        """통합 엔진 검증: 제12항 3 본항 포함 문장"""
        sentence = self._strip_punctuation("벽돌을 내려 놓는 그의 손길이 거침없이 담장을 쌓네.")
        expected = "벽또를 내려 논는 그의 손끼리 거치멉씨 담장을 싼네"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 3 붙임 ㄶ, ㅀ 뒤에 'ㄴ' 결합 -> [ㄴ] (ㅎ 탈락)
    # ================================================================================
    def test_norm12_3_addendum_words(self):
        """개별 단어 검증: 제12항 3 붙임 (ㄶ, ㅀ 뒤 ㄴ 결합)"""
        cases = {
            "않네": "안네",
            "않는": "안는",
            "뚫네": "뚤레",
            "뚫는": "뚤른",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_3_addendum_sentences(self):
        """통합 엔진 검증: 제12항 3 붙임 포함 문장"""
        sentence = self._strip_punctuation("그는 아무 말도 하지 않네, 그리고 아무 행동도 하지 않는 사람이었다.")
        expected = "그는 아무 말도 하지 안네 그리고 아무 행동도 하지 안는 사라미얻따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

    # ================================================================================
    # 제12항 4 ㅎ(ㄶ, ㅀ) 뒤에 모음 어미/접미사 결합 -> 'ㅎ' 탈락
    # ================================================================================
    def test_norm12_4_words(self):
        """개별 단어 검증: 제12항 4 (모음 어미/접미사 앞 ㅎ 탈락)"""
        cases = {
            "낳은": "나은",
            "놓아": "노아",
            "쌓이다": "싸이다",
            "많아": "마나",
            "않은": "아는",
            "닳아": "다라",
            "싫어도": "시러도",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                tokens = self.processor._tokenize_and_tag(word)

                res_tokens = apply_phonology_lut(tokens)
                res_tokens = norm12_4(res_tokens)
                actual = self._tokens_to_hangul(res_tokens)
                
                g2pk_res = self.g2pk(word)
                self.assert_kor_equal(expected, g2pk_res, log_only=True)

                self.assert_kor_equal(expected, actual, log_only=False)

    def test_norm12_4_sentences(self):
        """통합 엔진 검증: 제12항 4 포함 문장"""
        sentence = self._strip_punctuation("새끼를 낳은 어미 고양이가 쥐를 놓아 주고 담장에 기대어 쌓이다 지쳐 잠들자, 나뭇잎이 많아 햇빛을 막아 주니 아무 일도 않은 채 닳아 버린 발톱을 숨기고 비가 와서 싫어도 참았다.")
        expected = "새끼를 나은 어미 고양이가 쥐를 노아 주고 담장에 기대어 싸이다 지처 잠들자 나무니피 마나 해삐츨 마가 주니 아무 일도 아는 채 다라 버린 발토블 숨기고 비가 와서 시러도 차맏따"
        actual = apply_phonology(sentence, output_format="hangul")
        g2pk_res = self.g2pk(sentence)
        
        self.assert_kor_equal(expected, g2pk_res, log_only=True)

        self.assert_kor_equal(expected, actual, log_only=False)

if __name__ == "__main__":
    unittest.main()
