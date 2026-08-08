package com.pharmatools.inventario

import java.util.Locale

object TSPLGenerator {
    private const val ANCHO_TOTAL_DOTS = 440
    private const val MAX_CHARS_POR_LINEA = 32
    private const val DOT_POR_CAR = 12
    private const val OFFSET_CENTRADO_HORIZONTAL = -10
    private const val STEP_Y = 25
    private val Y_BASE = intArrayOf(55, 40, 30, 25, 15)
    private const val X_REF = 8
    private const val Y_REF = 182
    private const val Y_PRECIO = 150
    private const val OFFSET_PRECIO_HORIZONTAL = 35
    private const val ANCHO_DIGITO = 64
    private const val ANCHO_COMA = 38

    fun generar(descripcion: String, precio: Double): String {
        var lineas = wrapText(descripcion, MAX_CHARS_POR_LINEA)
        if (lineas.size > 5) lineas = lineas.subList(0, 5)
        val precioStr = String.format(Locale.US, "%.2f", precio).replace('.', ',')
        val partes = precioStr.split(",")
        val entero = partes[0]
        val decimal = partes[1]

        val anchoEntero = entero.length * ANCHO_DIGITO
        val anchoDecimal = 2 * ANCHO_DIGITO
        val anchoTotalPrecio = anchoEntero + ANCHO_COMA + anchoDecimal
        val xCentroTeorico = (ANCHO_TOTAL_DOTS - anchoTotalPrecio) / 2
        val xEntero = xCentroTeorico + OFFSET_PRECIO_HORIZONTAL
        val xComa = xEntero + anchoEntero
        val xDecimal = xComa + ANCHO_COMA + 2

        val sb = StringBuilder()
        sb.append("SIZE 55 mm, 40 mm\r\n")
        sb.append("GAP 0 mm, 0 mm\r\n")
        sb.append("DIRECTION 0,0\r\n")
        sb.append("REFERENCE 0,0\r\n")
        sb.append("OFFSET 0 mm\r\n")
        sb.append("SET TEAR ON\r\n")
        sb.append("CLS\r\n")

        val numLineas = lineas.size
        val yBase = Y_BASE[numLineas - 1]
        for (i in 0 until numLineas) {
            val x = (ANCHO_TOTAL_DOTS - lineas[i].length * DOT_POR_CAR) / 2 + OFFSET_CENTRADO_HORIZONTAL
            val y = yBase + i * STEP_Y
            sb.append("TEXT ").append(x).append(",").append(y).append(",\"2\",0,1,1,\"").append(lineas[i]).append("\"\r\n")
        }

        sb.append("TEXT ").append(X_REF).append(",").append(Y_REF).append(",\"4\",0,1,1,\"REF#\"\r\n")
        for (i in 0 until 3) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ").append(xEntero + dx).append(",").append(Y_PRECIO + dy).append(",\"5\",0,2,2,\"").append(entero).append("\"\r\n")
        }
        for (i in 0 until 3) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ").append(xComa + dx).append(",").append(Y_PRECIO + dy).append(",\"5\",0,1.2,2,\",\"\r\n")
        }
        for (i in 0 until 3) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ").append(xDecimal + dx).append(",").append(Y_PRECIO + dy).append(",\"5\",0,2,2,\"").append(decimal).append("\"\r\n")
        }
        sb.append("PRINT 1,1\r\n")
        return sb.toString()
    }

    fun generarConCodigoBarras(desc: String, precio: Double, codigo: String): String {
        val barcode = "BARCODE 20,180,\"128\",80,1,0,2,4,\"$codigo\"\r\nPRINT 1,1"
        return generar(desc, precio).replace("PRINT 1,1", barcode)
    }

    private fun wrapText(text: String, maxChars: Int): List<String> {
        val lines = mutableListOf<String>()
        val words = text.trim().split("\\s+".toRegex())
        val cur = StringBuilder()
        for (w in words) {
            if (cur.length + w.length + 1 <= maxChars) {
                if (cur.isNotEmpty()) cur.append(" ")
                cur.append(w)
            } else {
                lines.add(cur.toString())
                cur.setLength(0)
                cur.append(w)
            }
        }
        if (cur.isNotEmpty()) lines.add(cur.toString())
        return lines
    }
}
