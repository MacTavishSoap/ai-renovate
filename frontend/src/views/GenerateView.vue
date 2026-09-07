<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
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

const submitting = ref(false)

function onFileRead(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    form.imageUrl = e.target.result
  }
  reader.readAsDataURL(file.file)
}

async function onSubmit() {
  if (!form.style) return showToast('请选择风格')
  if (!form.roomType) return showToast('请选择房间类型')

  submitting.value = true
  try {
    await createGeneration({
      type: form.type,
      input_image_url: form.imageUrl || null,
      style: form.style,
      room_type: form.roomType,
      work_type: form.workType || null,
      extra_prompt: form.extraPrompt || null,
    })
    showToast('生成任务已提交')
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
    <header class="page-header">
      <h1 class="page-title">生成效果图</h1>
      <div class="credits">
        <span class="credits-num">{{ userStore.credits }}</span>
        <span class="credits-label">积分</span>
      </div>
    </header>

    <!-- 上传区 -->
    <section class="section">
      <h2 class="section-title">上传房间照片</h2>
      <div class="upload-area">
        <div v-if="form.imageUrl" class="preview-wrap">
          <img :src="form.imageUrl" alt="预览" class="preview-img" />
          <button class="reupload-btn" @click="form.imageUrl = ''">重新上传</button>
        </div>
        <label v-else class="upload-trigger">
          <input type="file" accept="image/*" class="file-hidden" @change="(e) => e.target.files[0] && onFileRead({ file: e.target.files[0] })" />
          <div class="upload-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
            </svg>
            <span>点击上传照片</span>
          </div>
        </label>
      </div>
    </section>

    <!-- 生成类型 -->
    <section class="section">
      <h2 class="section-title">生成类型</h2>
      <div class="chip-row">
        <button
          v-for="t in [{ v: 'effect', l: '效果图' }, { v: 'pano', l: '全景图' }]"
          :key="t.v"
          :class="['chip', { active: form.type === t.v }]"
          @click="form.type = t.v"
        >{{ t.l }}</button>
      </div>
    </section>

    <!-- 风格选择 -->
    <section class="section">
      <h2 class="section-title">装修风格</h2>
      <div class="chip-row">
        <button
          v-for="s in STYLES"
          :key="s"
          :class="['chip', { active: form.style === s }]"
          @click="form.style = s"
        >{{ s }}</button>
      </div>
    </section>

    <!-- 房间类型 -->
    <section class="section">
      <h2 class="section-title">房间类型</h2>
      <div class="chip-row">
        <button
          v-for="r in ROOM_TYPES"
          :key="r"
          :class="['chip', { active: form.roomType === r }]"
          @click="form.roomType = r"
        >{{ r }}</button>
      </div>
    </section>

    <!-- 施工类型 -->
    <section class="section">
      <h2 class="section-title">施工类型</h2>
      <div class="chip-row">
        <button
          v-for="w in WORK_TYPES"
          :key="w"
          :class="['chip', { active: form.workType === w }]"
          @click="form.workType = form.workType === w ? '' : w"
        >{{ w }}</button>
      </div>
    </section>

    <!-- 额外要求 -->
    <section class="section">
      <h2 class="section-title">额外要求</h2>
      <textarea
        v-model="form.extraPrompt"
        class="textarea"
        placeholder="例如：增加落地窗、暖色调灯光..."
        rows="2"
      ></textarea>
    </section>

    <!-- 提交 -->
    <div class="submit-area">
      <button
        class="submit-btn"
        :disabled="submitting || !form.style || !form.roomType"
        @click="onSubmit"
      >
        <span v-if="submitting" class="btn-loading"></span>
        {{ submitting ? '提交中...' : '开始生成' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.generate-page {
  padding-bottom: var(--space-xl);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-md) var(--space-md);
}

.page-title {
  font-size: var(--text-h1);
  font-weight: 600;
  color: var(--text);
}

.credits {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.credits-num {
  font-size: var(--text-h2);
  font-weight: 600;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}

.credits-label {
  font-size: var(--text-caption);
  color: var(--text-muted);
}

.section {
  padding: 0 var(--space-md);
  margin-bottom: var(--space-lg);
}

.section-title {
  font-size: var(--text-body-sm);
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: var(--space-sm);
}

/* 上传区 */
.upload-area {
  width: 100%;
}

.preview-wrap {
  position: relative;
}

.preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: var(--radius-lg);
}

.reupload-btn {
  position: absolute;
  bottom: var(--space-sm);
  right: var(--space-sm);
  height: 32px;
  padding: 0 var(--space-md);
  font-size: var(--text-caption);
  color: #fff;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
}

.upload-trigger {
  display: flex;
  width: 100%;
  cursor: pointer;
}

.file-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  width: 100%;
  height: 120px;
  background: var(--surface);
  border: 1px dashed var(--divider);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  font-size: var(--text-body-sm);
  transition: border-color var(--duration-fast) var(--ease-out);
}

.upload-trigger:hover .upload-placeholder {
  border-color: var(--accent);
}

/* chip 选择器 */
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.chip {
  height: 36px;
  padding: 0 var(--space-md);
  font-size: var(--text-body-sm);
  font-family: var(--font-sans);
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--divider);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.chip:hover {
  border-color: var(--accent);
}

.chip.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.chip:active {
  transform: scale(0.96);
}

/* textarea */
.textarea {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-body);
  font-family: var(--font-sans);
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--divider);
  border-radius: var(--radius-md);
  resize: none;
  outline: none;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.textarea::placeholder {
  color: var(--text-placeholder);
}

.textarea:focus {
  border-color: var(--accent);
}

/* 提交 */
.submit-area {
  padding: var(--space-md);
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  width: 100%;
  height: var(--touch-target);
  font-size: var(--text-button);
  font-family: var(--font-sans);
  font-weight: 500;
  color: #fff;
  background: var(--accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out);
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-loading {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
