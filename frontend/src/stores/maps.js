import axios from "axios";
import { ref } from "vue";
import { defineStore } from "pinia";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";
const apiBaseUrl = API_BASE_URL.replace(/\/$/, "");

function getCurrentPos() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      reject,
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });
}

export const useMapStore = defineStore("map", () => {
  const map = ref(null);

  const places = ref([]);       // 검색 결과
  const markers = ref([]);      // 장소 마커들
  const routeLine = ref(null);  // 경로 polyline
  const infoWindow = ref(null);

  const setMap = (m) => {
    map.value = m;
    infoWindow.value = new window.kakao.maps.InfoWindow({ zIndex: 2 });
  };

  const clearMarkers = () => {
    markers.value.forEach((m) => m.setMap(null));
    markers.value = [];
  };

  const clearRoute = () => {
    if (routeLine.value) routeLine.value.setMap(null);
    routeLine.value = null;
  };

  // 1) 키워드 검색 → 마커 + bounds + 리스트 저장
  const search = (keyword) => {
    const q = (keyword ?? "").trim();
    if (!q || !map.value) return;

    if (!window.kakao?.maps?.services) {
      console.error("Kakao services library not loaded");
      return;
    }

    const ps = new window.kakao.maps.services.Places();

    ps.keywordSearch(q, (data, status) => {
      if (status !== window.kakao.maps.services.Status.OK) {
        places.value = [];
        clearMarkers();
        clearRoute();
        return;
      }

      places.value = data;
      clearMarkers();
      clearRoute();

      const bounds = new window.kakao.maps.LatLngBounds();

      data.forEach((p) => {
        const pos = new window.kakao.maps.LatLng(p.y, p.x);

        const marker = new window.kakao.maps.Marker({
          map: map.value,
          position: pos,
        });

        window.kakao.maps.event.addListener(marker, "click", () => {
          infoWindow.value.setContent(
            `<div style="padding:6px 8px;font-size:12px;">
              <b>${p.place_name}</b><br/>
              ${p.road_address_name || p.address_name || ""}
            </div>`
          );
          infoWindow.value.open(map.value, marker);
        });

        markers.value.push(marker);
        bounds.extend(pos);
      });

      map.value.setBounds(bounds);
    });
  };

  // 2) (현 위치 → 선택한 장소) 경로 그리기
  const drawRouteTo = async (place) => {
  if (!map.value) return;

  const destLng = Number(place.x);
  const destLat = Number(place.y);

  const { lat: originLat, lng: originLng } = await getCurrentPos();

  let res;
  try {
    res = await axios.get(`${apiBaseUrl}/api/directions/`, {
      params: {
        origin_lng: originLng,
        origin_lat: originLat,
        dest_lng: destLng,
        dest_lat: destLat,
      },
    });
  } catch (err) {
    console.error("directions request failed:", err?.response?.status, err?.response?.data || err);
    return;
  }

  const pathRaw = res.data?.path;
  if (!Array.isArray(pathRaw) || pathRaw.length === 0) {
    console.error("directions response has no path:", res.data);
    return;
  }

  const linePath = pathRaw.map((p) => new window.kakao.maps.LatLng(p.lat, p.lng));

  if (routeLine.value) routeLine.value.setMap(null);

  routeLine.value = new window.kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 5,
  });
  routeLine.value.setMap(map.value);

  const bounds = new window.kakao.maps.LatLngBounds();
  linePath.forEach((ll) => bounds.extend(ll));
  map.value.setBounds(bounds);
};


  return {
    map,
    places,
    setMap,
    search,
    drawRouteTo,
  };
});
