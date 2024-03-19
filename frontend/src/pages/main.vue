<script setup lang="ts">
import MarketAnalysisService from 'src/api'
import { AllProductsData, CategoryData, FiltersData } from 'src/api/types'
import { ref, watch } from 'vue'

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
const subCategories = ref<CategoryData[]>([])
const page = ref(1)
const category = ref<string>([])
const selectCategory = ref('')
const sort = ref<string>('relevance')
const price = ref<string>()
const isLoading = ref(false)
const isLoadingMore = ref(false)

async function fetchAllProducts(loadMore = false) {
  try {
    if (!loadMore) isLoading.value = true
    const { data } = await MarketAnalysisService.getAll({
      page: page.value,
      category_id: category.value,
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
    }
    // for (const category of categories.value) {
    //   category.children = [{ value: '123455', label: 'fw' }]
    // }
    // categories.value[0].children = data
    // if (id) {
    //   subCategories.value = data
    // } else {
    //   categories.value = data.map((el) => {
    //     return { label: el.name, value: el.id }
    //   })
    // }
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
  console.log(id)
  category.value = id
  fetchCategories(id)
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
    <div class="categories">
      <q-tree
        node-key="id"
        :nodes="categories"
        label-key="name"
        :selected="category"
        @update:selected="onSelectCategory"
      />
      <!--      <q-select-->
      <!--        class="categories__select"-->
      <!--        :model-value="selectCategory"-->
      <!--        :options="categories"-->
      <!--        label="Категории"-->
      <!--        filled-->
      <!--        emit-value-->
      <!--        map-options-->
      <!--        clearable-->
      <!--        @update:model-value="onSelectCategory"-->
      <!--      />-->
      <!--      <div v-for="(item, index) in subCategories" :key="index">-->
      <!--        <q-btn color="primary" @click="category = item.id">{{ item.name }}</q-btn>-->
      <!--      </div>-->
    </div>
    <q-select
      v-model="sort"
      :options="filters.sort"
      label="Сортировать по"
      filled
      emit-value
      map-options
      clearable
    />
    <q-input
      v-model="search"
      clearable
      filled
      label="Искать по названию"
      class="controls__search"
      @keyup.enter="searchProducts"
      @clear="fetchAllProducts"
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>
    <q-option-group v-model="price" :options="filters.price" color="primary" />
    <div class="title">Всего найдено товаров: {{ products.total }}</div>
    <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
      <div v-show="!isLoading" class="cards">
        <div v-for="product in products.data" :key="product.id" class="card">
          <q-img
            fit="contain"
            class="card__image"
            height="200px"
            :src="`/${product.image}`"
            alt=""
          />
          <router-link :to="{ name: 'Product', params: { id: product.id } }">
            {{ product.name }}
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
          <div>Цена - {{ Number(product.price).toLocaleString('RU-ru') }}₸</div>
        </div>
        <h5 v-if="!products.data.length && !isLoading">Не найдено мероприятий</h5>
      </div>
    </transition>
    <q-inner-loading :showing="isLoading">
      <q-spinner-hourglass size="xl" color="primary" />
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
  </q-page>
</template>

<style scoped lang="scss">
.title {
  font-weight: 700;
  font-size: 24px;
  margin-bottom: 20px;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;

  &__select {
    width: 250px;
  }
}

.cards {
  display: flex;
  flex-wrap: wrap;
}

.card {
  padding: 10px;
  flex: 0 1 33.333%;
  border: 1px solid $grey-3;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
