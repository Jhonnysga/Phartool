package com.pharmatools.inventario.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.pharmatools.inventario.R
import com.pharmatools.inventario.data.Product
import com.pharmatools.inventario.databinding.ItemProductBinding
import java.util.Locale

class ProductAdapter(
    private val onClick: (Product) -> Unit
) : ListAdapter<Product, ProductAdapter.ProductViewHolder>(Diff) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductViewHolder {
        val binding = ItemProductBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ProductViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ProductViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ProductViewHolder(private val binding: ItemProductBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(product: Product) {
            binding.tvCode.text = product.code
            binding.tvName.text = product.name
            binding.tvCategory.text = product.category.ifBlank { "—" }
            binding.tvStock.text = "Stock: ${product.quantity} (mín ${product.minQuantity})"
            binding.tvPrice.text = String.format(Locale.getDefault(), "S/ %.2f", product.price)
            binding.tvStock.setTextColor(
                itemView.context.getColor(
                    if (product.isLowStock) R.color.bajo_stock else R.color.stock_ok
                )
            )
            binding.root.setOnClickListener { onClick(product) }
        }
    }

    companion object {
        private val Diff = object : DiffUtil.ItemCallback<Product>() {
            override fun areItemsTheSame(oldItem: Product, newItem: Product) =
                oldItem.code == newItem.code

            override fun areContentsTheSame(oldItem: Product, newItem: Product) =
                oldItem == newItem
        }
    }
}