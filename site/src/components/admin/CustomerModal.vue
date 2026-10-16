<script setup>
import { ref } from 'vue'
import Modal from './Modal.vue'
import Switch from './Switch.vue'
import Icon from './Icon.vue'
import { addCustomer, can, customers, maskName, toast } from '../../admin/store'

const emit = defineEmits(['close', 'done'])

const name = ref('')
const hide = ref(true)
const err = ref('')

function submit() {
  const n = name.value.trim()
  if (!n) { err.value = '请填写客户姓名'; return }
  if (customers.some((c) => c.name === n)) { err.value = '这位客户已经存在'; return }
  // 没有"隐藏姓名"权限时,新客户默认隐藏
  const c = addCustomer(n, can('customer.privacy') ? hide.value : true)
  toast(`已添加客户「${n}」`)
  emit('done', c)
  emit('close')
}
</script>

<template>
  <Modal title="添加客户" @close="emit('close')">
    <label class="ad-field">
      <span>客户姓名</span>
      <input v-model="name" class="ad-input" placeholder="例如:王思远" maxlength="12" autofocus
             @input="err = ''" @keydown.enter="submit" />
      <em v-if="err" class="ad-err">{{ err }}</em>
    </label>

    <div class="ad-row ad-row--box">
      <div>
        <strong>隐藏真实姓名</strong>
        <p class="ad-sub">对外显示为 <b class="ad-mono">{{ hide || !can('customer.privacy') ? maskName(name.trim() || '王思远') : (name.trim() || '王思远') }}</b></p>
      </div>
      <span v-if="!can('customer.privacy')" class="ad-lock"><Icon name="lock" />无权限</span>
      <Switch v-else v-model="hide" label="隐藏真实姓名" />
    </div>

    <template #foot>
      <button type="button" class="ad-btn ad-btn--ghost" @click="emit('close')">取消</button>
      <button type="button" class="ad-btn" @click="submit">添加</button>
    </template>
  </Modal>
</template>
