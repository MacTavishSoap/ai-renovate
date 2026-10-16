<script setup>
defineProps({ modelValue: Boolean, disabled: Boolean, label: String })
defineEmits(['update:modelValue'])
</script>

<template>
  <button type="button" class="sw" :class="{ 'is-on': modelValue }" role="switch"
          :aria-checked="modelValue" :aria-label="label" :disabled="disabled"
          @click="$emit('update:modelValue', !modelValue)">
    <i></i>
  </button>
</template>
