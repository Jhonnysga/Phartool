package com.pharmatools.inventario.data

import androidx.lifecycle.LiveData
import kotlinx.coroutines.flow.Flow

class ProductRepository(private val dao: ProductDao) {

    val products: LiveData<List<Product>> = dao.observeAll()

    fun search(query: String): LiveData<List<Product>> =
        if (query.isBlank()) dao.observeAll() else dao.observeSearch(query.trim())

    fun lowStock(): LiveData<List<Product>> = dao.observeLowStock()

    fun product(code: String): Flow<Product?> = dao.observeByCode(code)

    suspend fun save(product: Product) = dao.upsert(product)

    suspend fun delete(product: Product) = dao.delete(product)

    suspend fun findByCode(code: String): Product? = dao.findByCode(code)
}