export interface GetAllProductsParams {
  page: number
  category_id?: string
  sort?: string
  price?: string
}

export interface SearchParams {
  name: string
  page: number
}

export interface ProductData {
  id: string
  name: string
  image: string
  rating: string
  price: string
  description: string | null
}

export interface AllProductsData {
  total: number
  current: number
  pages: number
  data: Omit<ProductData, 'description'>[]
}

interface FeatureData {
  code: string
  name: string
  description: string
  type: string
  range: string
  comparable: string
  featureUnit: string
  featureValues: {
    value: string
  }[]
  mandatory: string
  keyAttribute: string
  merchantVisible: string
  position: string
  visible: string
  multiValued: string
}

export interface CharacteristicsData {
  code: string
  name: string
  features: FeatureData[]
  position: number
}

export interface ProductSupplierData {
  id: number
  name: string
  price: number
  rating: number
}

interface SearchProductData {
  id: string
  name: string
  rating: number
}

export interface SearchData {
  next: string
  data: SearchProductData[]
}

export interface CategoryData {
  id: string
  name: string
  code: string
  children?: CategoryData[]
}

type Item = { id: string; name: string }

type SortData = Item
type PriceData = Item

export interface FiltersData {
  sort: SortData[]
  price: PriceData[]
}
