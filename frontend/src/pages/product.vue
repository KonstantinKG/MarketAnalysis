<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import MarketAnalysisService from 'src/api'
import { type CharacteristicsData, ProductData, type ProductSupplierData } from 'src/api/types'

const router = useRouter()
const route = useRoute()

const id = computed(() => route.params.id as string)
const tab = ref('suppliers')
const product = ref<ProductData>({
  id: '',
  name: '',
  image: '',
  rating: '',
  price: '',
  description: ''
})
const suppliers = ref<ProductSupplierData[]>([])
const characteristics = ref<CharacteristicsData[]>([])

async function fetchProduct() {
  try {
    const { data } = await MarketAnalysisService.getById(id.value)
    product.value = data
  } catch (e) {
    console.error(e)
  }
}

async function fetchSuppliers() {
  try {
    const { data } = await MarketAnalysisService.getProductSuppliers(id.value)
    suppliers.value = data
  } catch (e) {
    console.error(e)
  }
}

async function fetchCharacteristics() {
  try {
    const { data } = await MarketAnalysisService.getCharacteristics(id.value)
    characteristics.value = data
  } catch (e) {
    console.error(e)
  }
}

fetchProduct()
fetchSuppliers()
fetchCharacteristics()
</script>

<template>
  <q-page>
    <q-btn class="q-mb-sm" icon="arrow_back" color="orange" no-caps @click="router.back()">
      Назад
    </q-btn>
    <div class="product">
      <q-img height="500px" fit="contain" :src="`/example.jpg`" />
      <div class="product__content">
        <div class="title">{{ product.name }}</div>
        <q-rating
          v-model="product.rating"
          icon="star_border"
          icon-selected="star"
          icon-half="star_half"
          size="2em"
          color="orange"
          readonly
        />
        <div class="price">
          <span class="text-grey-4">Цена - </span>
          <b>{{ Number(product.price).toLocaleString('RU-ru') }}₸</b>
        </div>
      </div>
    </div>
    <q-tabs active-bg-color="grey-9" v-model="tab" indicator-color="transparent" align="left">
      <q-tab name="suppliers" label="Продавцы" />
      <q-tab name="characteristics" label="Характеристики" />
      <q-tab v-if="product.description" name="description" label="Описание" />
    </q-tabs>
    <q-tab-panels v-model="tab">
      <q-tab-panel name="suppliers">
        <div v-for="supplier in suppliers" :key="supplier.id" class="supplier">
          <span>{{ supplier.name }}</span>
          <q-rating v-model="supplier.rating" size="2em" color="orange" readonly />
          <span class="supplier__price">{{ Number(product.price).toLocaleString('RU-ru') }}₸</span>
        </div>
      </q-tab-panel>
      <q-tab-panel name="characteristics">
        <div class="characteristics-title">Характеристики {{ product.name }}</div>
        <div
          v-for="characteristic in characteristics"
          :key="characteristic.code"
          class="characteristics"
        >
          <div class="characteristics__name">{{ characteristic.name }}</div>
          <div class="characteristics__content">
            <div
              v-for="feature in characteristic.features"
              :key="feature.code"
              class="characteristics__values"
            >
              <span class="characteristics__values-title">{{ feature.name }}</span>
              &#8212
              <span>
                {{
                  feature.featureValues[0].value === 'true' ? 'Да' : feature.featureValues[0].value
                }}
              </span>
            </div>
          </div>
        </div>
      </q-tab-panel>
      <q-tab-panel v-if="product.description" name="description">
        <div v-html="product.description" />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<style scoped lang="scss">
.product {
  display: flex;

  .q-img {
    border: 1px solid $grey-9;
  }

  &__content {
    flex: 0 0 300px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
    border-top: 1px solid $grey-9;
    border-bottom: 1px solid $grey-9;
    border-right: 1px solid $grey-9;

    .title {
      font-size: 24px;
      font-weight: 700;

      &::first-letter {
        text-transform: uppercase;
      }
    }

    .price {
      font-size: 16px;
    }
  }
}

.q-tabs {
  margin: 20px 0;
}

.characteristics-title {
  font-weight: 700;
  font-size: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid $grey;
}

.characteristics {
  display: flex;
  gap: 30px;

  &:not(:first-child) {
    margin-top: 20px;
  }

  & > div {
    padding-bottom: 20px;
    border-bottom: 1px solid $grey;
  }

  &__name {
    flex-basis: 25%;
    font-size: 16px;
    font-weight: 600;
  }

  &__content {
    flex: 1 1 auto;
  }

  &__values {
    display: flex;
    gap: 10px;
  }
}

.supplier {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid $grey;

  &:not(:last-child) {
    margin-bottom: 10px;
  }

  & > * {
    flex: 0 1 33.333%;
  }

  &__price {
    text-align: right;
  }
}
</style>
