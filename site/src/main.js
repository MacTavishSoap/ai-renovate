import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles.css'
import './admin.css'

document.documentElement.classList.add('js')
createApp(App).use(router).mount('#app')
