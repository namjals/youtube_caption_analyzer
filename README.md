# Youtube Caption Analyzer

"[포프티비 검색엔진 소개](https://www.youtube.com/watch?v=7bhohKCFi-U)" 영상을 보고 계기가 되어 만들었습니다.

자막을 다운 받아, 제목+설명+자막의 명사를 인덱싱, 키워드 추출하여 검색 결과를 보여줍니다.



### 주요 기능

- 채널 id로 해당 채널의 모든 자막을 다운로드 합니다.
- soynlp(영문,숫자) + komoran(한글) 조합하여 명사를 추출 합니다.
- 검색 결과에 비디오별로 키워드를 출력합니다. (doc2vec, soykeyword)
- 인덱싱을 이용해 빠른 검색이 가능합니다.
- 수동 자막이 늘어날 수록 성능이 나아질 것 입니다.




# 결과




### 메인

![alt text](https://github.com/namjals/youtube_caption_analyzer/blob/master/img/main.png)



### 검색 결과 1

![alt text](https://github.com/namjals/youtube_caption_analyzer/blob/master/img/result1.png)



### 검색 결과2

![alt text](https://github.com/namjals/youtube_caption_analyzer/blob/master/img/result2.png)




# 설치


- 환경 : Windows , Python36

```
pip install --upgrade google-api-python-client
pip install flask
pip install requests
pip install werkzeug
pip install soynlp
pip install JPype
pip install gensim
```




# 실행 방법


1. [구글 API 콘솔](https://console.cloud.google.com/apis/)에서 인증정보를 만듭니다.

2. 인증 정보를 /analyzer/key/client_secret.json로 다운로드 합니다.

3. 승인된 리디렉션 URI에 <http://localhost:8080/oauth2callback> 를 추가합니다.

4. 대시보드에 "YouTube Data API v3"를 추가합니다.

   - 구글 API 인증 과정은  [여기](https://opentutorials.org/course/2473/16571)에서 자세히 배울 수 있습니다.

5. 코드를 실행합니다.

   ```
   python server.py
   ```

6. [http://localhost:8080](http://localhost:8080/) 에 접속합니다.

7. 검색어를 입력하여 검색합니다.

8. /analyzer/data 폴더를 지우고, "1. Get auth" 클릭합니다.

9. 인증 진행 후, 자막을 다운받고자 하는 채널 id를 입력합니다.

   - ex) 포프tv : UC63J0Q5huHSlbNT3KxvAaHQ

10. "Download"를 클릭합니다.

11. 다운로드가 완료 되면, "1. Train"을 클릭합니다.

12. 훈련이 완료 되면 "2. Update"를 클릭합니다.

13. 검색어를 입력하여 검색합니다.





# 미진한 부분

- 검색어에 대해 공백 기준 토크나이징.
- 1글자 단어 인덱싱 X.
- 훈련, 업데이트 시 진행 바.
- 유사 영상?
