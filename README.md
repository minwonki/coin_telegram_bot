Sample Coin Alert to Telegram bot

# Setting

1. Google App Engine 가입 -> 프로젝트 생성 (Python)
2. Telegram Bot 생성
3. 소스 다운로드
4. Telegram Bot 토큰 변경
5. Deploy (gcloud app deploy app.yaml --project project_name)
   * app.yaml <- 기본 설정
   * cron.yaml <- 주기적인 작업 설정
   * index.yaml <- DB에서 Query 할때 사용 되는 설정 
6. Telegram Bot WebHook 설정
   * https://domain/telegram/me
   * https://domain/telegram/set-webhook?url=https://domain/telegram/webhook
7. 끝.

