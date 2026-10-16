<script setup>
import { ref } from 'vue'
import Modal from './Modal.vue'
import Switch from './Switch.vue'
import { addCustomer, can, customers, maskName, toast } from '../../admin/store'

const emit = defineEmits(['close', 'done'])

const name = ref('')
const priv = ref(true)
const err = ref('')

function submit() {
  const n = name.value.trim()
  if (!n) { err.value = '请填写客户名称'; return }
  if (customers.some((c) => c.name === n)) { err.value = '该客户已存在'; return }
  // 没有"设置隐私"权限时,新客户默认隐私化
  const c = addCustomer(n, can('customer.privacy') ? priv.value : true)
  toast(`已加入客户「${n}」`)
  emit('done', c)
  emit('close')
}
</script>

<template>
  <Modal title="加入所属客户" @close="emit('close')">
    <label class="ad-field">
      <span>客户名称</span>
      <input v-model="name" class="ad-input" placeholder="例如:王思远" maxlength="12" autofocus
             @input="err = ''" @keydown.enter="submit" />
      <em v-if="err" class="ad-err">{{ err }}</em>
    </label>

    <div class="ad-row ad-row--box">
      <div>
        <strong>客户隐私化</strong>
        <p class="ad-hint">开启后,公共演示中显示为 {{ maskName(name.trim() || '王思远') }}</p>
      </div>
      <Switch v-model="priv" label="客户隐私化" :disabled="!can('customer.privacy')" />
    </div>
    <p v-if="!can('customer.privacy')" class="ad-hint">当前身份无「设置客户隐私化」权限,新客户将默认隐私化。</p>

    <template #foot>
      <button type="button" class="ad-btn ad-btn--ghost" @click="emit('close')">取消</button>
      <button type="button" class="ad-btn" @click="submit">加入客户</button>
    </template>
  </Modal>
</template>
