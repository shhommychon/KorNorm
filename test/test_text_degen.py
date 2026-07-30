import unittest
from functools import partial
from kornorm.heuristics.repetition import fix_text_degeneration, find_text_degeneration
from kornorm.pipeline import StreamPipeline, BatchPipeline

# BatchPipeline(multiprocessing)에서 직렬화가 가능하도록 최상단에 함수를 정의합니다.
fix_text_degeneration_3 = partial(fix_text_degeneration, repeat_count=3, replace_char="...")

class TestRepetition(unittest.TestCase):
    def setUp(self):
        self.sample = "으아아아아아아아아악"  # '아'가 8번 반복
        self.sample_multi = "아니! 아니! 아니! 아니! 아니! 아니!" # "아니!"가 6번 반복 (띄어쓰기 포함)

    def test_basic_function(self):
        """순정 함수 테스트 (기본값: 5회 반복 후 〃 추가)"""
        result = fix_text_degeneration(self.sample)
        # '아' 5번 + '〃'
        self.assertEqual(result, "으아아아아아〃악")
        
        result_multi = fix_text_degeneration(self.sample_multi, repeat_count=3, replace_char='♤')
        # "아니! " 6번 + '♤'
        self.assertEqual(result_multi, "아니! 아니! 아니! ♤")

        result_multi = fix_text_degeneration('')
        self.assertEqual(result_multi, '')

        result_multi = fix_text_degeneration("abcde ")
        self.assertEqual(result_multi, "abcde ")

    def test_find_degeneration(self):
        """반복 조각의 위치·단위·횟수를 텍스트 무변경으로 보고하는지 테스트"""
        result = find_text_degeneration(self.sample)
        self.assertEqual(result, [(1, 9, '아', 8)])
        # 보고된 스팬을 원문에서 잘라내면 반복 조각 그대로여야 함
        start, end, unit, count = result[0]
        self.assertEqual(self.sample[start:end], unit * count)

        # 공백 포함 반복 단위 (끝의 부분 반복은 통째 횟수에서 제외됨)
        result_multi = find_text_degeneration(self.sample_multi, repeat_count=3)
        self.assertEqual(result_multi, [(0, 23, "아니! ", 5)])

        # 무반복 텍스트와 빈 텍스트는 빈 목록
        self.assertEqual(find_text_degeneration("정상 문장입니다"), [])
        self.assertEqual(find_text_degeneration(''), [])

    def test_find_matches_fix(self):
        """fix가 축약하는 입력과 find가 탐지하는 입력이 일치하는지 테스트"""
        samples = [self.sample, self.sample_multi, "정상 문장입니다", "하하하하하하", '']
        for sample in samples:
            fixed = (fix_text_degeneration(sample) != sample)
            found = (find_text_degeneration(sample) != [])
            self.assertEqual(fixed, found, sample)

    def test_stream_pipeline_with_partial(self):
        """StreamPipeline에 partial로 파라미터를 수정한 함수를 넣어 테스트"""
        # repeat_count=3, replace_char="..." 적용
        pipeline = StreamPipeline(fix_text_degeneration_3)
        samples = [self.sample, self.sample_multi]
        
        results = list(pipeline(samples))
        
        self.assertEqual(results[0], "으아아아...악")
        self.assertEqual(results[1], "아니! 아니! 아니! ...")

    def test_batch_pipeline_with_partial(self):
        """BatchPipeline에 partial로 파라미터를 수정한 함수를 넣어 테스트"""
        # 멀티프로세싱을 위해 최상단에 정의된 fix_text_degeneration_3 사용
        pipeline = BatchPipeline(fix_text_degeneration_3)
        samples = [self.sample, self.sample_multi]
        
        # 소량 데이터이므로 chunksize=1
        results = pipeline(samples, chunksize=1)
        
        self.assertEqual(results[0], "으아아아...악")
        self.assertEqual(results[1], "아니! 아니! 아니! ...")

if __name__ == "__main__":
    unittest.main()
