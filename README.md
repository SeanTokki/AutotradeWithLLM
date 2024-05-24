# LLM을 이용한 비트코인 자동매매 봇 개발일지
## 2024.03.28.
- output 형식이 일정하지 않아 형식 지정하는 프롬프트 수정. 특히 Gemini는 markdown 언어로 출력이 잦아서 형식표기문자 제거하는 로직 추가.
- output의 퀄리티를 높이기 위해서 퀄리티 높은 few-shot example 생성 및 추가.

## 2024.03.30.
- LLM이 기술지표를 계산하고 사용하지 않는 것을 확인. 따라서 pandas_ta 라이브러리를 통해 여러 기술지표를 직접 추가. 해당 라이브러리 덕분에 기술지표 확장성이 좋아짐. (원하는 지표를 추가하고 제거하는게 간단해짐)
- 기존 코드에서 시스템 프롬프트를 구현하기 위해 Gemini Chat API를 사용하였는데, 연속적인 호출에서 에러가 났음. 정확한 원인은 알 수 없지만, 채팅 히스토리에 쌓인 데이터가 너무 많아서 생기는 것 같아 다른 방법을 찾아봄.
- langchain 라이브러리를 통해 시스템 프롬프트를 Gemini에 쉽게 구현함으로써 해결.

## 2024.04.01.  
- 프롬프트 확장에 용이하도록 instructions 파일을 instructions(role, data preview, workflow, output format), context(technical glossary, considerations) 로 구분함.

## 2024.04.02.
- langchain ChatPromptTemplate을 이용해 프롬프트를 확장 및 변경에 용이하도록 재설정.
- output 형식이 일정하게 나오지 않음에 따라 output prompt의 체계화가 필요한 것으로 확인. lagnchain의 JSONParser를 이용하여 체계화된 output 구현.
- output의 퀄리티를 향상시키기 위해 좋은 fewshot example을 생성하고(llm 활용) langchain을 이용하여 fewshot prompt를 적용.

## 2024.04.03.
- ratio 형식을 아무리 지정해줘도 문자열이나 0.xx 이런식으로 나오는 현상이 발생하여 ratio translation 코드를 작성함.
- SQLite3을 이용하여 현재 asset과 recommendation을 기록하도록 구현함.

## 2024.04.05.
- context를 더 잘 활용할 수 있도록 workflow 1번에 context를 잘 읽고 머리에 새기도록 지시문을 추가함.
- instruction 곳곳에 output 타입이 JSON임을 강조함.

## 2024.04.08.
- DB 설계 변경
  - asset(<U>id</U>, timestamp, btc_balance, btc_avg_price, btc_price, krw_balance, total_asset)
  - recommendation(<U>id(fk)</U>, timestamp(fk), decision, ratio, reason, result)
  - result: 처음에는 NULL이고 다음번 실행에서 asset 삽입 후 total asset 비교해서 SUCCESS or FAIL 삽입

## 2024.04.10.
- 개발환경 이전(google colab -> aws linux + code-server)을 위해 코드 리팩토링 진행
  - global variables로 asset을 관리 -> AssetforTest class를 만들어 asset을 관리
  - 하나의 긴 코드를 autotrade.py, helper.py, DB.py, asset.py 네가지로 분리하여 모듈화.

## 2024.04.13.
- DB를 쉽게 확인하기 위한 간단한 웹페이지 제작.
- FastAPI를 활용하여 백엔드 서버 열고 DB에서 데이터 불러와서 html 파일 렌더링.

## 2024.04.18.
- 가끔씩 AI response의 형식이 이상하게 나올 때가 있어서 format checking을 하여 의도되지 않은 형식의 response를 거르고 3번의 재생성 기회를 부여.
- 거래 주기를 30분에 한번으로 변경하여 거래 빈도를 낮춤. 추가적으로, 거래 수수료도 asset 계산에 포함시킴.
- 크롤링을 하려는데 '코인니스' 웹사이트가 동적 웹사이트라 BeautifulSoup4 말고 다른 방법을 써야한다고 함. 추후 적용 예정.

## 2024.04.26.
- 기존 AWS 프리티어 서버로는 create-react-app을 사용할 수 없어서 부득이하게 개발 환경을 옮기게 됨.
- groomide로 다시 돌아와서 환경설정 중 몇 가지 장벽에 부딫힘.
  - langchain-google-genai는 protobuf 5.x 라이브러리에는 작동하지 않음을 깨닫고 requirements.txt 수정.
  - code-server를 사용할 때 CRA에서 경로를 제대로 못잡아주는 문제, 그리고 웹소켓 통신 문제로 HMR이 안되는 문제 등이 있었는데, 다음 링크를 통해 해결함.
  https://velog.io/@2wndrhs/code-server%EB%A1%9C-%EC%82%AC%EC%A7%80%EB%B0%A9%EC%97%90%EC%84%9C-%EC%BD%94%EB%94%A9%ED%95%98%EA%B8%B0-3-code-server%EB%A1%9C-%EC%9B%B9-%EC%84%9C%EB%B9%84%EC%8A%A4-%EC%8B%A4%ED%96%89-%EC%8B%9C-%EC%A3%BC%EC%9D%98%ED%95%A0-%EC%A0%90 
- 결과적으로 기존 aws 서버에서 하던 것 보다 쾌적하고, extension도 적용이 되는 좋은 환경을 설정할 수 있었음. 앞으로는 여기서 개발을 마저 진행할 것.
- 번외로 aws 서버에는 계속 30분마다 autotrade를 실시하고 있지만, 수수료 계산 설정 이후 손실 수준이 커서 response의 퀄리티를 높이기 위한 여러 방안을 더 고안 해 봐야 할 것 같음.

