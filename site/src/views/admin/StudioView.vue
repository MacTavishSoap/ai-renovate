<script setup>
import { computed } from 'vue'
import Icon from '../../components/admin/Icon.vue'
import { getEffectItemThumbUrl, getThumbUrl } from '@frontend/api/pano'
import { can, me, perms, toast } from '../../admin/store'

const roleBlocked = computed(() => !perms[me.value.role]['studio.enter'])

// 生图流程:用项目里真实的图来示意 户型图 → 3D 户型图 → 全景图
const steps = [
  { t: '户型图', src: getEffectItemThumbUrl('effect_reference.jpg') },
  { t: '3D 户型图', src: getEffectItemThumbUrl('effect_front.jpg') },
  { t: '360° 全景图', src: getThumbUrl({ levels: { thumb: 'livingroom_thumb.jpg' } }) },
]

const soon = () => toast('AI 生图页面建设中,入口已就绪')
</script>

<template>
  <section v-if="can('studio.enter')" class="ad-studio">
    <ol class="ad-studio__flow" aria-label="生图流程">
      <li v-for="s in steps" :key="s.t">
        <img :src="s.src" :alt="s.t" />
        <span>{{ s.t }}</span>
      </li>
    </ol>
    <div class="ad-studio__cta">
      <button type="button" class="ad-btn" @click="soon"><Icon name="cube" />进入 AI 生图</button>
      <em class="ad-chip">建设中</em>
    </div>
  </section>

  <section v-else class="ad-locked">
    <Icon name="lock" />
    <h2>你暂时不能使用 AI 生图</h2>
    <p>{{ roleBlocked ? `「${me.role}」这个角色还没有开通` : '请管理员为你开通' }}</p>
    <RouterLink class="ad-btn ad-btn--ghost" :to="roleBlocked ? '/admin/permissions' : '/admin/staff'">
      去{{ roleBlocked ? '权限管理' : '员工列表' }}
    </RouterLink>
  </section>
</template>
