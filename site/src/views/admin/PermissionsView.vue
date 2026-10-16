<script setup>
import { computed } from 'vue'
import Switch from '../../components/admin/Switch.vue'
import Icon from '../../components/admin/Icon.vue'
import { CAPS, can, me, perms, ROLES, toast } from '../../admin/store'

const isAdmin = computed(() => me.value.role === '管理员')

const groups = computed(() =>
  [...new Set(CAPS.map((c) => c.group))].map((g) => ({ g, items: CAPS.filter((c) => c.group === g) })),
)

const locked = (r) => !isAdmin.value || r === '管理员'
// 没有"进入功能页面"时,"发起生图"没有意义
const dim = (r, c) => c.key === 'studio.generate' && !perms[r]['studio.enter']

function set(r, c, v) {
  perms[r][c.key] = v
  toast(`${r} · ${c.label}:${v ? '已开启' : '已关闭'}`)
}
</script>

<template>
  <section class="ad-perm">
    <div class="ad-perm__main">
      <p v-if="!isAdmin" class="ad-banner"><Icon name="lock" />仅管理员可修改权限,当前为只读。</p>

      <div class="ad-tablewrap">
        <table class="ad-table ad-matrix">
          <thead>
            <tr>
              <th>能力</th>
              <th v-for="r in ROLES" :key="r" class="ctr">
                {{ r }}<small>{{ r === '业务人员' ? '前台使用' : r === '管理员' ? '全部开启' : '内部制作' }}</small>
              </th>
            </tr>
          </thead>
          <tbody v-for="grp in groups" :key="grp.g">
            <tr class="ad-matrix__g"><td :colspan="ROLES.length + 1">{{ grp.g }}</td></tr>
            <tr v-for="c in grp.items" :key="c.key">
              <td>
                <strong>{{ c.label }}</strong>
                <p class="ad-hint">{{ c.hint }}</p>
              </td>
              <td v-for="r in ROLES" :key="r" class="ctr" :class="{ 'is-dim': dim(r, c) }">
                <Switch :model-value="perms[r][c.key]" :label="`${r} ${c.label}`" :disabled="locked(r)"
                        @update:model-value="set(r, c, $event)" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="ad-note">「管理员」永远拥有全部能力,避免误操作把自己锁在门外。</p>
    </div>

    <aside class="ad-perm__side">
      <section class="ad-panel">
        <h3 class="ad-panel__t">当前身份能做什么 <small>{{ me.name }} · {{ me.role }}</small></h3>
        <ul class="ad-can">
          <li v-for="c in CAPS" :key="c.key" :class="{ 'is-on': can(c.key) }">
            <Icon :name="can(c.key) ? 'check' : 'close'" />{{ c.label }}
          </li>
        </ul>
        <p v-if="perms[me.role]['studio.enter'] && !me.studio" class="ad-hint">
          该角色可以进入功能页面,但员工「{{ me.name }}」尚未被单独开通。
        </p>
      </section>
    </aside>
  </section>
</template>
