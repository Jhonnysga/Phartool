package com.pharmatools.inventario

import android.app.ProgressDialog
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var dbHelper: DatabaseHelper
    private lateinit var prefs: SharedPreferences
    private lateinit var tvUltimaActualizacion: TextView
    private lateinit var btnSincronizar: Button
    private lateinit var btnControl: Button
    private lateinit var btnDirecto: Button
    private lateinit var btnConfig: Button
    private val executor: ExecutorService = Executors.newSingleThreadExecutor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        dbHelper = DatabaseHelper(this)
        prefs = getSharedPreferences("PharmatoolsPrefs", MODE_PRIVATE)
        tvUltimaActualizacion = findViewById(R.id.tvUltimaActualizacion)
        btnSincronizar = findViewById(R.id.btnSincronizar)
        btnControl = findViewById(R.id.btnControlEtiquetado)
        btnDirecto = findViewById(R.id.btnEtiquetado)
        btnConfig = findViewById(R.id.btnConfiguracion)

        btnSincronizar.setOnClickListener { sincronizarProductos(true) }
        btnControl.setOnClickListener { startActivity(Intent(this, ControlEtiquetadoActivity::class.java)) }
        btnDirecto.setOnClickListener { startActivity(Intent(this, EtiquetadoDirectoActivity::class.java)) }
        btnConfig.setOnClickListener { startActivity(Intent(this, ConfiguracionActivity::class.java)) }

        mostrarUltimaActualizacion()
        if (dbHelper.getCantidadProductos() == 0) {
            sincronizarProductos(true)
        } else {
            val ultima = prefs.getLong("ultima_sincronizacion", 0)
            if (System.currentTimeMillis() - ultima > 24 * 60 * 60 * 1000) {
                sincronizarProductos(false)
            }
        }
    }

    private fun sincronizarProductos(mostrarDialogo: Boolean) {
        val progress: ProgressDialog? = if (mostrarDialogo) {
            ProgressDialog(this).apply {
                setTitle("Sincronizando")
                setMessage("Descargando catálogo...")
                setProgressStyle(ProgressDialog.STYLE_SPINNER)
                setCancelable(false)
                show()
            }
        } else null

        executor.execute {
            try {
                val productos = ApiClient(this).obtenerTodosProductos()
                dbHelper.sincronizarProductos(productos)
                prefs.edit().putLong("ultima_sincronizacion", System.currentTimeMillis()).apply()
                runOnUiThread {
                    progress?.dismiss()
                    mostrarUltimaActualizacion()
                    Toast.makeText(this, "✅ ${productos.size} productos sincronizados", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    progress?.dismiss()
                    Toast.makeText(this, "❌ Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun mostrarUltimaActualizacion() {
        val fecha = prefs.getLong("ultima_sincronizacion", 0)
        tvUltimaActualizacion.text = if (fecha == 0L) {
            "📅 Última actualización: Nunca"
        } else {
            "📅 Última actualización: " + SimpleDateFormat("dd/MM/yyyy HH:mm:ss", Locale.getDefault()).format(Date(fecha))
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
    }
}
