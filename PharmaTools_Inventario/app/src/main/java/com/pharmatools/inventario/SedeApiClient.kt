package com.pharmatools.inventario

import com.google.gson.Gson
import com.google.gson.JsonArray
import com.google.gson.JsonObject
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException
import java.util.concurrent.TimeUnit

class SedeApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()

    @Throws(IOException::class)
    fun obtenerSedes(): List<Sede> {
        val request = Request.Builder().url(BASE_URL).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Error HTTP: ${response.code}")
            val json = response.body?.string() ?: return emptyList()
            val jsonArray: JsonArray = gson.fromJson(json, JsonArray::class.java)
            val sedes = mutableListOf<Sede>()
            for (i in 0 until jsonArray.size()) {
                val obj = jsonArray.get(i).asJsonObject
                sedes.add(
                    Sede(
                        obj.get("nombre").asString,
                        obj.get("ciudad").asString,
                        obj.get("id_sucursal_ext").asString.trim(),
                        obj.get("servidorId").asInt
                    )
                )
            }
            return sedes
        }
    }

    data class Sede(
        val nombre: String,
        val ciudad: String,
        val idSucursal: String,
        val servidorId: Int
    )

    companion object {
        private const val BASE_URL = "https://citasprevimedicaidb.com:3276/api/Sucursal/ListarSedesCiudad/"
    }
}
