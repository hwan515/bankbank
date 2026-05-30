# Infrastructure

Portainer 또는 Docker Compose로 운영 서비스를 올리기 위한 설정입니다.

## Files

- `docker-compose.yml`: backend, frontend, MySQL, Redis, ChromaDB stack 정의
- `env.example`: Portainer environment variables 예시

## Services

| Service | Container | Internal endpoint | Published port |
| --- | --- | --- | --- |
| Backend | `bankbank-backend` | `backend:8000` | `18000` |
| Frontend | `bankbank-frontend` | `frontend:80` | `18080` |
| MySQL | `bankbank-mysql` | `mysql:3306` | `33306` |
| Redis | `bankbank-redis` | `redis:6379` | `16379` |
| ChromaDB | `bankbank-chroma` | `chroma:8000` | `18001` |

## Portainer Deploy

1. Portainer에서 새 Stack을 생성합니다.
2. `docker-compose.yml` 내용을 Stack Web editor에 붙여넣습니다.
3. `env.example`의 값을 실제 운영 값으로 바꿔 Environment variables에 등록합니다.
4. Stack을 배포합니다.
5. 기존 DB를 옮기는 경우 새 MySQL이 빈 상태일 때 덤프를 복원합니다.

## Database Migration

기존 운영 DB는 `hwan515.synology.me:23306 / finance_db`를 사용했습니다. 새 stack MySQL은 포트 충돌을 피하기 위해 기본 공개 포트를 `33306`으로 둡니다.

```bash
mysqldump -h hwan515.synology.me -P 23306 -u user -p \
  --single-transaction --routines --triggers --events \
  --set-gtid-purged=OFF finance_db > finance_db.sql

mysql -h hwan515.synology.me -P 33306 -u root -p finance_db < finance_db.sql
```

## Post Deploy

DB 복원 후 ChromaDB에는 카드 벡터를 별도로 적재해야 합니다.

```bash
python manage.py sync_chroma --all --batch-size 50
```
