# UI 유틸리티 가이드

이 프로젝트는 공통 UI 스타일을 `frontend/src/assets/theme.css` 와 `frontend/src/assets/ui.css` 에서 중앙 관리합니다.  
임의의 CSS를 추가하거나 Bootstrap의 `text-*`, `bg-*` 같은 색상 헬퍼를 쓰지 말고, 아래 유틸리티를 우선 사용해 주세요.

## 기준 파일
- 디자인 토큰(변수): `frontend/src/assets/theme.css`
- 유틸리티 클래스: `frontend/src/assets/ui.css`

---

## 디자인 토큰 (theme.css)

### 색상
- `--bg`, `--bg-alt`, `--surface`, `--surface-alt`
- `--ink`, `--ink-soft`, `--muted`
- `--border`
- `--accent`, `--accent-strong`, `--accent-warm`

### 그림자 및 라운드
- `--shadow-1`, `--shadow-2`
- `--radius-sm`, `--radius-md`, `--radius-lg`

### 버튼
- `--btn-h`, `--btn-h-sm`, `--btn-pad-x`

---

## 유틸리티 (ui.css)

### 카드
- `ui-card` (기본)
- `ui-card-soft` (뮤트 배경)

### 배지
- `ui-badge`
- `ui-badge-primary`
- `ui-badge-success`
- `ui-badge-warning`
- `ui-badge-info`

### 버튼
- `ui-btn`
- `ui-btn-primary`
- `ui-btn-ghost`
- `ui-btn-danger`
- `ui-btn-sm`

### 텍스트
- `ui-title`, `ui-sub`
- `ui-text-ink`, `ui-text-soft`, `ui-text-muted`
- `ui-text-accent`, `ui-text-success`, `ui-text-warning`, `ui-text-danger`

### 레이아웃
- `w100`

---

## Bootstrap 헬퍼 대체 규칙

Bootstrap의 `text-*`, `bg-*`를 쓰는 대신 아래 클래스로 교체해 주세요.

- `text-muted` → `ui-text-muted`
- `text-secondary` → `ui-text-soft`
- `text-primary` → `ui-text-accent`
- `text-success` → `ui-text-success`
- `text-warning` → `ui-text-warning`
- `text-danger` → `ui-text-danger`
- `badge bg-*` → `ui-badge` + `ui-badge-*`

---

## 사용 예시

### 버튼
```html
<button class="ui-btn ui-btn-primary">확인</button>
<button class="ui-btn ui-btn-ghost ui-btn-sm">취소</button>
```