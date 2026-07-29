import unittest
from kornorm.phonology.engine import apply_phonology

class TestContextHomograph(unittest.TestCase):
    def test_bed_reading(self):
        """침구 문맥 단서(펴·눕·들)에서 [잠짜리]를 선택하는지 테스트"""
        self.assertEqual(apply_phonology("잠자리를 펴고 눕다", output_format="hangul"), "잠짜리를 펴고 눕따")
        self.assertEqual(apply_phonology("잠자리에 들었다", output_format="hangul"), "잠짜리에 드럳따")

    def test_insect_reading(self):
        """곤충 문맥 단서(난다·잡·여름)에서 [잠자리]를 선택하는지 테스트"""
        self.assertEqual(apply_phonology("잠자리가 하늘을 난다", output_format="hangul"), "잠자리가 하느를 난다")
        self.assertEqual(apply_phonology("여름 잠자리를 잡았다", output_format="hangul"), "여름 잠자리를 자받따")

    def test_default_reading(self):
        """단서가 없으면 기본 독법 [잠짜리]를 유지하는지 테스트"""
        self.assertEqual(apply_phonology("잠자리", output_format="hangul"), "잠짜리")

if __name__ == "__main__":
    unittest.main()
