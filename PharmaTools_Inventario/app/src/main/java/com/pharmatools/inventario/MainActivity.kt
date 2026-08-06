package com.pharmatools.inventario

import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.doAfterTextChanged
import androidx.lifecycle.LiveData
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.gms.scanner.codescanner.GmsBarcodeScanner
import com.google.android.gms.scanner.codescanner.GmsBarcodeScannerOptions
import com.google.android.gms.scanner.codescanner.GmsBarcodeScanning
import com.pharmatools.inventario.data.AppDatabase
import com.pharmatools.inventario.data.Product
import com.pharmatools.inventario.data.ProductRepository
import com.pharmatools.inventario.databinding.ActivityMainBinding
import com.pharmatools.inventario.databinding.DialogProductBinding
import com.pharmatools.inventario.ui.InventoryViewModel
import com.pharmatools.inventario.ui.ProductAdapter

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: ProductAdapter
    private var activeObserver: LiveData<List<Product>>? = null
    private lateinit var scanner: GmsBarcodeScanner

    private val viewModel: InventoryViewModel by viewModels {
        InventoryViewModel.Factory(ProductRepository(AppDatabase.getInstance(this).productDao()))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupList()
        setupSearch()
        setupScanner()
        setupFabs()

        observeList(viewModel.products)
    }

    private fun setupList() {
        adapter = ProductAdapter { product -> showProductDialog(product) }
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        binding.recyclerView.adapter = adapter
    }

    private fun setupSearch() {
        binding.searchInput.doAfterTextChanged { text ->
            observeList(viewModel.search(text.toString()))
        }
    }

    private fun setupScanner() {
        val options = GmsBarcodeScannerOptions.Builder()
            .enableAutoZoom()
            .build()
        scanner = GmsBarcodeScanning.getScanner(this, options)
    }

    private fun setupFabs() {
        binding.fabAdd.setOnClickListener { showProductDialog(null) }
        binding.fabScan.setOnClickListener { launchScanner() }
    }

    private fun observeList(products: LiveData<List<Product>>) {
        activeObserver?.removeObservers(this)
        activeObserver = products
        products.observe(this) { list ->
            adapter.submitList(list.orEmpty())
        }
    }

    private fun launchScanner() {
        scanner.startScan()
            .addOnSuccessListener { barcode ->
                barcode.rawValue?.let(::openScannedCode)
            }
            .addOnCanceledListener { }
            .addOnFailureListener { toast(getString(R.string.sin_escaner)) }
    }

    private fun openScannedCode(code: String) {
        val existing = adapter.currentList.firstOrNull { it.code == code }
        if (existing != null) {
            showProductDialog(existing)
        } else {
            binding.searchInput.setText(code)
            showProductDialog(null)
        }
    }

    private fun showProductDialog(product: Product?) {
        val dialogBinding = DialogProductBinding.inflate(layoutInflater)
        product?.let {
            dialogBinding.etCode.setText(it.code)
            dialogBinding.etName.setText(it.name)
            dialogBinding.etCategory.setText(it.category)
            dialogBinding.etQty.setText(it.quantity.toString())
            dialogBinding.etMin.setText(it.minQuantity.toString())
            dialogBinding.etPrice.setText(it.price.toString())
        }

        val builder = AlertDialog.Builder(this)
            .setTitle(if (product == null) R.string.agregar_producto else R.string.editar_producto)
            .setView(dialogBinding.root)
            .setNegativeButton(R.string.cancelar, null)
            .setPositiveButton(R.string.guardar) { _, _ ->
                saveFrom(dialogBinding, product)
            }

        if (product != null) {
            builder.setNeutralButton(R.string.eliminar) { _, _ ->
                viewModel.deleteProduct(product.code)
            }
        }
        builder.show()
    }

    private fun saveFrom(dialogBinding: DialogProductBinding, product: Product?) {
        val code = dialogBinding.etCode.text?.toString()?.trim().orEmpty()
        val name = dialogBinding.etName.text?.toString()?.trim()
        val category = dialogBinding.etCategory.text?.toString()?.trim().orEmpty()
        val qty = dialogBinding.etQty.text?.toString()?.toIntOrNull() ?: 0
        val min = dialogBinding.etMin.text?.toString()?.toIntOrNull() ?: 0
        val price = dialogBinding.etPrice.text?.toString()?.toDoubleOrNull() ?: 0.0

        when {
            code.isEmpty() -> toast(getString(R.string.codigo_vacio))
            name.isNullOrBlank() -> toast(getString(R.string.nombre_vacio))
            else -> viewModel.saveProduct(code, name, category, qty, min, price)
        }
    }

    private fun toast(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}