import re
import unittest
from kornorm.heuristics.eraser import (
    purge_symbols, remove_middle_symbols, strip_punctuation, collapse_whitespace
)

class TestEraser(unittest.TestCase):
    def test_purge_symbols(self):
        """텍스트 전역에서 대상 문자열을 모두 제거하는지 테스트"""
        text = "뚜뚜뚜뚜뚜�뚜뚜뚜��"
        targets = ['\uFFFD']
        self.assertEqual(purge_symbols(text, targets), "뚜뚜뚜뚜뚜뚜뚜뚜")
        
        text = "반가~워요~!"
        targets = ['~', '!']
        self.assertEqual(purge_symbols(text, targets), "반가워요")

        # 멀티 캐릭터 타겟 테스트
        text = "Hello... World..."
        targets = ["..."]
        self.assertEqual(purge_symbols(text, targets), "Hello World")

    def test_remove_middle_symbols(self):
        """텍스트 중간의 대상만 제거하고 끝부분은 유지하는지 테스트"""
        text = "뚜뚜뚜뚜뚜�뚜뚜뚜��"
        targets = ['\uFFFD']
        self.assertEqual(remove_middle_symbols(text, targets), "뚜뚜뚜뚜뚜뚜뚜뚜�")

        text = "안~녕~하세요~~"
        targets = ['~']
        self.assertEqual(remove_middle_symbols(text, targets), "안녕하세요~")

        # 멀티 캐릭터 타겟 테스트
        text = "잠시...만요..."
        targets = ["..."]
        self.assertEqual(remove_middle_symbols(text, targets), "잠시만요...")

    def test_regex_targets(self):
        """리터럴과 컴파일된 정규식 패턴을 섞어 넘겨도 제거되는지 테스트"""
        text = "[음악] 노래 [박수] 환호"
        targets = (re.compile(r"\[[^\]]+\] ?"),)
        self.assertEqual(purge_symbols(text, targets), "노래 환호")

        text = "지금까지 강남에서 ABC 뉴스 홍길동입니다"
        targets = (re.compile(r"ABC 뉴스 \S+입니다"),)
        self.assertEqual(purge_symbols(text, targets), "지금까지 강남에서 ")

        # remove_middle: 패턴 매치도 문장 끝 1개는 보존
        text = "웃음ㅋㅋ 정말ㅋㅋ 대박ㅋㅋ"
        targets = (re.compile("ㅋ+"),)
        self.assertEqual(remove_middle_symbols(text, targets), "웃음 정말 대박ㅋㅋ")

    def test_strip_punctuation(self):
        """기본 세트의 문장부호만 제거하고 의미 보유 기호는 남기는지 테스트"""
        text = "(웃음) 안녕... 반가워!"
        self.assertEqual(strip_punctuation(text), "웃음 안녕 반가워")

        text = '"인용" 부호와 「괄호」, — 줄표'
        self.assertEqual(strip_punctuation(text), "인용 부호와 괄호  줄표")

        # 하이픈·가운뎃점·퍼센트는 기본 세트에서 의도적으로 제외
        text = "6·25는 1950-06-25, 100% 확실"
        self.assertEqual(strip_punctuation(text), "6·25는 1950-06-25 100% 확실")

    def test_collapse_whitespace(self):
        """공백·탭 연속 축약과 양 끝 정리, 개행 보존을 테스트"""
        self.assertEqual(collapse_whitespace("  다중   공백\t\t정리  "), "다중 공백\t정리")
        self.assertEqual(collapse_whitespace("줄은  유지\n다음  줄"), "줄은 유지\n다음 줄")

        # strip_punctuation이 남긴 이중 공백을 정리하는 체이닝
        text = '"인용" 부호와 「괄호」, — 줄표'
        self.assertEqual(collapse_whitespace(strip_punctuation(text)), "인용 부호와 괄호 줄표")

if __name__ == "__main__":
    unittest.main()
