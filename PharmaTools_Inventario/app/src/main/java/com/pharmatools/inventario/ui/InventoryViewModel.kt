package com.pharmatools.inventario.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.pharmatools.inventario.data.Product
import com.pharmatools.inventario.data.ProductRepository
import kotlinx.coroutines.launch

class InventoryViewModel(private val repository: ProductRepository) : ViewModel() {

    val products = repository.products

    fun search(query: String) = repository.search(query)

    fun saveProduct(code: String, name: String, category: String, qty: Int, min: Int, price: Double) {
        viewModelScope.launch {
            repository.save(
                Product(
                    code = code,
                    name = name,
                    category = category,
                    quantity = qty,
                    minQuantity = min,
                    price = price
                )
            )
        }
    }

    fun deleteProduct(code: String) {
        viewModelScope.launch {
            repository.findByCode(code)?.let { repository.delete(it) }
        }
    }

    class Factory(private val repository: ProductRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T =
            if (modelClass.isAssignableFrom(InventoryViewModel::class.java)) {
                InventoryViewModel(repository) as T
            } else {
                throw IllegalArgumentException("Unknown ViewModel class")
            }
    }
}