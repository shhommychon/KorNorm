# [KorNorm 파이프라인 엔진 모듈]
# 
# 이 모듈은 '단일 문자열 입력 -> 단일 문자열 출력' 형태의 순수 함수(Pure Function)들을 
# 조립하여 실행하는 두 가지 방식의 파이프라인을 제공합니다. 
# 
# 설계 철학:
# - 전처리 로직(퍼즐 조각)은 어떤 종류의 파이프라인에서 실행되더라도 일관되게 작동해야 합니다.
# - 전처리 함수 안에는 for문으로 텍스트 리스트를 순회하는 코드가 없어야 하며, 오직 단일 텍스트 처리에만 집중합니다.
# - 이를 통해 로직과 실행 엔진 사이의 결합도를 낮추고 확장이 용이한 구조를 유지합니다.

import concurrent.futures
from typing import Iterable, Callable, List, Optional


class StreamPipeline:
    """
    메모리 최적화: 제너레이터 기반 지연 평가(Lazy Evaluation) 파이프라인.
    
    이 파이프라인은 입력 텍스트 스트림을 하나씩 순차적으로 처리합니다.
    100GB 이상의 거대한 텍스트 파일을 처리할 때와 같이 메모리 점유율을 
    최소화해야 하는 시나리오에 적합합니다.
    """
    def __init__(self, *funcs: Callable[[str], str]):
        """
        Args:
            *funcs (Callable): 적용할 전처리 함수 리스트. 순차적으로 적용됩니다.
        """
        self.funcs = funcs

    def __call__(self, texts: Iterable[str]):
        """
        입력된 Iterable을 순회하며 전처리 함수들을 적용하는 제너레이터를 반환합니다.
        
        Args:
            texts (Iterable[str]): 처리할 원본 문자열들의 스트림.
            
        Yields:
            str: 모든 전처리 함수가 적용된 문자열.
        """
        for text in texts:
            # 텍스트 하나에 대해 모든 함수를 순차적으로 적용 (Chain of Responsibility)
            for func in self.funcs:
                text = func(text)
            yield text


class BatchPipeline:
    """
    속도 최적화: 멀티프로세싱 기반 병렬 처리 파이프라인.
    
    복잡한 정규식이나 무거운 G2P 변환 등 CPU 연산 집약적인 작업을 수행할 때
    CPU 멀티 코어를 활용하여 처리 속도를 극대화합니다.
    
    주의 및 한계:
    - 전처리 함수는 반드시 모듈 최상단(Top-level)에 정의되어 직렬화(Pickling) 가능해야 합니다.
    - RAM 사용량 주의: 'Worker Initializer' 패턴 사용 시, 무거운 객체(예: 1GB 사전)는 
      워커 프로세스 개수(max_workers)만큼 메모리에 복제됩니다. 
      예: 사전 1GB * 워커 8개 = 8GB RAM 소모. 타겟 하드웨어의 RAM 용량을 고려하십시오.
    """
    def __init__(
        self, 
        *funcs: Callable[[str], str], 
        max_workers: Optional[int] = None, 
        initializer: Optional[Callable] = None
    ):
        """
        Args:
            *funcs (Callable): 적용할 전처리 함수 리스트.
            max_workers (int, optional): 사용할 프로세스 개수. None일 경우 CPU 코어 수에 맞춤.
            initializer (Callable, optional): 각 워커 프로세스가 가동될 때 최초 1회 실행되는 초기화 함수. 
                무거운 G2P 사전 등을 워커의 전역 메모리에 로드할 때 활용합니다.
        """
        self.funcs = funcs
        self.max_workers = max_workers
        self.initializer = initializer

    def _process_single(self, text: str) -> str:
        """멀티프로세스 워커가 실행할 단일 텍스트 처리 로직."""
        for func in self.funcs:
            text = func(text)
        return text

    def __call__(self, texts: Iterable[str], chunksize: int = 1000) -> List[str]:
        """
        병렬로 작업을 분배하고 처리된 결과 리스트를 반환합니다.
        
        Args:
            texts (Iterable[str]): 처리할 원본 문자열들.
            chunksize (int): 각 워커에 한 번에 전달할 데이터 크기. 
                오버헤드와 처리 속도 사이의 균형을 위해 조절 가능합니다.
        """
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers,
            initializer=self.initializer
        ) as executor:
            # map을 사용하여 입력 순서를 유지하며 병렬 처리
            results = executor.map(self._process_single, texts, chunksize=chunksize)
            return list(results)
