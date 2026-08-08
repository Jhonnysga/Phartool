package com.pharmatools.inventario

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.JsonArray
import com.google.gson.JsonObject
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException
import java.util.concurrent.TimeUnit

class ApiClient(context: Context) {
    private val context = context.applicationContext
    private val client = OkHttpClient.Builder()
        .connectTimeout(120, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()

    private fun getPrefs(): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private fun getCoAlma(): String =
        getPrefs().getString(KEY_CO_ALMA, "02") ?: "02"

    private fun getServidorId(): Int =
        getPrefs().getInt(KEY_SERVIDOR_ID, 1)

    @Throws(IOException::class)
    fun obtenerTodosProductos(): List<Producto> {
        val url = "$BASE_URL?page=1&perPage=10000&co_alma=${getCoAlma()}&servidorId=${getServidorId()}"
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Error HTTP: ${response.code}")
            val json = response.body?.string() ?: return emptyList()
            val root = gson.fromJson(json, JsonObject::class.java)
            val list = root.getAsJsonObject("result").getAsJsonArray("list")
            return (0 until list.size()).mapNotNull { i ->
                val item = list.get(i).asJsonObject
                Producto(
                    item.get("ref").asString,
                    item.get("art_des").asString,
                    item.get("prec_vta_usd").asDouble
                )
            }
        }
    }

    @Throws(IOException::class)
    fun obtenerProductoPorRef(ref: String): Producto? {
        val url = "$BASE_URL?page=1&perPage=1&filter=$ref&co_alma=${getCoAlma()}&servidorId=${getServidorId()}"
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) return null
            val json = response.body?.string() ?: return null
            val root = gson.fromJson(json, JsonObject::class.java)
            if (root.get("succeeded").asBoolean) {
                val list = root.getAsJsonObject("result").getAsJsonArray("list")
                if (list.size() > 0) {
                    val item = list.get(0).asJsonObject
                    return Producto(
                        item.get("ref").asString,
                        item.get("art_des").asString,
                        item.get("prec_vta_usd").asDouble
                    )
                }
            }
            return null
        }
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_CO_ALMA = "co_alma"
        private const val KEY_SERVIDOR_ID = "servidor_id"
        private const val BASE_URL = "https://citasprevimedicaidb.com:3276/api/Art/"
    }
}
