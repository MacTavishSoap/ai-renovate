<script setup>
import { computed, ref } from 'vue'
import Switch from '../../components/admin/Switch.vue'
import Modal from '../../components/admin/Modal.vue'
import Icon from '../../components/admin/Icon.vue'
import { addStaff, customers, me, ROLES, staff, studioState, toast } from '../../admin/store'

const isAdmin = computed(() => me.value.role === '管理员')
const owned = (id) => customers.filter((c) => c.ownerId === id).length

function setStudio(s, v) {
  s.studio = v
  toast(`${s.name}${v ? '已开通' : '已关闭'} AI 生图`)
}
function setRole(s, e) {
  s.role = e.target.value
  toast(`${s.name} 已改为「${s.role}」`)
}

const showAdd = ref(false)
const name = ref('')
const role = ref('业务人员')
const err = ref('')

function openAdd() {
  name.value = ''
  role.value = '业务人员'
  err.value = ''
  showAdd.value = true
}
function submit() {
  const n = name.value.trim()
  if (!n) { err.value = '请填写员工姓名'; return }
  if (staff.some((s) => s.name === n)) { err.value = '已有同名员工'; return }
  addStaff(n, role.value)
  showAdd.value = false
  toast(`已添加员工「${n}」`)
}
</script>

<template>
  <section>
    <div class="ad-bar">
      <p class="ad-count">共 <b>{{ staff.length }}</b> 位员工</p>
      <button v-if="isAdmin" type="button" class="ad-btn" @click="openAdd"><Icon name="plus" />添加员工</button>
      <span v-else class="ad-lock"><Icon name="lock" />仅管理员可修改</span>
    </div>

    <div class="ad-tablewrap">
      <table class="ad-table">
        <thead>
          <tr>
            <th>员工</th><th>角色</th><th>AI 生图</th><th class="num">名下客户</th><th class="num">已生图</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id" :class="{ 'is-me': s.id === me.id }">
            <td>
              <span class="ad-who"><span class="ad-avatar">{{ s.name[0] }}</span>{{ s.name }}<em v-if="s.id === me.id" class="ad-chip">当前身份</em></span>
            </td>
            <td>
              <select class="ad-select ad-select--cell" :value="s.role" :disabled="!isAdmin || s.id === me.id"
                      :aria-label="`${s.name} 的角色`" @change="setRole(s, $event)">
                <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
              </select>
            </td>
            <td>
              <span class="ad-switchcell">
                <Switch :model-value="s.studio" :label="`${s.name} 使用 AI 生图`"
                        :disabled="!isAdmin || studioState(s) === 'role'" @update:model-value="setStudio(s, $event)" />
                <em :class="`is-${studioState(s)}`">{{ { on: '已开通', off: '未开通', role: '该角色未授权' }[studioState(s)] }}</em>
              </span>
            </td>
            <td class="num">{{ owned(s.id) }}</td>
            <td class="num">{{ s.gens }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-if="showAdd" title="添加员工" @close="showAdd = false">
      <label class="ad-field">
        <span>姓名</span>
        <input v-model="name" class="ad-input" maxlength="8" placeholder="员工姓名" autofocus @input="err = ''" @keydown.enter="submit" />
        <em v-if="err" class="ad-err">{{ err }}</em>
      </label>
      <label class="ad-field">
        <span>角色</span>
        <select v-model="role" class="ad-select"><option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option></select>
      </label>
      <template #foot>
        <button type="button" class="ad-btn ad-btn--ghost" @click="showAdd = false">取消</button>
        <button type="button" class="ad-btn" @click="submit">添加</button>
      </template>
    </Modal>
  </section>
</template>
