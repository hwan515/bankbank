/**
 * 카드 관련 공용 유틸리티 함수
 */

// HTML 엔티티 디코딩
export function decodeHtml(text) {
  if (!text) return ''
  const entities = {
    '&middot;': '·',
    '&bull;': '•',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&nbsp;': ' ',
    '&quot;': '"',
    '&#39;': "'",
    '&apos;': "'",
    '&ndash;': '–',
    '&mdash;': '—',
    '&hellip;': '…',
    '&trade;': '™',
    '&reg;': '®',
    '&copy;': '©',
    '&times;': '×',
    '&divide;': '÷',
    '&plusmn;': '±',
    '&rarr;': '→',
    '&larr;': '←',
    '&uarr;': '↑',
    '&darr;': '↓',
  }
  return text.replace(/&[a-zA-Z0-9#]+;/g, match => entities[match] || match)
}

// 혜택 텍스트 포맷팅 (공백 있는 / 를 줄바꿈으로)
export function formatBenefits(text) {
  if (!text) return ''
  return decodeHtml(text).replace(/\s+\/\s+/g, '\n')
}

// 전월실적 포맷팅
export function formatSpending(amount) {
  if (!amount || amount === 0) return '조건 없음'
  return `${(amount / 10000).toLocaleString()}만원 이상`
}

// 추천 점수 포맷팅
export function formatScore(score) {
  const similarity = Math.max(0, Math.min(100, (1 - score / 2) * 100))
  return similarity.toFixed(0) + '%'
}

// 순위 뱃지 클래스
export function getRankBadgeClass(index) {
  if (index === 0) return 'bg-warning text-dark'
  if (index === 1) return 'bg-secondary text-white'
  if (index === 2) return 'bg-danger text-white'
  return 'bg-light text-dark'
}

// 점수 색상 클래스
export function getScoreClass(score) {
  if (score < 0.5) return 'text-success'
  if (score < 1.0) return 'text-primary'
  return 'text-warning'
}

// 카드 타입 라벨
export function getCardTypeLabel(type) {
  return type === 'CRD' ? '신용카드' : '체크카드'
}

// 카드 타입 뱃지 클래스
export function getCardTypeBadgeClass(type) {
  return type === 'CRD' ? 'bg-primary' : 'bg-success'
}

// 카테고리 코드 → 한글 변환
export const categoryMap = {
  'TRANS': '교통',
  'COMM': '통신',
  'SHOP': '쇼핑',
  'COFFEE': '카페',
  'FOOD': '외식',
  'GAS': '주유',
  'UTIL': '공과금',
  'SUB': '구독',
  'PAY': '페이',
  'MOVIE': '영화',
  'TRAVEL': '여행',
  'ONLINE': '온라인',
  'MART': '마트',
  'BEAUTY': '뷰티',
  'HEALTH': '건강',
  'EDU': '교육',
  'ETC': '기타'
}

export function getCategoryName(code) {
  return categoryMap[code] || code || '기타'
}

// 이미지 에러 핸들링 (placeholder 이미지로 대체)
export function handleImageError(event, size = '300x200') {
  event.target.src = `https://placehold.co/${size}/f8f9fa/999?text=No+Image`
}

// Vue 컴포저블로 사용
export function useCardUtils() {
  return {
    decodeHtml,
    formatBenefits,
    formatSpending,
    formatScore,
    getRankBadgeClass,
    getScoreClass,
    getCardTypeLabel,
    getCardTypeBadgeClass,
    getCategoryName,
    categoryMap,
    handleImageError
  }
}
