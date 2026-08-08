package com.pharmatools.inventario

import android.app.ProgressDialog
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

class ConfiguracionActivity : AppCompatActivity() {

    private lateinit var prefs: SharedPreferences
    private lateinit var spinnerSede: Spinner
    private lateinit var etMacImpresora: EditText
    private lateinit var btnGuardar: Button
    private lateinit var btnVolver: Button
    private var sedes: List<SedeApiClient.Sede> = emptyList()
    private lateinit var adapter: ArrayAdapter<String>
    private var progressDialog: ProgressDialog? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_configuracion)

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        spinnerSede = findViewById(R.id.spinnerSede)
        etMacImpresora = findViewById(R.id.etMacImpresora)
        btnGuardar = findViewById(R.id.btnGuardarConfig)
        btnVolver = findViewById(R.id.btnVolverConfig)

        adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, mutableListOf())
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerSede.adapter = adapter

        btnGuardar.setOnClickListener { guardarConfiguracion() }
        btnVolver.setOnClickListener { finish() }

        cargarSedesDesdeAPI()
    }

    private fun cargarSedesDesdeAPI() {
        progressDialog = ProgressDialog(this).apply {
            setTitle("Cargando sedes")
            setMessage("Consultando lista de sedes...")
            setCancelable(false)
            show()
        }
        Thread {
            try {
                val resultado = SedeApiClient().obtenerSedes()
                runOnUiThread {
                    progressDialog?.dismiss()
                    if (resultado.isEmpty()) {
                        Toast.makeText(this, "No se encontraron sedes", Toast.LENGTH_SHORT).show()
                        return@runOnUiThread
                    }
                    sedes = resultado
                    cargarSedesEnSpinner()
                    cargarConfiguracionActual()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    progressDialog?.dismiss()
                    Toast.makeText(this, "Error al cargar sedes: ${e.message}", Toast.LENGTH_SHORT).show()
                    cargarSedesRespaldo()
                }
            }
        }.start()
    }

    private fun cargarSedesRespaldo() {
        val hardcoded = arrayOf(
            arrayOf("CATEDRAL", "Barquisimeto", "02", "1"),
            arrayOf("ESTE", "Barquisimeto", "03", "1"),
            arrayOf("OESTE", "Barquisimeto", "04", "1"),
            arrayOf("SAN BENITO (JEBE)", "Barquisimeto", "08", "1"),
            arrayOf("LA FUNDACION", "Barquisimeto", "PRIN", "3"),
            arrayOf("FARMACIA LA 21", "Barquisimeto", "09", "1"),
            arrayOf("FARMACIA CERRITOS BLANCOS", "Barquisimeto", "11", "1"),
            arrayOf("CLINIFARMA CABUDARE", "Cabudare", "01", "1"),
            arrayOf("CHUCHO BRICEÑO", "Cabudare", "06", "1"),
            arrayOf("LA MONTAÑITA", "Cabudare", "07", "1"),
            arrayOf("PLAZA SAN PEDRO", "Valera", "13", "1"),
            arrayOf("YARITAGUA", "Yaritagua", "PRIN", "2")
        )
        sedes = hardcoded.map { s ->
            SedeApiClient.Sede(s[0], s[1], s[2], s[3].toInt())
        }
        cargarSedesEnSpinner()
        cargarConfiguracionActual()
        Toast.makeText(this, "Usando lista de sedes local (sin conexión)", Toast.LENGTH_LONG).show()
    }

    private fun cargarSedesEnSpinner() {
        val nombres = sedes.map { "${it.nombre} (${it.ciudad})" }
        adapter.clear()
        adapter.addAll(nombres)
        adapter.notifyDataSetChanged()
    }

    private fun cargarConfiguracionActual() {
        val sedeActual = prefs.getString(KEY_SEDE, "CATEDRAL")
        etMacImpresora.setText(prefs.getString(KEY_MAC, MAC_DEFAULT))
        for (i in sedes.indices) {
            if (sedes[i].nombre == sedeActual) {
                spinnerSede.setSelection(i)
                break
            }
        }
    }

    private fun guardarConfiguracion() {
        val pos = spinnerSede.selectedItemPosition
        if (pos < 0) {
            Toast.makeText(this, "Selecciona una sede", Toast.LENGTH_SHORT).show()
            return
        }
        val sede = sedes[pos]
        val mac = etMacImpresora.text.toString().trim()
        if (mac.isEmpty()) {
            Toast.makeText(this, "Ingresa la MAC", Toast.LENGTH_SHORT).show()
            return
        }
        if (!mac.matches("^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$".toRegex())) {
            Toast.makeText(this, "MAC inválida. Ej: 60:8A:10:19:48:B4", Toast.LENGTH_SHORT).show()
            return
        }
        val servidorId = when (sede.nombre) {
            "YARITAGUA" -> 2
            "LA FUNDACION" -> 3
            else -> 1
        }
        prefs.edit()
            .putString(KEY_SEDE, sede.nombre)
            .putString(KEY_CO_ALMA, sede.idSucursal)
            .putInt(KEY_SERVIDOR_ID, servidorId)
            .putString(KEY_MAC, mac)
            .apply()

        AlertDialog.Builder(this)
            .setTitle("✅ Configuración guardada")
            .setMessage(
                "Sede: ${sede.nombre}\nServidor ID: $servidorId\nMAC: $mac\n\n" +
                    "📌 RECUERDA:\n• La impresora debe estar EMPAREJADA por Bluetooth\n• El PIN es: 0000"
            )
            .setPositiveButton("Entendido") { _, _ -> finish() }
            .setCancelable(false)
            .show()
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_SEDE = "sede_actual"
        private const val KEY_CO_ALMA = "co_alma"
        private const val KEY_SERVIDOR_ID = "servidor_id"
        private const val KEY_MAC = "mac_impresora"
        private const val MAC_DEFAULT = "60:8A:10:19:48:B4"
    }
}
