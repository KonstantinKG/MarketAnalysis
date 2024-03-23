<script setup lang="ts">
import MarketAnalysisService from 'src/api'
import { AllProductsData, CategoryData, FiltersData } from 'src/api/types'
import { ref, watch } from 'vue'
import { FILES_PATH } from 'src/constants'

const products = ref<AllProductsData>({
  total: 0,
  pages: 1,
  current: 1,
  data: []
})
const filters = ref<FiltersData>({
  sort: [],
  price: []
})
const search = ref('')
const categories = ref<CategoryData[]>([])
const page = ref(1)
const category = ref<string | string[]>([])
const sort = ref<string>('relevance')
const price = ref<string | undefined>(undefined)
const isLoading = ref(false)
const isLoadingMore = ref(false)

async function fetchAllProducts(loadMore = false) {
  try {
    if (!loadMore) isLoading.value = true
    const { data } = await MarketAnalysisService.getAll({
      page: page.value,
      category_id: category.value as string,
      sort: sort.value,
      price: price.value
    })
    if (data.current > 1) {
      products.value.current = data.current
      products.value.total = data.total
      products.value.data = products.value.data.concat(data.data)
    } else {
      products.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

async function searchProducts() {
  try {
    isLoading.value = true
    const { data } = await MarketAnalysisService.searchProducts({
      name: search.value,
      page: page.value
    })
    if (data.current > 1) {
      products.value.current = data.current
      products.value.total = data.total
      products.value.data = products.value.data.concat(data.data)
    } else {
      products.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  isLoadingMore.value = true
  page.value++
  await fetchAllProducts(true)
  isLoadingMore.value = false
}

async function fetchCategories(id?: string) {
  try {
    const { data } = await MarketAnalysisService.getCategories(id)
    if (categories.value.length) {
      const index = categories.value.findIndex((elem) => elem.id === id)
      categories.value[index].children = data
    } else {
      categories.value = data
      for (const item of data) {
        await fetchCategories(item.id)
      }
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchFilters() {
  try {
    const { data } = await MarketAnalysisService.getFilters()
    filters.value.sort = data.sort.map((el) => {
      return { label: el.name, value: el.id }
    })
    filters.value.price = data.price.map((el) => {
      return { label: el.name, value: el.id }
    })
  } catch (e) {
    console.error(e)
  }
}

function onSelectCategory(id: string) {
  category.value = id
}

watch([category, sort, price], async () => {
  page.value = 1
  await fetchAllProducts()
})

fetchAllProducts()
fetchFilters()
fetchCategories()
</script>

<template>
  <q-page>
    <div class="sidebar">
      <div class="categories">
        <div class="sidebar-title">Категории</div>
        <q-tree
          node-key="id"
          :nodes="categories"
          label-key="name"
          selected-color="orange"
          :selected="category"
          @update:selected="onSelectCategory"
        />
      </div>
      <div class="prices">
        <div class="sidebar-title">Цены</div>
        <q-option-group
          v-model="price"
          :options="[{ label: 'Все', value: undefined }, ...filters.price]"
          color="primary"
        />
      </div>
    </div>
    <div class="content relative-position">
      <q-input
        v-model="search"
        clearable
        filled
        label="Искать по названию"
        class="content__search"
        @keyup.enter="searchProducts"
        @clear="fetchAllProducts"
      >
        <template #prepend>
          <q-icon name="search" />
        </template>
      </q-input>
      <div class="content__header">
        <div class="title">Всего найдено товаров: {{ products.total }}</div>
        <q-select
          v-model="sort"
          style="flex-basis: 250px"
          :options="filters.sort"
          label="Сортировать по"
          filled
          emit-value
          map-options
          clearable
        />
      </div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div v-if="!isLoading" class="content__cards">
          <div v-for="product in products.data" :key="product.id" class="content__card">
            <div class="product-image">
              <q-img fit="contain" height="200px" :src="`${FILES_PATH}${product.image}`" />
            </div>
            <router-link :to="{ name: 'Product', params: { id: product.id } }">
              <div class="product-name">{{ product.name }}</div>
            </router-link>
            <q-rating
              v-model="product.rating"
              icon="star_border"
              icon-selected="star"
              icon-half="star_half"
              size="2em"
              color="orange"
              readonly
            />
            <div>
              <span class="text-grey-4">Цена - </span>
              <b>{{ Number(product.price).toLocaleString('RU-ru') }}₸</b>
            </div>
          </div>
        </div>
      </transition>
      <q-inner-loading :showing="isLoading">
        <q-spinner-dots size="xl" color="primary" />
      </q-inner-loading>
      <div class="row justify-center q-mt-md">
        <q-btn
          v-if="products.current < products.pages && !isLoading"
          :loading="isLoadingMore"
          outline
          padding="sm xl"
          color="orange"
          @click="loadMore"
        >
          Показать еще
        </q-btn>
      </div>
    </div>
  </q-page>
</template>

<style scoped lang="scss">
.q-page {
  display: flex;
  gap: 20px;
}

.sidebar {
  flex: 0 0 240px;
  display: flex;
  flex-direction: column;
  gap: 20px;

  .categories {
    padding-bottom: 20px;
    border-bottom: 1px solid $grey-9;
  }

  &-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 10px;
  }
}

.content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-weight: 700;
      font-size: 24px;
    }
  }

  &__cards {
    display: flex;
    flex-wrap: wrap;
  }

  &__card {
    flex: 0 1 33.333%;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
    border: 1px solid $grey-9;

    .product-image {
      padding-bottom: 10px;
      border-bottom: 1px solid $grey-9;
    }

    .product-name::first-letter {
      text-transform: uppercase;
    }
  }
}
</style>
