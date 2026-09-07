<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { createGeneration } from '@/api/generations'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const STYLES = ['北欧风', '日式', '现代简约', '工业风', '新中式', '轻奢', '美式', '法式']
const ROOM_TYPES = ['客厅', '卧室', '厨房', '卫生间', '书房', '阳台', '餐厅', '儿童房']
const WORK_TYPES = ['整装', '软装', '局部改造']

const form = reactive({
  type: 'effect',
  style: '',
  roomType: '',
  workType: '',
  extraPrompt: '',
  imageUrl: '',
})

const uploading = ref(false)
const submitting = ref(false)

// TODO: 接入真实上传（COS），当前占位
function onFileRead(file) {
  // 开发期：用本地 base64 预览
  const reader = new FileReader()
  reader.onload = (e) => {
    form.imageUrl = e.target.result
  }
  reader.readAsDataURL(file.file)
}

async function onSubmit() {
  if (!form.style) {
    showFailToast('请选择风格')
    return
  }
  if (!form.roomType) {
    showFailToast('请选择房间类型')
    return
  }

  submitting.value = true
  try {
    const res = await createGeneration({
      type: form.type,
      input_image_url: form.imageUrl || null,
      style: form.style,
      room_type: form.roomType,
      work_type: form.workType || null,
      extra_prompt: form.extraPrompt || null,
    })
    showSuccessToast('生成任务已提交')
    // 跳到历史页查看进度
    router.push('/history')
  } catch {
    /* http 拦截器已处理 */
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="generate-page">
    <van-nav-bar title="生成效果图" />

    <div class="credits-bar">
      <van-icon name="gold-coin-o" />
      <span>剩余积分：{{ userStore.credits }}</span>
    </div>

    <!-- 上传图片 -->
    <van-cell-group inset title="上传房间照片（可选）">
      <van-cell>
        <van-uploader
          :max-count="1"
          accept="image/*"
          :after-read="onFileRead"
          v-model="form.imageUrl"
          style="display: none;"
        />
        <div v-if="form.imageUrl" class="preview-img">
          <img :src="form.imageUrl" alt="预览" />
          <van-button size="small" plain type="danger" @click="form.imageUrl = ''">
            重新上传
          </van-button>
        </div>
        <van-uploader v-else :max-count="1" accept="image/*" :after-read="onFileRead" />
      </van-cell>
    </van-cell-group>

    <!-- 生成类型 -->
    <van-cell-group inset title="生成类型">
      <van-radio-group v-model="form.type" direction="horizontal">
        <van-radio name="effect">效果图</van-radio>
        <van-radio name="pano">全景图</van-radio>
      </van-radio-group>
    </van-cell-group>

    <!-- 风格选择 -->
    <van-cell-group inset title="装修风格">
      <van-grid :column-num="4" :border="false">
        <van-grid-item
          v-for="s in STYLES"
          :key="s"
          @click="form.style = s"
        >
          <div :class="['tag', { active: form.style === s }]">{{ s }}</div>
        </van-grid-item>
      </van-grid>
    </van-cell-group>

    <!-- 房间类型 -->
    <van-cell-group inset title="房间类型">
      <van-grid :column-num="4" :border="false">
        <van-grid-item
          v-for="r in ROOM_TYPES"
          :key="r"
          @click="form.roomType = r"
        >
          <div :class="['tag', { active: form.roomType === r }]">{{ r }}</div>
        </van-grid-item>
      </van-grid>
    </van-cell-group>

    <!-- 施工类型 -->
    <van-cell-group inset title="施工类型（可选）">
      <van-radio-group v-model="form.workType" direction="horizontal">
        <van-radio v-for="w in WORK_TYPES" :key="w" :name="w">{{ w }}</van-radio>
      </van-radio-group>
    </van-cell-group>

    <!-- 额外要求 -->
    <van-cell-group inset title="额外要求（可选）">
      <van-field
        v-model="form.extraPrompt"
        type="textarea"
        placeholder="例如：增加落地窗、暖色调灯光..."
        rows="2"
        autosize
      />
    </van-cell-group>

    <!-- 提交 -->
    <div class="submit-btn">
      <van-button
        type="primary"
        block
        round
        :loading="submitting"
        loading-text="提交中..."
        @click="onSubmit"
      >
        开始生成
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.generate-page {
  padding-bottom: 20px;
}

.credits-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 13px;
  color: #969799;
}

.preview-img {
  position: relative;
}

.preview-img img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
}

.tag {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  background: #f7f8fa;
  color: #646566;
  transition: all 0.2s;
}

.tag.active {
  background: #1989fa;
  color: #fff;
}

.submit-btn {
  padding: 16px;
}
</style>
