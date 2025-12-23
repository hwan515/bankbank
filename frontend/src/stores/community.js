import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from './api'

export const useCommunityStore = defineStore('community', () => {
  const posts = ref([])
  const currentPost = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchPosts = async (boardType = null) => {
    loading.value = true
    error.value = null
    try {
      const query = boardType ? `?board=${boardType}` : ''
      const res = await api.get(`/api/community/posts/${query}`)
      posts.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchPostDetail = async (postId) => {
    loading.value = true
    error.value = null
    try {
      const res = await api.get(`/api/community/posts/${postId}/`)
      currentPost.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const createPost = async (payload) => {
    try {
      const res = await api.post('/api/community/posts/', payload)
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const updatePost = async (postId, payload) => {
    try {
      const res = await api.patch(`/api/community/posts/${postId}/`, payload)
      currentPost.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const deletePost = async (postId) => {
    try {
      await api.delete(`/api/community/posts/${postId}/`)
      currentPost.value = null
      posts.value = posts.value.filter((p) => p.id !== postId)
      return true
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const createComment = async (postId, content) => {
    try {
      const res = await api.post(`/api/community/posts/${postId}/comments/`, {
        content,
      })
      if (currentPost.value && currentPost.value.comments) {
        currentPost.value.comments.push(res.data)
      }
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const updateComment = async (commentId, content) => {
    try {
      const res = await api.patch(`/api/community/comments/${commentId}/`, {
        content,
      })
      if (currentPost.value?.comments) {
        const idx = currentPost.value.comments.findIndex((c) => c.id === commentId)
        if (idx !== -1) currentPost.value.comments[idx] = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const deleteComment = async (commentId) => {
    try {
      await api.delete(`/api/community/comments/${commentId}/`)
      if (currentPost.value?.comments) {
        currentPost.value.comments = currentPost.value.comments.filter(
          (c) => c.id !== commentId
        )
      }
      return true
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const reactToPost = async (postId, reaction) => {
    try {
      const res = await api.post(`/api/community/posts/${postId}/${reaction}/`)
      currentPost.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const reactToComment = async (commentId, reaction) => {
    try {
      const res = await api.post(`/api/community/comments/${commentId}/${reaction}/`)
      if (currentPost.value?.comments) {
        const idx = currentPost.value.comments.findIndex((c) => c.id === commentId)
        if (idx !== -1) currentPost.value.comments[idx] = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    posts,
    currentPost,
    loading,
    error,
    fetchPosts,
    fetchPostDetail,
    createPost,
    updatePost,
    deletePost,
    createComment,
    updateComment,
    deleteComment,
    reactToPost,
    reactToComment,
  }
})
