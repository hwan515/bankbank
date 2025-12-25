import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'
const apiBaseUrl = API_BASE_URL.replace(/\/$/, '')

export const useStockStore = defineStore('stock', () => {
  const videoList = ref([])

  const favoritedIds = ref(new Set())
  const showOnlyFavorite = ref(false)

  const load = async () => {
    try {
        const res = await axios.get(`${apiBaseUrl}/stocks/load`)
        // videoList에 넣기. 
        videoList.value = res.data.items ?? []
    } catch(err) {
        console.error('load 실패: ', err)
    }
  }

  const search = async (keyword) => {
    try {
        showOnlyFavorite.value = false
        const res = await axios.get(`${apiBaseUrl}/stocks/search`,
            {
                params : {q:keyword}
            }
        )
        // videoList에 넣기. 
        videoList.value = res.data.items ?? []
    } catch(err) {
        console.error('load 실패: ', err)
    }
  }

  const toggleFavorite = (videoId) => {
    if (favoritedIds.value.has(videoId)) {
        favoritedIds.value.delete(videoId)
    } else {
        favoritedIds.value.add(videoId)
    }
  }

  const toggleFavoriteFilter = () => {
    showOnlyFavorite.value = !showOnlyFavorite.value
  }

  const filteredVideoList = computed(() => {
    if(!showOnlyFavorite.value) return videoList.value
    return videoList.value.filter(v => 
        favoritedIds.value.has(v.id?.videoId)
    )
  })

  return {
    load, 
    search,
    videoList,
    favoritedIds,
    showOnlyFavorite,
    toggleFavorite,
    toggleFavoriteFilter,
    filteredVideoList,
   }
})
