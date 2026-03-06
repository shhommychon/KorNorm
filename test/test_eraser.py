import unittest
from kornorm.heuristics.eraser import purge_symbols, remove_middle_symbols

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

if __name__ == "__main__":
    unittest.main()