## 2024.05.03.
- 데이터베이스 관련 함수는 모두 DB_Class 파일에서 Database class를 통해서 동작하도록 모듈화.
- 이로인해 DB connection이 계속 유지가 되어 다른 스레드에서 DB를 접속하지 못하던 문제 해결.
- get_AI_device 함수 안에 코드가 너무 많아서 가독성을 위해 세부 함수로 쪼갬.

## 2024.05.05.
- 클래스명은 PascalCase, 함수명은 camelCase, 변수명은 snake_case로 통일시킴

## 2024.05.06.
- AsyncChromiumLoader 이용해서 코인 뉴스 사이트 크롤링, 정보를 llm을 통해 정돈시키고 메인 prompt 인풋으로 사용.

## 2024.05.13.
- AsyncChromiumLoader에 로딩이 다 안되었는데 페이지를 반환하는 문제가 있어 직접 async하게 playwright 사용하도록 수정중.

## 2024.05.14.
- playwright의 page.goto가 의도한대로 여러 링크를 다 한번에 들어가지 않는 현상 발견. 이유 찾는 중. 만약 해결 못하면 그냥 하나씩 해보는 수밖에 없음.
- 예상은 크롤링 막아놓은 사이트를 30초 기다리느라 다른것도 다 기다리는 중인 것으로...

## 2024.05.15.
- page.goto의 timeout을 100초로 늘렸더니 어느정도 정상작동 하는 것으로 확인. 아마 서버 사양 문제가 아니었을까 추측됨.
- 따라서 한번에 최대 2개의 크롤러만 실행될 수 있도록 수정함.
- 크롤링이 막힌 사이트의 경우 coinness.com/article에서 찾은 뉴스 제목으로 대체.

## 2024.05.16.
- crawler module 안에 지금까지 구현한 함수들을 배치하고, helper module 안에 getCoinnessNews() 함수를 추가하여 모든 과정을 wrapping함.
- LLM에 집어넣어서 요약하는 것까지 확인 완료.

## 2024.05.18.
- 요약문이 한글로 출력되는 문제를 해결하기 위해 instruction 수정. -> 실패... input이 다 한국어라 그런듯...
- ChatGPT 4o를 이용하여 조금 더 깔끔한 news_organize_instructions 제작.
- 기존의 instruction과 context를 수정하여 news data를 잘 알아듣고 반영하도록 수정.

## 2024.05.19.
- 기존 autotrade.py 코드랑 합쳐서 한 사이클 굴려보는 도중 pthread_create failed 오류가 생기는 것을 확인.
- 디버깅 결과 helper.py에서 데이터에 기술지표 추가하는 라인인 df.ta.strategy(CustomStrategy)에서 발생하는 것을 확인.
- 크롤러만 파일 읽기로 대체하였을 때에도 오류 발생, 아예 news data 가져오지 않았을 때에는 발생하지 않음.
- 요약하기 위한 llm invoke 과정에서 문제가 있었을 것으로 추정 -> 요약 과정을 뒤로 밀어서 하나의 체인으로 구성할까 고민 중.

## 2024.05.20.
- 뉴스 요약 과정과 AI 판단 과정을 합치는 도중, 하나의 체인 결과에 추가로 argument들을 어떻게 집어넣느냐에 대해 많은 시행착오가 있었음.
- 결국 RunnableLambda를 통해서 arguments를 추가하는 사용자 정의 함수를 chain 사이에 집어넣음으로써 해결.
- fewshot example에 양질의 예제를 집어넣기 위해 gpt-4o를 사용하여 주어진 모든 자료를 활용하여 판단 근거를 제시하는 example을 만들어냄.

## 2024.05.24.
- 본격적인 frontend 코딩에 앞서서 GPT를 활용해서 간단한 테스팅에 사용할 FastAPI - html 코드를 만들어냄.
- 백엔드로 파이썬 프레임워크를 선택한 이유는 자동매매를 파이썬 프로그램으로 코딩했기 때문에 서버상에서 프로그램을 실행/종료 시키기 용이하기 때문.
- 자세한 이유는 모르지만 vs-server 환경 문제로 html에서 fetch시에 /proxy/8000을 추가함으로서 not allowed method 문제 해결.
- 버튼을 누르면 전역변수가 바뀌도록 코딩. 추후 autotrade.py 파일 실행과 종료의 트리거로 쓰일 예정.
- aws server에 올려서 오랜기간 테스팅하고 그 결과를 지켜볼 예정.


## Todo
- exception handling... -> 에러가 떠도 프로그램이 종료되지 않도록
===================================================
- AI 웹디자인으로 그래프 시각화 + 현재 자산 정보 + history table 확인할 수 있는 웹페이지 만들기 with React.js
===================================================
- 수익을 본 recommendation만 따로 수집하여 few-shot example 업데이트
- 정보가 많이 쌓인다면 SemanticSimilarityExampleSelector 이용하여 dynamic few-shot example 사용
- 서버 열어서 upbit api키 받고 buy/sell 구현하고 서버에 24시간 구동
===================================================
- 최종 마무리는 1. 원하는 기술지표 2. 거래를 원하는 코인 3. 원하는 매매전략(pdf, txt, 웹사이트 url?, 유튜브 url?) 입력받아서
- AI 판단을 화면에 출력 / API 형식으로 return 해주는 걸로 끝내면 될듯.
