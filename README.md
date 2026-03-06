# 고놈 KorNorm

2022–2023년 한 AI 음성 합성 스타트업에서 보낸 1년 남짓한 시간 동안 유용하게 썼던 사내 한국어 정규화 도구가 그리워서 직접 만들기 시작한 저장소입니다.  
This repository is born out of nostalgia for a decent in-house Korean normalizer I used during my brief one-year stint at an AI speech startup.

인터넷 곳곳의 능력자들이 공개한 코드를 긁어 모은 뒤, AI 코딩 에이전트에게 맡겨서 재구성하는 방식으로 구현할 예정입니다.  
I'll build this by gathering code from various gigachads online and shoving them all into an AI coding agent to reorganize them.

---

###### 표절할 코드 목록 List to plagiarize

* 내가 퇴사하면서 회사에 유기해놓고 왔던 내 기억 속 텍스트 정규화 라이브러리
* [jamo](https://github.com/jdongian/python-jamo) : [조슈아 동](https://github.com/JDongian)님의 근본 자모 패키지
* 한국어 G2P 라이브러리
  - [Kyubyong/g2pK](https://github.com/Kyubyong/g2pK) : [TUNiB 박규병](https://github.com/Kyubyong)님 g2pK 원본 (2020년 마지막 커밋)
  - [harmlessman/g2pkk](https://github.com/harmlessman/g2pkk) : [무해한생물](https://drawing-thoughts.tistory.com/)님 g2pK 전체 OS 버젼 (2022년 마지막 커밋)
  - [tenebo/g2pk2](https://github.com/tenebo/g2pk2) : [이인표](https://github.com/tenebo)님 g2pK 최신본 (2023년 마지막 커밋)
  - [SMART-G2P](https://github.com/SMART-TTS/SMART-G2P) : SMART-G2P (2023년 마지막 커밋)
* [pecab](https://github.com/hyunwoongko/pecab) : [카카오 고현웅](https://github.com/hyunwoongko)님 순수 파이썬 Mecab
* `OKT` 시리즈
  - [twitter-korean](https://github.com/twitter/twitter-korean-text) : 트위터 코리안 구 버젼 (2019년 마지막 커밋)
  - [open-korean-text](https://github.com/open-korean-text/open-korean-text) : 트위터 코리안 오픈소스 버젼 (2024년 마지막 커밋)
* 유명한 한국어 TTS 클리너 함수들
  - [carpedm20/multi-speaker-tacotron-tensorflow](https://github.com/carpedm20/multi-speaker-tacotron-tensorflow/tree/master/text) : [前 OpenAI 김태훈](https://carpedm30.notion.site/me)님 한국어 tacotron 전처리 함수
  - [hash2430/pitchtron](https://github.com/hash2430/pitchtron/blob/hard/text/korean.py) : [정성희](https://jsh-tts.tistory.com/)님 한국어 pitchtron 전처리 함수
  - [keonlee9420/Expressive-FastSpeech2](https://github.com/keonlee9420/Expressive-FastSpeech2/blob/main/text/korean.py) : [크래프톤 이건](https://sites.google.com/view/keonlee9420)님 한국어 FastSpeech2 전처리 함수
  - [jwj7140/Bert-VITS2-Korean](https://github.com/jwj7140/Bert-VITS2-Korean/blob/main/text/korean.py) : [경기대 정우준](https://github.com/jwj7140)님 한국어 Bert-VITS2 전처리 함수
  - [ORI-Muchim/MB-iSTFT-VITS-Korean](https://github.com/ORI-Muchim/MB-iSTFT-VITS-Korean/blob/main/text/korean.py) : [단국대 조민형](https://ori-muchim.github.io/)님 한국어 MB-iSTFT-VITS 전처리 함수
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/text/korean.py) : GPT-SoVITS (2024) 한국어 전처리 함수
* [zeroth](https://github.com/goodatlas/zeroth) : 근본 한국어 음성 인식 프로젝트
* [WFST @NeMo-text-processing](https://github.com/NVIDIA/NeMo-text-processing/blob/main/tutorials/WFST_Tutorial.ipynb) : `pynini` 및 `WFST(가중 유한 상태 트랜스듀서, Weighted Finite-State Transducer)`를 이용한 규칙 기반, 결정론적 텍스트 전처리기
