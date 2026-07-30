#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import urllib.request
from PIL import Image, ImageDraw

PROJECT_NAME = "PharmaTools_Inventario"
PACKAGE = "com.pharmatools.inventario"
PACKAGE_PATH = PACKAGE.replace(".", "/")
COMPILE_SDK = 33
TARGET_SDK = 33
MIN_SDK = 29

def download_wrapper_jar(dest_dir):
    jar_path = os.path.join(dest_dir, "gradle-wrapper.jar")
    if os.path.exists(jar_path):
        print("  ✅ gradle-wrapper.jar ya existe")
        return
    url = "https://github.com/gradle/gradle/raw/v7.5.0/gradle/wrapper/gradle-wrapper.jar"
    print("  ⬇️ Descargando gradle-wrapper.jar...")
    try:
        urllib.request.urlretrieve(url, jar_path)
        print("  ✅ gradle-wrapper.jar descargado")
    except Exception as e:
        print(f"  ❌ Error al descargar: {e}")
        with open(jar_path, "w") as f:
            f.write("")
        print("  ⚠️ Archivo vacío creado")

def create_icon_png():
    img = Image.new('RGB', (192, 192), color='#38B2AC')
    draw = ImageDraw.Draw(img)
    draw.text((65, 65), "PT", fill='white')
    return img

def create_logo_xml():
    return '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="120dp"
    android:height="120dp"
    android:viewportWidth="120"
    android:viewportHeight="120">
    <path
        android:fillColor="#38B2AC"
        android:pathData="M20,20 L100,20 L100,100 L20,100 Z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M50,45 L70,45 L70,55 L50,55 Z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M50,65 L70,65 L70,75 L50,75 Z" />
