package com.pharmatools.inventario

import android.bluetooth.BluetoothAdapter
import android.content.SharedPreferences
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning
import java.util.Locale

class ControlEtiquetadoActivity : AppCompatActivity() {

    private lateinit var dbHelper: DatabaseHelper
    private lateinit var printerService: BluetoothPrinterService
    private lateinit var scanner: GmsBarcodeScanner
    private lateinit var prefs: SharedPreferences

    private lateinit var tvDescripcion: TextView
    private lateinit var tvPrecio: TextView
    private lateinit var tvEstado: TextView
    private lateinit var etBusqueda: EditText
    private lateinit var lvResultados: ListView
    private lateinit var btnOk: Button
    private lateinit var btnImprimir: Button
    private lateinit var btnVolver: Button
    private lateinit var btnEscanear: Button
    private lateinit var btnGenerarCodigo: Button

    private var ultimoProducto: Producto? = null
    private var productosEncontrados: List<Producto> = emptyList()
    private lateinit var adapter: ArrayAdapter<String>
    private var isScanning = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_control_etiquetado)

        dbHelper = DatabaseHelper(this)
        printerService = BluetoothPrinterService()
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)

        val options = GmsBarcodeScannerOptions.Builder()
            .enableAutoZoom()
            .build()
        scanner = GmsBarcodeScanning.getClient(this, options)

        tvDescripcion = findViewById(R.id.tvDescripcion)
        tvPrecio = findViewById(R.id.tvPrecio)
        tvEstado = findViewById(R.id.tvEstado)
        etBusqueda = findViewById(R.id.etBusqueda)
        lvResultados = findViewById(R.id.lvResultados)
        btnOk = findViewById(R.id.btnOk)
        btnImprimir = findViewById(R.id.btnImprimir)
        btnVolver = findViewById(R.id.btnVolverControl)
        btnEscanear = findViewById(R.id.btnEscanearControl)
        btnGenerarCodigo = findViewById(R.id.btnGenerarCodigo)

        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, mutableListOf())
        lvResultados.adapter = adapter

        etBusqueda.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                buscarProductos(s?.toString() ?: "")
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        lvResultados.setOnItemClickListener { _, _, position, _ ->
            if (position < productosEncontrados.size) {
                mostrarProducto(productosEncontrados[position])
                lvResultados.visibility = View.GONE
                etBusqueda.setText("")
            }
        }

        btnEscanear.setOnClickListener { iniciarEscaneo() }
        btnOk.setOnClickListener {
            if (ultimoProducto != null) {
                tvEstado.text = "Verificado. Escanea siguiente."
                limpiarPantalla()
            } else {
                Toast.makeText(this, "No hay producto", Toast.LENGTH_SHORT).show()
            }
        }
        btnImprimir.setOnClickListener {
            ultimoProducto?.let { imprimirEtiqueta(it) } ?: Toast.makeText(this, "No hay producto", Toast.LENGTH_SHORT).show()
        }
        btnGenerarCodigo.setOnClickListener {
            ultimoProducto?.let { generarCodigoBarras(it) } ?: Toast.makeText(this, "Selecciona un producto", Toast.LENGTH_SHORT).show()
        }
        btnVolver.setOnClickListener { finish() }
    }

    private fun buscarProductos(query: String) {
        if (query.length < 2) {
            lvResultados.visibility = View.GONE
            return
        }
        productosEncontrados = dbHelper.buscarProductos(query)
        if (productosEncontrados.isEmpty()) {
            adapter.clear()
            adapter.add("No se encontraron productos")
            lvResultados.visibility = View.VISIBLE
            return
        }
        val opciones = productosEncontrados.map { "${it.artDes} - ${it.ref}" }
        adapter.clear()
        adapter.addAll(opciones)
        lvResultados.visibility = View.VISIBLE
    }

    private fun mostrarProducto(p: Producto) {
        ultimoProducto = p
        tvDescripcion.text = "📦 ${p.artDes}"
        tvPrecio.text = "💰 Precio: " + String.format(Locale.US, "%.2f", p.precio).replace('.', ',')
        tvEstado.text = "🔍 Verifica físicamente. ¿Está igual?"
        btnOk.isEnabled = true
        btnImprimir.isEnabled = true
        btnGenerarCodigo.isEnabled = true
    }

    private fun iniciarEscaneo() {
        if (isScanning) return
        isScanning = true
        scanner.startScan()
            .addOnSuccessListener { barcode: Barcode ->
                val codigo = barcode.rawValue ?: ""
                procesarCodigo(codigo)
                isScanning = false
            }
            .addOnFailureListener {
                Toast.makeText(this, "Error al escanear", Toast.LENGTH_SHORT).show()
                isScanning = false
            }
    }

    private fun procesarCodigo(codigo: String) {
        val p = dbHelper.buscarPorRef(codigo)
        if (p == null) {
            tvEstado.text = "❌ Producto no encontrado: $codigo"
            limpiarPantalla()
        } else {
            mostrarProducto(p)
        }
    }

    private fun imprimirEtiqueta(p: Producto) {
        val tspl = TSPLGenerator.generar(p.artDes, p.precio)
        val mac = prefs.getString(KEY_MAC, MAC_DEFAULT) ?: MAC_DEFAULT
        val device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac)
        printerService.print(device, tspl, object : BluetoothPrinterService.Callback {
            override fun onSuccess() {
                runOnUiThread {
                    Toast.makeText(this@ControlEtiquetadoActivity, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show()
                    tvEstado.text = "Etiqueta impresa. Escanea siguiente."
                    limpiarPantalla()
                }
            }
            override fun onError(error: String) {
                runOnUiThread { tvEstado.text = "❌ Error: $error" }
            }
        })
    }

    private fun generarCodigoBarras(p: Producto) {
        val tspl = TSPLGenerator.generarConCodigoBarras(p.artDes, p.precio, p.ref)
        val mac = prefs.getString(KEY_MAC, MAC_DEFAULT) ?: MAC_DEFAULT
        val device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac)
        printerService.print(device, tspl, object : BluetoothPrinterService.Callback {
            override fun onSuccess() {
                runOnUiThread {
                    Toast.makeText(this@ControlEtiquetadoActivity, "📦 Código de barras impreso", Toast.LENGTH_SHORT).show()
                    tvEstado.text = "Código de barras impreso. Escanea siguiente."
                    limpiarPantalla()
                }
            }
            override fun onError(error: String) {
                runOnUiThread { tvEstado.text = "❌ Error: $error" }
            }
        })
    }

    private fun limpiarPantalla() {
        ultimoProducto = null
        tvDescripcion.text = ""
        tvPrecio.text = ""
        btnOk.isEnabled = false
        btnImprimir.isEnabled = false
        btnGenerarCodigo.isEnabled = false
        lvResultados.visibility = View.GONE
        etBusqueda.setText("")
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_MAC = "mac_impresora"
        private const val MAC_DEFAULT = "60:8A:10:19:48:B4"
    }
}
