package com.pharmatools.inventario

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.util.Locale

class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, DB_NAME, null, VERSION) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE productos (ref TEXT PRIMARY KEY, art_des TEXT, prec_vta_usd REAL)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS productos")
        onCreate(db)
    }

    fun sincronizarProductos(productos: List<Producto>) {
        val db = writableDatabase
        db.beginTransaction()
        try {
            db.delete("productos", null, null)
            for (p in productos) {
                val cv = ContentValues().apply {
                    put("ref", p.ref)
                    put("art_des", p.artDes)
                    put("prec_vta_usd", p.precio)
                }
                db.insert("productos", null, cv)
            }
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
            db.close()
        }
    }

    fun buscarPorRef(ref: String): Producto? {
        val db = readableDatabase
        val c = db.query("productos", null, "ref=?", arrayOf(ref), null, null, null)
        c.use {
            if (it.moveToFirst()) {
                return Producto(it.getString(0), it.getString(1), it.getDouble(2))
            }
        }
        return null
    }

    fun buscarProductos(query: String): List<Producto> {
        val resultados = mutableListOf<Producto>()
        val db = readableDatabase
        val palabras = query.trim().split("\\s+".toRegex())
        val whereClause = StringBuilder()
        val args = mutableListOf<String>()

        for (palabra in palabras) {
            if (whereClause.isNotEmpty()) whereClause.append(" AND ")
            whereClause.append("(art_des LIKE ? OR ref LIKE ?)")
            args.add("%$palabra%")
            args.add("%$palabra%")
        }

        val c = db.query(
            "productos", null, whereClause.toString(),
            args.toTypedArray(), null, null, "art_des ASC LIMIT 50"
        )
        c.use {
            while (it.moveToNext()) {
                resultados.add(Producto(it.getString(0), it.getString(1), it.getDouble(2)))
            }
        }
        return resultados
    }

    fun getCantidadProductos(): Int {
        val db = readableDatabase
        var count = 0
        db.rawQuery("SELECT COUNT(*) FROM productos", null).use { c ->
            if (c.moveToFirst()) count = c.getInt(0)
        }
        return count
    }

    companion object {
        private const val DB_NAME = "productos.db"
        private const val VERSION = 1
    }
}