</vector>'''

def create_project():
    project_dir = os.path.join(os.getcwd(), PROJECT_NAME)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
        print(f"  🗑️ Eliminado proyecto anterior: {project_dir}")

    print(f"  📁 Creando proyecto en: {project_dir}")
    
    # ===== CREAR ESTRUCTURA =====
    os.makedirs(os.path.join(project_dir, "app/src/main/java", PACKAGE_PATH))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/layout"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/values"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/drawable"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/mipmap-hdpi"))
    os.makedirs(os.path.join(project_dir, "gradle/wrapper"))

    download_wrapper_jar(os.path.join(project_dir, "gradle/wrapper"))

    # ===== ICONO =====
    icon_path = os.path.join(project_dir, "app/src/main/res/mipmap-hdpi", "ic_pharmatools.png")
    img = create_icon_png()
    img.save(icon_path)
    print("  ✅ ic_pharmatools.png (icono)")

    for dens in ["mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
        dest_dir = os.path.join(project_dir, "app/src/main/res", dens)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(icon_path, dest_dir)
        print(f"  ✅ ic_pharmatools.png copiado a {dens}")

    # ===== LOGO VECTORIAL =====
    logo_path = os.path.join(project_dir, "app/src/main/res/drawable", "logo_pharmatools.xml")
    with open(logo_path, "w") as f:
        f.write(create_logo_xml())
    print("  ✅ logo_pharmatools.xml")

    # ===== GRADLE FILES (CON KOTLIN) =====
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("""plugins {
    id 'com.android.application' version '7.4.2' apply false
    id 'org.jetbrains.kotlin.android' version '1.8.20' apply false
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
""")

    with open(os.path.join(project_dir, "settings.gradle"), "w") as f:
        f.write(f"""pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.PREFER_PROJECT)
    repositories {{
        google()
        mavenCentral()
    }}
}}
rootProject.name = "{PROJECT_NAME}"
include ':app'
""")

    with open(os.path.join(project_dir, "gradle.properties"), "w") as f:
        f.write("""org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
android.enableJetifier=true
org.gradle.daemon=false
org.gradle.parallel=false
kotlin.code.style=official
""")

    with open(os.path.join(project_dir, "gradle/wrapper/gradle-wrapper.properties"), "w") as f:
        f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # ===== app/build.gradle (CON KOTLIN) =====
    with open(os.path.join(project_dir, "app/build.gradle"), "w") as f:
        f.write(f"""plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}}

android {{
    namespace '{PACKAGE}'
    compileSdk {COMPILE_SDK}

    defaultConfig {{
        applicationId '{PACKAGE}'
        minSdk {MIN_SDK}
        targetSdk {TARGET_SDK}
        versionCode 1
        versionName '1.0'
        multiDexEnabled true
    }}

    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_11
        targetCompatibility JavaVersion.VERSION_11
    }}

    kotlinOptions {{
        jvmTarget = '11'
    }}

    lintOptions {{
        abortOnError false
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    
    // ESCÁNER DE GOOGLE PLAY SERVICES
    implementation 'com.google.android.gms:play-services-code-scanner:16.1.0'
    implementation 'com.google.android.gms:play-services-base:18.3.0'
    implementation 'com.google.android.gms:play-services-basement:18.3.0'
    implementation 'com.google.android.gms:play-services-tasks:18.1.0'
    
    implementation 'androidx.multidex:multidex:2.0.1'
    implementation 'org.json:json:20230227'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.google.code.gson:gson:2.10.1'
}}
""")

    # ===== ANDROID MANIFEST =====
    with open(os.path.join(project_dir, "app/src/main/AndroidManifest.xml"), "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.BLUETOOTH" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.CAMERA" />

    <application
        android:allowBackup="true"
        android:label="Pharmatools Tag"
        android:theme="@style/Theme.PharmatoolsTag"
        android:icon="@mipmap/ic_pharmatools"
        android:roundIcon="@mipmap/ic_pharmatools"
        android:usesCleartextTraffic="true">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ControlEtiquetadoActivity" />
        <activity android:name=".EtiquetadoDirectoActivity" />
        <activity android:name=".ConfiguracionActivity" />
    </application>
</manifest>
""")

    # ===== RECURSOS VALUES =====
    colors_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="color_principal">#38B2AC</color>
    <color name="color_principal_oscuro">#2C9C96</color>
    <color name="color_principal_claro">#E6F7F6</color>
    <color name="fondo_general">#F8F9FA</color>
    <color name="fondo_tarjeta">#FFFFFF</color>
    <color name="texto_principal">#212529</color>
    <color name="texto_secundario">#6C757D</color>
    <color name="primaryDarkColor">@color/color_principal_oscuro</color>
    <color name="primaryColor">@color/color_principal</color>
    <color name="accentColor">@color/color_principal</color>
    <color name="backgroundColor">@color/fondo_general</color>
    <color name="surfaceColor">@color/fondo_tarjeta</color>
</resources>
"""
    with open(os.path.join(project_dir, "app/src/main/res/values/colors.xml"), "w") as f:
        f.write(colors_xml)
    print("  ✅ colors.xml")

    themes_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.PharmatoolsTag" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="android:statusBarColor">@color/color_principal_oscuro</item>
        <item name="colorPrimary">@color/color_principal</item>
        <item name="colorPrimaryVariant">@color/color_principal_oscuro</item>
        <item name="colorSecondary">@color/color_principal</item>
        <item name="colorAccent">@color/color_principal</item>
        <item name="android:colorBackground">@color/fondo_general</item>
        <item name="colorSurface">@color/fondo_tarjeta</item>
        <item name="android:textColorPrimary">@color/texto_principal</item>
        <item name="android:textColorSecondary">@color/texto_secundario</item>
    </style>
</resources>
"""
    with open(os.path.join(project_dir, "app/src/main/res/values/themes.xml"), "w") as f:
        f.write(themes_xml)
    print("  ✅ themes.xml")

    styles_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="ButtonStyle" parent="Widget.MaterialComponents.Button">
        <item name="android:backgroundTint">@color/color_principal</item>
        <item name="android:textColor">@android:color/white</item>
        <item name="android:textSize">16sp</item>
        <item name="android:padding">12dp</item>
        <item name="cornerRadius">8dp</item>
        <item name="android:elevation">2dp</item>
    </style>
    <style name="ButtonSecondary" parent="Widget.MaterialComponents.Button.OutlinedButton">
        <item name="android:textColor">@color/color_principal</item>
        <item name="android:textSize">16sp</item>
        <item name="cornerRadius">8dp</item>
        <item name="strokeColor">@color/color_principal</item>
        <item name="strokeWidth">1dp</item>
    </style>
</resources>
"""
    with open(os.path.join(project_dir, "app/src/main/res/values/styles.xml"), "w") as f:
        f.write(styles_xml)
    print("  ✅ styles.xml")

    strings_xml = """<resources>
    <string name="app_name">Pharmatools Tag</string>
</resources>
"""
    with open(os.path.join(project_dir, "app/src/main/res/values/strings.xml"), "w") as f:
        f.write(strings_xml)
    print("  ✅ strings.xml")

    # ===== LAYOUTS =====
    layouts = {
        "activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true"
    android:background="@color/fondo_general">
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:gravity="center_horizontal"
        android:padding="24dp">
        <ImageView
            android:id="@+id/iv_logo"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:adjustViewBounds="true"
            android:src="@drawable/logo_pharmatools"
            android:layout_marginTop="16dp"
            android:layout_marginBottom="16dp" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Pharmatools Tag"
            android:textSize="28sp"
            android:textStyle="bold"
            android:textColor="@color/color_principal"
            android:layout_marginBottom="8dp" />
        <TextView
            android:id="@+id/tvUltimaActualizacion"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="📅 Última actualización: --"
            android:textSize="14sp"
            android:textColor="@color/texto_secundario"
            android:layout_marginBottom="32dp" />
        <Button
            android:id="@+id/btnSincronizar"
            style="@style/ButtonStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="🔄 Sincronizar productos"
            android:layout_marginBottom="16dp" />
        <Button
            android:id="@+id/btnControlEtiquetado"
            style="@style/ButtonStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="🔍 Control de Etiquetado"
            android:layout_marginBottom="16dp" />
        <Button
            android:id="@+id/btnEtiquetado"
            style="@style/ButtonStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="🏷️ Etiquetado"
            android:layout_marginBottom="16dp" />
        <Button
            android:id="@+id/btnConfiguracion"
            style="@style/ButtonSecondary"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="⚙️ Configuración" />
    </LinearLayout>
</ScrollView>""",
        "activity_control_etiquetado.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="@color/fondo_general">
    <TextView
        android:id="@+id/tvEstado"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Escanea o busca un producto"
        android:textSize="18sp"
        android:textColor="@color/texto_principal"
        android:layout_marginBottom="16dp" />
    <EditText
        android:id="@+id/etBusqueda"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="🔍 Buscar por nombre o código..."
        android:inputType="text"
        android:layout_marginBottom="8dp" />
    <ListView
        android:id="@+id/lvResultados"
        android:layout_width="match_parent"
        android:layout_height="200dp"
        android:visibility="gone" />
    <Button
        android:id="@+id/btnEscanearControl"
        style="@style/ButtonStyle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="📷 Escanear código"
        android:layout_marginBottom="8dp" />
    <TextView
        android:id="@+id/tvDescripcion"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="16sp"
        android:textColor="@color/texto_principal"
        android:layout_marginBottom="8dp" />
    <TextView
        android:id="@+id/tvPrecio"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="16sp"
        android:textColor="@color/texto_principal"
        android:layout_marginBottom="16dp" />
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:layout_marginBottom="16dp">
        <Button
            android:id="@+id/btnOk"
            style="@style/ButtonSecondary"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="✅ OK (verificado)"
            android:enabled="false" />
        <Button
            android:id="@+id/btnImprimir"
            style="@style/ButtonStyle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="🏷️ Imprimir precio"
            android:enabled="false"
            android:layout_marginStart="8dp" />
        <Button
            android:id="@+id/btnGenerarCodigo"
            style="@style/ButtonStyle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="📦 Crear código"
            android:enabled="false"
            android:layout_marginStart="8dp" />
    </LinearLayout>
    <Button
        android:id="@+id/btnVolverControl"
        style="@style/ButtonSecondary"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="🔙 Volver al menú" />
</LinearLayout>""",
        "activity_etiquetado_directo.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:padding="24dp"
    android:background="@color/fondo_general">
    <TextView
        android:id="@+id/tvEstadoDirecto"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="📷 Escanea un código para imprimir..."
        android:textSize="20sp"
        android:textColor="@color/texto_principal"
        android:gravity="center"
        android:layout_marginBottom="32dp" />
    <Button
        android:id="@+id/btnVolverDirecto"
        style="@style/ButtonSecondary"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="🔙 Volver al menú" />
</LinearLayout>""",
        "activity_configuracion.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:background="@color/fondo_general">
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="⚙️ Configuración Avanzada"
        android:textSize="24sp"
        android:textStyle="bold"
        android:textColor="@color/color_principal"
        android:layout_marginBottom="24dp" />
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="📍 Selecciona la sede"
        android:textSize="16sp"
        android:textColor="@color/texto_principal"
        android:layout_marginBottom="8dp" />
    <Spinner
        android:id="@+id/spinnerSede"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginBottom="16dp" />
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="📡 MAC de la impresora"
        android:textSize="16sp"
        android:textColor="@color/texto_principal"
        android:layout_marginBottom="8dp" />
    <EditText
        android:id="@+id/etMacImpresora"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Ej: 60:8A:10:19:48:B4"
        android:inputType="text"
        android:layout_marginBottom="16dp" />
    <Button
        android:id="@+id/btnGuardarConfig"
        style="@style/ButtonStyle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="💾 Guardar configuración"
        android:layout_marginBottom="16dp" />
    <Button
        android:id="@+id/btnVolverConfig"
        style="@style/ButtonSecondary"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="🔙 Volver al menú" />
</LinearLayout>"""
    }

    for name, content in layouts.items():
        path = os.path.join(project_dir, "app/src/main/res/layout", name)
        with open(path, "w") as f:
            f.write(content)
        print(f"  ✅ {name}")

    # ===== CLASES KOTLIN =====
    kotlin_files = {
        "Producto.kt": """
package com.pharmatools.inventario

data class Producto(
    val ref: String,
    val artDes: String,
    val precio: Double
)
""",
        "DatabaseHelper.kt": """
package com.pharmatools.inventario

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, DB_NAME, null, VERSION) {

    companion object {
        private const val DB_NAME = "productos.db"
        private const val VERSION = 1
    }

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
        return if (c != null && c.moveToFirst()) {
            Producto(c.getString(0), c.getString(1), c.getDouble(2))
        } else null
    }

    fun buscarProductos(query: String): List<Producto> {
        val resultados = mutableListOf<Producto>()
        val db = readableDatabase
        val palabras = query.trim().split("\\\\s+".toRegex())
        val whereClause = StringBuilder()
        val args = mutableListOf<String>()

        for (palabra in palabras) {
            if (whereClause.isNotEmpty()) whereClause.append(" AND ")
            whereClause.append("(art_des LIKE ? OR ref LIKE ?)")
            args.add("%$palabra%")
            args.add("%$palabra%")
        }

        val c = db.query("productos", null, whereClause.toString(),
            args.toTypedArray(), null, null, "art_des ASC LIMIT 50")

        while (c.moveToNext()) {
            resultados.add(Producto(c.getString(0), c.getString(1), c.getDouble(2)))
        }
        c.close()
        db.close()
        return resultados
    }

    fun getCantidadProductos(): Int {
        val db = readableDatabase
        val c = db.rawQuery("SELECT COUNT(*) FROM productos", null)
        val count = if (c.moveToFirst()) c.getInt(0) else 0
        c.close()
        db.close()
        return count
    }
}
""",
        "ApiClient.kt": """
package com.pharmatools.inventario

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class ApiClient(private val context: Context) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(120, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()

    private fun getCoAlma(): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_CO_ALMA, "02") ?: "02"
    }

    private fun getServidorId(): Int {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getInt(KEY_SERVIDOR_ID, 1)
    }

    fun obtenerTodosProductos(): List<Producto> {
        val coAlma = getCoAlma()
        val servidorId = getServidorId()
        val url = "$BASE_URL?page=1&perPage=10000&co_alma=$coAlma&servidorId=$servidorId"
        val request = Request.Builder().url(url).build()
        val response = client.newCall(request).execute()
        if (!response.isSuccessful) throw IOException("Error HTTP: ${response.code}")
        val json = response.body?.string() ?: throw IOException("Respuesta vacía")
        val root = gson.fromJson(json, JsonObject::class.java)
        val list = root.getAsJsonObject("result").getAsJsonArray("list")
        return list.map { item ->
            val obj = item.asJsonObject
            Producto(obj.get("ref").asString, obj.get("art_des").asString, obj.get("prec_vta_usd").asDouble)
        }
    }

    fun obtenerProductoPorRef(ref: String): Producto? {
        val coAlma = getCoAlma()
        val servidorId = getServidorId()
        val url = "$BASE_URL?page=1&perPage=1&filter=$ref&co_alma=$coAlma&servidorId=$servidorId"
        val request = Request.Builder().url(url).build()
        val response = client.newCall(request).execute()
        if (!response.isSuccessful) return null
        val json = response.body?.string() ?: return null
        val root = gson.fromJson(json, JsonObject::class.java)
        if (root.get("succeeded").asBoolean) {
            val list = root.getAsJsonObject("result").getAsJsonArray("list")
            if (list.size() > 0) {
                val item = list.get(0).asJsonObject
                return Producto(item.get("ref").asString, item.get("art_des").asString, item.get("prec_vta_usd").asDouble)
            }
        }
        return null
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_CO_ALMA = "co_alma"
        private const val KEY_SERVIDOR_ID = "servidor_id"
        private const val BASE_URL = "https://citasprevimedicaidb.com:3276/api/Art/"
    }
}
""",
        "SedeApiClient.kt": """
package com.pharmatools.inventario

import com.google.gson.Gson
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class SedeApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()

    data class Sede(val nombre: String, val ciudad: String, val idSucursal: String, val servidorId: Int)

    fun obtenerSedes(): List<Sede> {
        val request = Request.Builder().url(BASE_URL).build()
        val response = client.newCall(request).execute()
        if (!response.isSuccessful) throw IOException("Error HTTP: ${response.code}")
        val json = response.body?.string() ?: throw IOException("Respuesta vacía")
        val jsonArray = gson.fromJson(json, Array<SedeData>::class.java)
        return jsonArray.map { Sede(it.nombre, it.ciudad, it.idSucursalExt.trim(), it.servidorId) }
    }

    private data class SedeData(
        val nombre: String,
        val ciudad: String,
        val id_sucursal_ext: String,
        val servidorId: Int
    ) {
        val idSucursalExt = id_sucursal_ext
    }

    companion object {
        private const val BASE_URL = "https://citasprevimedicaidb.com:3276/api/Sucursal/ListarSedesCiudad/"
    }
}
""",
        "BluetoothPrinterService.kt": """
package com.pharmatools.inventario

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.os.Handler
import android.os.Looper
import java.io.OutputStream
import java.nio.charset.StandardCharsets
import java.util.UUID

class BluetoothPrinterService {
    private val handler = Handler(Looper.getMainLooper())

    interface Callback {
        fun onSuccess()
        fun onError(error: String)
    }

    fun print(device: BluetoothDevice, command: String, callback: Callback) {
        Thread {
            try {
                val socket = device.createRfcommSocketToServiceRecord(UUID_SPP)
                BluetoothAdapter.getDefaultAdapter().cancelDiscovery()
                socket.connect()
                val out = socket.outputStream
                out.write("$command\\r\\n".toByteArray(StandardCharsets.UTF_8))
                out.flush()
                Thread.sleep(500)
                handler.post { callback.onSuccess() }
                socket.close()
            } catch (e: Exception) {
                handler.post { callback.onError(e.message ?: "Error desconocido") }
            }
        }.start()
    }

    companion object {
        private val UUID_SPP = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    }
}
""",
        "TSPLGenerator.kt": """
package com.pharmatools.inventario

import kotlin.math.min

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
        val precioStr = String.format("%.2f", precio).replace('.', ',')
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
        sb.append("SIZE 55 mm, 40 mm\\r\\nGAP 0 mm, 0 mm\\r\\nDIRECTION 0,0\\r\\nREFERENCE 0,0\\r\\nOFFSET 0 mm\\r\\nSET TEAR ON\\r\\nCLS\\r\\n")

        val numLineas = lineas.size
        val yBase = Y_BASE[numLineas - 1]
        for (i in lineas.indices) {
            val x = (ANCHO_TOTAL_DOTS - lineas[i].length * DOT_POR_CAR) / 2 + OFFSET_CENTRADO_HORIZONTAL
            val y = yBase + i * STEP_Y
            sb.append("TEXT $x,$y,\\"2\\",0,1,1,\\"${lineas[i]}\\"\\r\\n")
        }

        sb.append("TEXT $X_REF,$Y_REF,\\"4\\",0,1,1,\\"REF#\\"\\r\\n")
        for (i in 0..2) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ${xEntero + dx},${Y_PRECIO + dy},\\"5\\",0,2,2,\\"$entero\\"\\r\\n")
        }
        for (i in 0..2) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ${xComa + dx},${Y_PRECIO + dy},\\"5\\",0,1.2,2,\\",\\"\\r\\n")
        }
        for (i in 0..2) {
            val dx = if (i == 1) 1 else 0
            val dy = if (i == 2) 1 else 0
            sb.append("TEXT ${xDecimal + dx},${Y_PRECIO + dy},\\"5\\",0,2,2,\\"$decimal\\"\\r\\n")
        }
        sb.append("PRINT 1,1\\r\\n")
        return sb.toString()
    }

    fun generarConCodigoBarras(desc: String, precio: Double, codigo: String): String {
        return generar(desc, precio).replace("PRINT 1,1", "BARCODE 20,180,\\"128\\",80,1,0,2,4,\\"$codigo\\"\\r\\nPRINT 1,1")
    }

    private fun wrapText(text: String, maxChars: Int): List<String> {
        val lines = mutableListOf<String>()
        val words = text.trim().split("\\\\s+".toRegex())
        val cur = StringBuilder()
        for (w in words) {
            if (cur.length + w.length + 1 <= maxChars) {
                if (cur.isNotEmpty()) cur.append(" ")
                cur.append(w)
            } else {
                lines.add(cur.toString())
                cur.clear()
                cur.append(w)
            }
        }
        if (cur.isNotEmpty()) lines.add(cur.toString())
        return lines
    }
}
""",
        "MainActivity.kt": """
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
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var dbHelper: DatabaseHelper
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var prefs: SharedPreferences
    private lateinit var tvUltimaActualizacion: TextView
    private lateinit var btnSincronizar: Button
    private lateinit var btnControl: Button
    private lateinit var btnDirecto: Button
    private lateinit var btnConfig: Button

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
        if (dbHelper.getCantidadProductos() == 0) sincronizarProductos(true)
        else {
            val ultima = prefs.getLong("ultima_sincronizacion", 0)
            if (System.currentTimeMillis() - ultima > 24 * 60 * 60 * 1000) sincronizarProductos(false)
        }
    }

    private fun sincronizarProductos(mostrarDialogo: Boolean) {
        var progress: ProgressDialog? = null
        if (mostrarDialogo) {
            progress = ProgressDialog(this).apply {
                setTitle("Sincronizando")
                setMessage("Descargando catálogo...")
                setProgressStyle(ProgressDialog.STYLE_SPINNER)
                setCancelable(false)
                show()
            }
        }
        val finalProgress = progress
        executor.execute {
            try {
                val productos = ApiClient(this).obtenerTodosProductos()
                dbHelper.sincronizarProductos(productos)
                prefs.edit().putLong("ultima_sincronizacion", System.currentTimeMillis()).apply()
                runOnUiThread {
                    finalProgress?.dismiss()
                    mostrarUltimaActualizacion()
                    Toast.makeText(this, "✅ ${productos.size} productos sincronizados", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    finalProgress?.dismiss()
                    Toast.makeText(this, "❌ Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun mostrarUltimaActualizacion() {
        val fecha = prefs.getLong("ultima_sincronizacion", 0)
        tvUltimaActualizacion.text = if (fecha == 0L) "📅 Última actualización: Nunca"
        else "📅 Última actualización: ${SimpleDateFormat("dd/MM/yyyy HH:mm:ss", Locale.getDefault()).format(Date(fecha))}"
    }
}
""",
        "ControlEtiquetadoActivity.kt": """
package com.pharmatools.inventario

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

import com.google.android.gms.code_scanner.GmsBarcodeScanner
import com.google.android.gms.tasks.Task
import com.google.mlkit.vision.barcode.common.Barcode

class ControlEtiquetadoActivity : AppCompatActivity() {
    private lateinit var dbHelper: DatabaseHelper
    private lateinit var printerService: BluetoothPrinterService
    private lateinit var scanner: GmsBarcodeScanner
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
    private var productosEncontrados = mutableListOf<Producto>()
    private lateinit var adapter: ArrayAdapter<String>
    private lateinit var prefs: SharedPreferences
    private var isScanning = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_control_etiquetado)
        dbHelper = DatabaseHelper(this)
        printerService = BluetoothPrinterService()
        scanner = GmsBarcodeScanner.getInstance(this)
        prefs = getSharedPreferences("PharmatoolsPrefs", MODE_PRIVATE)

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
                buscarProductos(s.toString())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        lvResultados.setOnItemClickListener { _, _, position, _ ->
            val p = productosEncontrados[position]
            mostrarProducto(p)
            lvResultados.visibility = android.view.View.GONE
            etBusqueda.setText("")
        }

        btnEscanear.setOnClickListener { iniciarEscaneo() }
        btnOk.setOnClickListener {
            if (ultimoProducto != null) {
                tvEstado.text = "Verificado. Escanea siguiente."
                limpiarPantalla()
            } else Toast.makeText(this, "No hay producto", Toast.LENGTH_SHORT).show()
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
            lvResultados.visibility = android.view.View.GONE
            return
        }
        productosEncontrados = dbHelper.buscarProductos(query).toMutableList()
        if (productosEncontrados.isEmpty()) {
            adapter.clear()
            adapter.add("No se encontraron productos")
            lvResultados.visibility = android.view.View.VISIBLE
            return
        }
        val opciones = productosEncontrados.map { "${it.artDes} - ${it.ref}" }
        adapter.clear()
        adapter.addAll(opciones)
        lvResultados.visibility = android.view.View.VISIBLE
    }

    private fun mostrarProducto(p: Producto) {
        ultimoProducto = p
        tvDescripcion.text = "📦 ${p.artDes}"
        tvPrecio.text = "💰 Precio: ${String.format("%.2f", p.precio).replace('.', ',')}"
        tvEstado.text = "🔍 Verifica físicamente. ¿Está igual?"
        btnOk.isEnabled = true
        btnImprimir.isEnabled = true
        btnGenerarCodigo.isEnabled = true
    }

    private fun iniciarEscaneo() {
        if (isScanning) return
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), CAMERA_PERMISSION_CODE)
            return
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT), BLUETOOTH_PERMISSION_CODE)
                return
            }
        }
        isScanning = true
        tvEstado.text = "📷 Escaneando..."
        val task = scanner.startScan()
        task.addOnSuccessListener { barcode ->
            val codigo = barcode.rawValue
            procesarCodigo(codigo)
            isScanning = false
        }.addOnFailureListener { e ->
            Toast.makeText(this, "Error al escanear: ${e.message}", Toast.LENGTH_SHORT).show()
            tvEstado.text = "❌ Error al escanear"
            isScanning = false
        }
    }

    private fun procesarCodigo(codigo: String) {
        val p = dbHelper.buscarPorRef(codigo)
        if (p == null) {
            tvEstado.text = "❌ Producto no encontrado: $codigo"
            limpiarPantalla()
        } else mostrarProducto(p)
    }

    private fun imprimirEtiqueta(p: Producto) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_CONNECT), BLUETOOTH_PERMISSION_CODE)
                return
            }
        }
        val tspl = TSPLGenerator.generar(p.artDes, p.precio)
        val mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4") ?: "60:8A:10:19:48:B4"
        try {
            val device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac)
            tvEstado.text = "🖨️ Imprimiendo..."
            printerService.print(device, tspl, object : BluetoothPrinterService.Callback {
                override fun onSuccess() {
                    runOnUiThread {
                        Toast.makeText(this@ControlEtiquetadoActivity, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show()
                        tvEstado.text = "✅ Etiqueta impresa. Escanea siguiente."
                        limpiarPantalla()
                    }
                }
                override fun onError(error: String) {
                    runOnUiThread {
                        tvEstado.text = "❌ Error: $error"
                        Toast.makeText(this@ControlEtiquetadoActivity, "Error: $error", Toast.LENGTH_SHORT).show()
                    }
                }
            })
        } catch (e: Exception) {
            tvEstado.text = "❌ Error Bluetooth: ${e.message}"
            Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun generarCodigoBarras(p: Producto) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_CONNECT), BLUETOOTH_PERMISSION_CODE)
                return
            }
        }
        val tspl = TSPLGenerator.generarConCodigoBarras(p.artDes, p.precio, p.ref)
        val mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4") ?: "60:8A:10:19:48:B4"
        try {
            val device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac)
            tvEstado.text = "🖨️ Generando código..."
            printerService.print(device, tspl, object : BluetoothPrinterService.Callback {
                override fun onSuccess() {
                    runOnUiThread {
                        Toast.makeText(this@ControlEtiquetadoActivity, "📦 Código de barras impreso", Toast.LENGTH_SHORT).show()
                        tvEstado.text = "✅ Código impreso. Escanea siguiente."
                        limpiarPantalla()
                    }
                }
                override fun onError(error: String) {
                    runOnUiThread {
                        tvEstado.text = "❌ Error: $error"
                        Toast.makeText(this@ControlEtiquetadoActivity, "Error: $error", Toast.LENGTH_SHORT).show()
                    }
                }
            })
        } catch (e: Exception) {
            tvEstado.text = "❌ Error Bluetooth: ${e.message}"
            Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun limpiarPantalla() {
        ultimoProducto = null
        tvDescripcion.text = ""
        tvPrecio.text = ""
        btnOk.isEnabled = false
        btnImprimir.isEnabled = false
        btnGenerarCodigo.isEnabled = false
        lvResultados.visibility = android.view.View.GONE
        etBusqueda.setText("")
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            CAMERA_PERMISSION_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) iniciarEscaneo()
                else Toast.makeText(this, "Permiso de cámara necesario", Toast.LENGTH_SHORT).show()
            }
            BLUETOOTH_PERMISSION_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    if (ultimoProducto != null) imprimirEtiqueta(ultimoProducto!!)
                    else iniciarEscaneo()
                } else Toast.makeText(this, "Permisos Bluetooth necesarios", Toast.LENGTH_SHORT).show()
            }
        }
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_MAC = "mac_impresora"
        private const val CAMERA_PERMISSION_CODE = 100
        private const val BLUETOOTH_PERMISSION_CODE = 200
    }
}
""",
        "EtiquetadoDirectoActivity.kt": """
package com.pharmatools.inventario

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

import com.google.android.gms.code_scanner.GmsBarcodeScanner
import com.google.android.gms.tasks.Task
import com.google.mlkit.vision.barcode.common.Barcode

class EtiquetadoDirectoActivity : AppCompatActivity() {
    private lateinit var dbHelper: DatabaseHelper
    private lateinit var printerService: BluetoothPrinterService
    private lateinit var scanner: GmsBarcodeScanner
    private lateinit var tvEstado: TextView
    private lateinit var btnVolver: Button
    private lateinit var prefs: SharedPreferences
    private var isScanning = false
    private var isPrinting = false
    private val handler = Handler()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_etiquetado_directo)
        dbHelper = DatabaseHelper(this)
        printerService = BluetoothPrinterService()
        scanner = GmsBarcodeScanner.getInstance(this)
        prefs = getSharedPreferences("PharmatoolsPrefs", MODE_PRIVATE)
        tvEstado = findViewById(R.id.tvEstadoDirecto)
        btnVolver = findViewById(R.id.btnVolverDirecto)
        btnVolver.setOnClickListener { finish() }
        iniciarCicloEscaneo()
    }

    private fun iniciarCicloEscaneo() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), CAMERA_PERMISSION_CODE)
            return
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT), BLUETOOTH_PERMISSION_CODE)
                return
            }
        }
        tvEstado.text = "📷 Escanea un código..."
        if (isScanning) return
        isScanning = true
        val task = scanner.startScan()
        task.addOnSuccessListener { barcode ->
            isScanning = false
            val codigo = barcode.rawValue
            procesarCodigo(codigo)
        }.addOnFailureListener { e ->
            isScanning = false
            tvEstado.text = "❌ Error al escanear: ${e.message}"
            handler.postDelayed({ iniciarCicloEscaneo() }, 2000)
        }
    }

    private fun procesarCodigo(codigo: String) {
        val p = dbHelper.buscarPorRef(codigo)
        if (p == null) {
            tvEstado.text = "❌ Producto no encontrado: $codigo"
            handler.postDelayed({ iniciarCicloEscaneo() }, 2000)
            return
        }
        tvEstado.text = "🖨️ Imprimiendo: ${p.artDes}"
        imprimirEtiqueta(p)
    }

    private fun imprimirEtiqueta(p: Producto) {
        if (isPrinting) return
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_CONNECT), BLUETOOTH_PERMISSION_CODE)
                return
            }
        }
        isPrinting = true
        val tspl = TSPLGenerator.generar(p.artDes, p.precio)
        val mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4") ?: "60:8A:10:19:48:B4"
        val adapter = BluetoothAdapter.getDefaultAdapter()
        if (adapter == null || !adapter.isEnabled()) {
            tvEstado.text = "❌ Bluetooth no disponible"
            Toast.makeText(this, "Bluetooth no disponible", Toast.LENGTH_SHORT).show()
            isPrinting = false
            handler.postDelayed({ iniciarCicloEscaneo() }, 2000)
            return
        }
        try {
            val device = adapter.getRemoteDevice(mac)
            printerService.print(device, tspl, object : BluetoothPrinterService.Callback {
                override fun onSuccess() {
                    runOnUiThread {
                        Toast.makeText(this@EtiquetadoDirectoActivity, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show()
                        isPrinting = false
                        tvEstado.text = "✅ Etiqueta impresa. Escanea otro."
                        handler.postDelayed({ iniciarCicloEscaneo() }, 1500)
                    }
                }
                override fun onError(error: String) {
                    runOnUiThread {
                        tvEstado.text = "❌ Error: $error"
                        Toast.makeText(this@EtiquetadoDirectoActivity, "Error al imprimir", Toast.LENGTH_SHORT).show()
                        isPrinting = false
                        handler.postDelayed({ iniciarCicloEscaneo() }, 2000)
                    }
                }
            })
        } catch (e: Exception) {
            tvEstado.text = "❌ Error Bluetooth: ${e.message}"
            isPrinting = false
            handler.postDelayed({ iniciarCicloEscaneo() }, 2000)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == CAMERA_PERMISSION_CODE || requestCode == BLUETOOTH_PERMISSION_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                iniciarCicloEscaneo()
            } else {
                Toast.makeText(this, "Permisos necesarios", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    companion object {
        private const val PREFS_NAME = "PharmatoolsPrefs"
        private const val KEY_MAC = "mac_impresora"
        private const val CAMERA_PERMISSION_CODE = 100
        private const val BLUETOOTH_PERMISSION_CODE = 200
    }
}
""",
        "ConfiguracionActivity.kt": """
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
    private lateinit var spinnerSede: Spinner
    private lateinit var etMacImpresora: EditText
    private lateinit var btnGuardar: Button
    private lateinit var btnVolver: Button
    private lateinit var prefs: SharedPreferences
    private val sedes = mutableListOf<SedeApiClient.Sede>()
    private lateinit var adapter: ArrayAdapter<String>
    private var progressDialog: ProgressDialog? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_configuracion)
        prefs = getSharedPreferences("PharmatoolsPrefs", MODE_PRIVATE)
        spinnerSede = findViewById(R.id.spinnerSede)
        etMacImpresora = findViewById(R.id.etMacImpresora)
        btnGuardar = findViewById(R.id.btnGuardarConfig)
        btnVolver = findViewById(R.id.btnVolverConfig)

        adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, mutableListOf())
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerSede.adapter = adapter

        btnGuardar.setOnClickListener { guardarConfiguracion() }
        btnVolver.setOnClickListener { finish() }
        cargarSedesRespaldo()
    }

    private fun cargarSedesRespaldo() {
        sedes.clear()
        val hardcoded = arrayOf(
            arrayOf("CATEDRAL","Barquisimeto","02","1"),
            arrayOf("ESTE","Barquisimeto","03","1"),
            arrayOf("OESTE","Barquisimeto","04","1"),
            arrayOf("SAN BENITO (JEBE)","Barquisimeto","08","1"),
            arrayOf("LA FUNDACION","Barquisimeto","PRIN","3"),
            arrayOf("FARMACIA LA 21","Barquisimeto","09","1"),
            arrayOf("FARMACIA CERRITOS BLANCOS","Barquisimeto","11","1"),
            arrayOf("CLINIFARMA CABUDARE","Cabudare","01","1"),
            arrayOf("CHUCHO BRICEÑO","Cabudare","06","1"),
            arrayOf("LA MONTAÑITA","Cabudare","07","1"),
            arrayOf("PLAZA SAN PEDRO","Valera","13","1"),
            arrayOf("YARITAGUA","Yaritagua","PRIN","2")
        )
        for (s in hardcoded) {
            sedes.add(SedeApiClient.Sede(s[0], s[1], s[2], s[3].toInt()))
        }
        cargarSedesEnSpinner()
        cargarConfiguracionActual()
        Toast.makeText(this, "Usando lista de sedes local", Toast.LENGTH_LONG).show()
    }

    private fun cargarSedesEnSpinner() {
        val nombres = sedes.map { "${it.nombre} (${it.ciudad})" }
        adapter.clear()
        adapter.addAll(nombres)
        adapter.notifyDataSetChanged()
    }

    private fun cargarConfiguracionActual() {
        val sedeActual = prefs.getString(KEY_SEDE, "CATEDRAL") ?: "CATEDRAL"
        etMacImpresora.setText(prefs.getString(KEY_MAC, "60:8A:10:19:48:B4"))
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
        val servidorId = when {
            sede.nombre == "YARITAGUA" -> 2
            sede.nombre == "LA FUNDACION" -> 3
            else -> 1
        }
        prefs.edit().apply {
            putString(KEY_SEDE, sede.nombre)
            putString(KEY_CO_ALMA, sede.idSucursal)
            putInt(KEY_SERVIDOR_ID, servidorId)
            putString(KEY_MAC, mac)
        }.apply()

        AlertDialog.Builder(this)
            .setTitle("✅ Configuración guardada")
            .setMessage("Sede: ${sede.nombre}\\nServidor ID: $servidorId\\nMAC: $mac\\n\\n📌 RECUERDA:\\n• La impresora debe estar EMPAREJADA por Bluetooth\\n• El PIN es: 0000")
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
    }
}
"""
    }

    for fname, content in kotlin_files.items():
        path = os.path.join(project_dir, "app/src/main/java", PACKAGE_PATH, fname)
        with open(path, "w") as f:
            f.write(content.strip())
        print(f"  ✅ {fname}")

    # ===== GRADLEW SCRIPT =====
    gradlew_path = os.path.join(project_dir, "gradlew")
    with open(gradlew_path, "w") as f:
        f.write("""#!/bin/bash
if [ -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    java -cp "gradle/wrapper/gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain "$@"
else
    echo "Error: gradle-wrapper.jar no encontrado"
    exit 1
fi
""")
    os.chmod(gradlew_path, 0o755)
    print("  ✅ gradlew")

    print(f"\n✅ Proyecto creado exitosamente en: {project_dir}")
    return project_dir

if __name__ == "__main__":
    create_project()