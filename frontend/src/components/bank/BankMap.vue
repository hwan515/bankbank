<template>
  <div class="page">
    <!-- 상단 바 -->
    <div class="topbar">
      <div class="brand">
        <div class="dot" />
        <div>
          <div class="brand-title">지도 검색</div>
          <div class="brand-sub">장소를 검색하고 경로를 확인하세요</div>
        </div>
      </div>

      <div class="search">
        <SearchBar />
      </div>
    </div>

    <!-- 본문 -->
    <div class="layout">
      <!-- 지도 카드 -->
      <section class="card map-card">
        <div class="card-head">
          <div class="card-title">Map</div>
          <div class="card-meta">Kakao Maps</div>
        </div>
        <div class="map-wrap">
          <div ref="mapEl" class="map"></div>
        </div>
      </section>

      <!-- 결과 패널 -->
      <aside class="card panel">
        <div class="card-head">
          <div>
            <div class="card-title">검색 결과</div>
            <div class="card-meta">{{ mapStore.places.length }}개</div>
          </div>

          <button class="mini-btn" type="button" @click="mapStore.search('')">
            초기화
          </button>
        </div>

        <div v-if="mapStore.places.length === 0" class="empty">
          <div class="empty-title">아직 결과가 없어요</div>
          <div class="empty-sub">검색어를 입력하고 Enter를 눌러보세요.</div>
        </div>

        <ul v-else class="list">
          <li
            v-for="p in mapStore.places"
            :key="p.id"
            class="item"
            @click="mapStore.drawRouteTo(p)"
          >
            <div class="item-top">
              <div class="name">{{ p.place_name }}</div>
              <div v-if="p.distance" class="badge">{{ p.distance }}m</div>
            </div>

            <div class="addr">{{ p.road_address_name || p.address_name }}</div>

            <div class="meta-row">
              <span v-if="p.phone" class="meta">{{ p.phone }}</span>
              <span v-if="p.category_name" class="meta">· {{ p.category_name }}</span>
            </div>
          </li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import SearchBar from "./SearchBar.vue";
import { useMapStore } from "@/stores/maps";

const mapEl = ref(null);
const mapStore = useMapStore();
const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_JS_KEY;

const loadKakao = () =>
  new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) return resolve();

    const script = document.createElement("script");
    script.async = true;
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_JS_KEY}&autoload=false&libraries=services,clusterer,drawing`;
    script.onload = () => window.kakao.maps.load(resolve);
    script.onerror = () => reject(new Error("Kakao SDK load failed"));
    document.head.appendChild(script);
  });

onMounted(async () => {
  await loadKakao();

  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 5,
  };

  const map = new window.kakao.maps.Map(mapEl.value, options);
  mapStore.setMap(map);
});
</script>

<style scoped>
/* Page */
.page {
  max-width: 1100px;
  margin: 28px auto;
  padding: 0 16px;
  color: #111;
}

/* Topbar */
.topbar {
  display: grid;
  grid-template-columns: 1fr minmax(280px, 420px);
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #111;
}

.brand-title {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -0.2px;
}

.brand-sub {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.search {
  justify-self: end;
  width: 100%;
}

/* Layout */
.layout {
  display: grid;
  grid-template-columns: 1.7fr 1fr;
  gap: 12px;
  align-items: start;
}

/* Card */
.card {
  border: 1px solid #ececec;
  border-radius: 14px;
  background: #fff;
  overflow: hidden;
}

.card-head {
  padding: 14px 14px 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.card-title {
  font-weight: 800;
  font-size: 14px;
  letter-spacing: -0.2px;
}

.card-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* Map */
.map-card {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.map-wrap {
  padding: 12px;
}

.map {
  width: 100%;
  height: 520px;
  border-radius: 12px;
  overflow: hidden;
  background: #f6f7f8;
}

/* Panel */
.panel {
  height: 100%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
}

.mini-btn {
  height: 30px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 12px;
  cursor: pointer;
}
.mini-btn:hover {
  background: #fafafa;
}

.empty {
  padding: 16px 14px 18px;
}
.empty-title {
  font-weight: 800;
  font-size: 13px;
}
.empty-sub {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

/* List */
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 520px;
  overflow: auto;
  border-top: 1px solid #f2f2f2;
}

/* nice scroll */
.list::-webkit-scrollbar { width: 10px; }
.list::-webkit-scrollbar-thumb {
  background: #e9e9e9;
  border-radius: 999px;
  border: 3px solid #fff;
}

.item {
  padding: 12px 14px;
  border-bottom: 1px solid #f3f3f3;
  cursor: pointer;
  transition: background 0.12s ease;
}

.item:hover {
  background: #fcfcfc;
}

.item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.name {
  font-weight: 800;
  font-size: 13px;
  letter-spacing: -0.1px;
}

.badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #ededed;
  color: #111;
  background: #fff;
}

.addr {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.35;
}

.meta-row {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

/* Responsive */
@media (max-width: 992px) {
  .topbar {
    grid-template-columns: 1fr;
  }
  .search {
    justify-self: start;
  }
  .layout {
    grid-template-columns: 1fr;
  }
  .map {
    height: 420px;
  }
  .list {
    max-height: 420px;
  }
}
</style>
