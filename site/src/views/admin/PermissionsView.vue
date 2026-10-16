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
// 没有"使用 AI 生图页面"时,"发起生图"没有意义,淡显
const dim = (r, c) => c.key === 'studio.generate' && !perms[r]['studio.enter']

function set(r, c, v) {
  perms[r][c.key] = v
  toast(`${r}:${c.label} 已${v ? '开启' : '关闭'}`)
}
</script>

<template>
  <section class="ad-perm">
    <div class="ad-perm__main">
      <p v-if="!isAdmin" class="ad-banner"><Icon name="lock" />仅管理员可以修改,当前为只读</p>

      <div class="ad-tablewrap">
        <table class="ad-table ad-matrix">
          <thead>
            <tr>
              <th>谁可以…</th>
              <th v-for="r in ROLES" :key="r" class="ctr">{{ r }}</th>
            </tr>
          </thead>
          <tbody v-for="grp in groups" :key="grp.g">
            <tr class="ad-matrix__g"><td :colspan="ROLES.length + 1">{{ grp.g }}</td></tr>
            <tr v-for="c in grp.items" :key="c.key">
              <td>{{ c.label }}</td>
              <td v-for="r in ROLES" :key="r" class="ctr" :class="{ 'is-dim': dim(r, c) }">
                <Switch :model-value="perms[r][c.key]" :label="`${r}:${c.label}`" :disabled="locked(r)"
                        @update:model-value="set(r, c, $event)" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <aside class="ad-perm__side">
      <section class="ad-panel">
        <h3 class="ad-panel__t">{{ me.name }} <small>{{ me.role }}</small></h3>
        <ul class="ad-can">
          <li v-for="c in CAPS" :key="c.key" :class="{ 'is-on': can(c.key) }">
            <Icon :name="can(c.key) ? 'check' : 'close'" />{{ c.label }}
          </li>
        </ul>
      </section>
    </aside>
  </section>
</template>
