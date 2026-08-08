package com.pharmatools.inventario

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.os.Handler
import android.os.Looper
import java.nio.charset.StandardCharsets
import java.util.UUID

class BluetoothPrinterService {

    interface Callback {
        fun onSuccess()
        fun onError(error: String)
    }

    private val handler = Handler(Looper.getMainLooper())

    fun print(device: BluetoothDevice, command: String, callback: Callback) {
        Thread {
            try {
                val socket: BluetoothSocket = device.createRfcommSocketToServiceRecord(UUID_SPP)
                try {
                    BluetoothAdapter.getDefaultAdapter()?.cancelDiscovery()
                    socket.connect()
                    val out = socket.outputStream
                    out.write((command.trim() + "\r\n").toByteArray(StandardCharsets.UTF_8))
                    out.flush()
                    Thread.sleep(500)
                    handler.post { callback.onSuccess() }
                } finally {
                    runCatching { socket.close() }
                }
            } catch (e: Exception) {
                handler.post { callback.onError(e.message ?: "Error de impresión") }
            }
        }.start()
    }

    companion object {
        private val UUID_SPP = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    }
}
