package com.pharmatools.inventario.data

import androidx.lifecycle.LiveData
import androidx.room.Dao
import kotlinx.coroutines.flow.Flow
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface ProductDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(product: Product)

    @Update
    suspend fun update(product: Product)

    @Delete
    suspend fun delete(product: Product)

    @Query("SELECT * FROM products ORDER BY name COLLATE NOCASE ASC")
    fun observeAll(): LiveData<List<Product>>

    @Query("SELECT * FROM products WHERE name LIKE '%' || :query || '%' OR code LIKE '%' || :query || '%' ORDER BY name COLLATE NOCASE ASC")
    fun observeSearch(query: String): LiveData<List<Product>>

    @Query("SELECT * FROM products WHERE code = :code ORDER BY name LIMIT 1")
    fun observeByCode(code: String): Flow<Product?>

    @Query("SELECT * FROM products WHERE code = :code LIMIT 1")
    suspend fun findByCode(code: String): Product?

    @Query("SELECT * FROM products WHERE quantity < minQuantity ORDER BY name COLLATE NOCASE ASC")
    fun observeLowStock(): LiveData<List<Product>>
}