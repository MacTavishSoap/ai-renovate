<script setup>
import { computed } from 'vue'
import Icon from '../../components/admin/Icon.vue'
import { can, me, perms, toast } from '../../admin/store'

const roleBlocked = computed(() => !perms[me.value.role]['studio.enter'])

const tiles = [
  { t: '户型生图', d: '由户型图与风格词生成空间效果' },
  { t: '风格迁移', d: '在既有空间上切换风格与材质' },
  { t: '材质替换', d: '局部更换家具、墙面与灯光' },
]

const soon = () => toast('功能页面建设中 · 入口已就绪,待后续接入')
</script>

<template>
  <section v-if="can('studio.enter')" class="ad-studio">
    <div class="ad-studio__hero">
      <div class="ad-studio__fl" aria-hidden="true"></div>
      <div class="ad-studio__txt">
        <p class="ad-label">PLACEHOLDER</p>
        <h2 class="fluted-text">生图工坊</h2>
        <p>基于生图的功能页面入口。当前仅保留入口位置,界面与能力将在后续接入;产出的资产会自动归入「资产合集」。</p>
        <button type="button" class="ad-btn" @click="soon"><Icon name="cube" />进入工坊</button>
      </div>
    </div>

    <ul class="ad-studio__tiles">
      <li v-for="(t, i) in tiles" :key="t.t">
        <button type="button" @click="soon">
          <span class="ad-studio__no">0{{ i + 1 }}</span>
          <strong>{{ t.t }}</strong>
          <small>{{ t.d }}</small>
          <em class="ad-chip">待接入</em>
        </button>
      </li>
    </ul>
  </section>

  <section v-else class="ad-locked">
    <Icon name="lock" />
    <h2>暂未开放</h2>
    <p v-if="roleBlocked">角色「{{ me.role }}」未被授权使用功能页面。请管理员在「权限管理」中为该角色开启「进入功能页面」。</p>
    <p v-else>你的账号尚未被单独开通功能页面。请管理员在「员工列表」中为「{{ me.name }}」开通。</p>
    <RouterLink class="ad-btn ad-btn--ghost" :to="roleBlocked ? '/admin/permissions' : '/admin/staff'">
      前往{{ roleBlocked ? '权限管理' : '员工列表' }}
    </RouterLink>
  </section>
</template>
