package com.pharmatools.inventario

import android.bluetooth.BluetoothAdapter
import android.content.SharedPreferences
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning

class EtiquetadoDirectoActivity : AppCompatActivity() {

    private lateinit var dbHelper: DatabaseHelper
    private lateinit var printerService: BluetoothPrinterService
    private lateinit var scanner: GmsBarcodeScanner
    private lateinit var prefs: SharedPreferences
    private lateinit var tvEstado: TextView
    private lateinit var btnVolver: Button

    private val handler = Handler(Looper.getMainLooper())
    private var isScanning = false
    private var isPrinting = false
    private var intentosFallidos = 0
    private var timeoutRunnable: Runnable? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_etiquetado_directo)

        dbHelper = DatabaseHelper(this)
        printerService = BluetoothPrinterService()
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)

        val options = GmsBarcodeScannerOptions.Builder()
            .enableAutoZoom()
            .build()
        scanner = GmsBarcodeScanning.getClient(this, options)

        tvEstado = findViewById(R.id.tvEstadoDirecto)
        btnVolver = findViewById(R.id.btnVolverDirecto)
        btnVolver.setOnClickListener { finish() }

        iniciarCicloEscaneo()
    }

    private fun iniciarCicloEscaneo() {
        intentosFallidos = 0
        tvEstado.text = "📷 Escanea un código para imprimir..."
        handler.postDelayed({ iniciarEscaneoConTimeout() }, 300)
    }

    private fun iniciarEscaneoConTimeout() {
        if (isScanning) return
        isScanning = true

        val runnable = Runnable {
            if (isScanning) {
                isScanning = false
                tvEstado.text = "⏰ Tiempo de escaneo agotado"
                Toast.makeText(this, "No se detectó escaneo. Volviendo al menú.", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
        timeoutRunnable = runnable
        handler.postDelayed(runnable, TIMEOUT_ESCANEO)

        scanner.startScan()
            .addOnSuccessListener { barcode: Barcode ->
                handler.removeCallbacks(runnable)
                isScanning = false
                val codigo = barcode.rawValue ?: ""
                handler.postDelayed({ procesarCodigo(codigo) }, PAUSA_POST_ESCANEO)
            }
            .addOnFailureListener {
                handler.removeCallbacks(runnable)
                isScanning = false
                intentosFallidos++
                if (intentosFallidos >= MAX_INTENTOS_FALLIDOS) {
                    tvEstado.text = "❌ Error al escanear. Volviendo al menú."
                    Toast.makeText(this, "Error al escanear. Volviendo al menú.", Toast.LENGTH_SHORT).show()
                    handler.postDelayed({ finish() }, 1000)
                } else {
                    tvEstado.text = "⚠️ Error al escanear. Reintentando... ($intentosFallidos/$MAX_INTENTOS_FALLIDOS)"
                    handler.postDelayed({ iniciarCicloEscaneo() }, 1500)
                }
            }
    }

    private fun procesarCodigo(codigo: String) {
        val p = dbHelper.buscarPorRef(codigo)
        if (p == null) {
            intentosFallidos++
            if (intentosFallidos >= MAX_INTENTOS_FALLIDOS) {
                tvEstado.text = "❌ Producto no encontrado: $codigo. Volviendo al menú."
                Toast.makeText(this, "Producto no encontrado. Volviendo al menú.", Toast.LENGTH_SHORT).show()
                handler.postDelayed({ finish() }, 1500)
                return
            }
            tvEstado.text = "⚠️ Producto no encontrado. Reintentando... ($intentosFallidos/$MAX_INTENTOS_FALLIDOS)"
            handler.postDelayed({ iniciarCicloEscaneo() }, 1500)
            return
        }
        intentosFallidos = 0
        tvEstado.text = "🖨️ Imprimiendo: ${p.artDes}"
        imprimirEtiqueta(p)
    }

    private fun imprimirEtiqueta(p: Producto) {
        if (isPrinting) return
        isPrinting = true

        val tspl = TSPLGenerator.generar(p.artDes, p.precio)
        val mac = prefs.getString(KEY_MAC, MAC_DEFAULT) ?: MAC_DEFAULT
        val adapter = BluetoothAdapter.getDefaultAdapter()
        if (adapter == null || !adapter.isEnabled) {
            tvEstado.text = "❌ Bluetooth no disponible"
            Toast.makeText(this, "Bluetooth no disponible", Toast.LENGTH_SHORT).show()
            isPrinting = false
            handler.postDelayed({ finish() }, 1000)
            return
        }

        printerService.print(adapter.getRemoteDevice(mac), tspl, object : BluetoothPrinterService.Callback {
            override fun onSuccess() {
                runOnUiThread {
                    Toast.makeText(this@EtiquetadoDirectoActivity, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show()
                    isPrinting = false
                    tvEstado.text = "✅ Etiqueta impresa. Escanea otro producto."
                    handler.postDelayed({
                        if (!isFinishing) {
                            intentosFallidos = 0
                            iniciarCicloEscaneo()
                        }
                    }, PAUSA_POST_IMPRESION)
                }
            }
            override fun onError(error: String) {
                runOnUiThread {
                    tvEstado.text = "❌ Error: $error"
                    Toast.makeText(this@EtiquetadoDirectoActivity, "Error al imprimir: $error", Toast.LENGTH_SHORT).show()
                    isPrinting = false
                    handler.postDelayed({ finish() }, 1500)
                }
            }
        })
    }

    override fun onDestroy() {
        super.onDestroy()
        timeoutRunnable?.let { handler.removeCallbacks(it) }
        handler.removeCallbacksAndMessages(null)
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_MAC = "mac_impresora"
        private const val MAC_DEFAULT = "60:8A:10:19:48:B4"
        private const val MAX_INTENTOS_FALLIDOS = 2
        private const val TIMEOUT_ESCANEO = 15000L
        private const val PAUSA_POST_ESCANEO = 500L
        private const val PAUSA_POST_IMPRESION = 2000L
    }
}
