<template>
  <img
    :src="src"
    :alt="alt"
    :class="imgClass"
    :style="imgStyle"
    @error="onError"
  />
</template>

<script setup>
import { handleImageError } from '@/composables/useCardUtils'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  imgClass: {
    type: String,
    default: 'img-fluid'
  },
  imgStyle: {
    type: [String, Object],
    default: ''
  },
  placeholderSize: {
    type: String,
    default: '300x200'
  }
})

function onError(event) {
  handleImageError(event, props.placeholderSize)
}
</script>
