// src/plugins/element-plus.js
import { defineNuxtPlugin } from 'nuxt/app'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.use(ElementPlus)
})