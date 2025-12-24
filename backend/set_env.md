### .env 파일

# database
MYSQL_HOST=your_host
MYSQL_PORT=your_db
MYSQL_DB=yout_db
MYSQL_USER=user
MYSQL_PASSWORD=your_password

# api key
FIN_API_KEY=your_api_key

#
 1. .env 파일에 추가할 환경변수:
  DJANGO_SECRET_KEY=your-secure-secret-key
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1
  GMS_BASE_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1
  2. 프로덕션 배포 전:
    - DEBUG=False 설정
    - 실제 도메인을 ALLOWED_HOSTS에 추가
    - 강력한 DJANGO_SECRET_KEY 생성