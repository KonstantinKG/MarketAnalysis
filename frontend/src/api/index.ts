import { api } from 'boot/axios'
import { AxiosResponse } from 'axios'
import type {
  GetAllProductsParams,
  AllProductsData,
  ProductData,
  CharacteristicsData,
  ProductSupplierData,
  SearchParams,
  SearchData,
  CategoryData,
  FiltersData
} from './types'

type PromiseResponse<T> = Promise<{ data: T }>

class MarketAnalysisService {
  private readonly RESOURCE = 'get'

  getData = <T>(response: AxiosResponse<T>) => response.data

  async getAll(params: GetAllProductsParams): PromiseResponse<AllProductsData> {
    return await api.get(`${this.RESOURCE}/products`, { params }).then(this.getData)
  }

  async getById(id: string): PromiseResponse<ProductData> {
    return await api.get(`${this.RESOURCE}/product`, { params: { id } }).then(this.getData)
  }

  async getCharacteristics(product_id: string): PromiseResponse<CharacteristicsData> {
    return await api
      .get(`${this.RESOURCE}/product/characteristics`, { params: { product_id } })
      .then(this.getData)
  }

  async getProductSuppliers(product_id: string): PromiseResponse<ProductSupplierData[]> {
    return await api
      .get(`${this.RESOURCE}/product/suppliers`, { params: { product_id } })
      .then(this.getData)
  }

  async searchProducts(params: SearchParams): PromiseResponse<SearchData> {
    return await api.get('search/products', { params }).then(this.getData)
  }

  async getCategories(id?: string): PromiseResponse<CategoryData> {
    return await api.get(`${this.RESOURCE}/categories`, { params: { id } }).then(this.getData)
  }

  async getFilters(): PromiseResponse<FiltersData> {
    return await api.get(`${this.RESOURCE}/filters`).then(this.getData)
  }
}

export default new MarketAnalysisService()
