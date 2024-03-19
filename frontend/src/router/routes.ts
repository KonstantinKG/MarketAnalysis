import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/default.vue'),
    redirect: '/products',
    children: [
      { path: '/products', component: () => import('pages/main.vue') },
      {
        path: '/products/:id',
        name: 'Product',
        component: () => import('pages/product.vue')
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/error-page.vue')
  }
]

export default routes
