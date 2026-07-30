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
MAC_IMPRESORA = "60:8A:10:19:48:B4"
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
        print("  ⚠️ Archivo vacío creado (la compilación fallará si no se descarga)")

def download_aar(dest_dir):
    """Descarga play-services-code-scanner.aar si no existe"""
    aar_path = os.path.join(dest_dir, "play-services-code-scanner.aar")
    if os.path.exists(aar_path) and os.path.getsize(aar_path) > 1000:
        print("  ✅ play-services-code-scanner.aar ya existe")
        return
    print("  ⬇️ Descargando play-services-code-scanner.aar...")
    os.makedirs(dest_dir, exist_ok=True)
    urls = [
        "https://maven.google.com/com/google/android/gms/play-services-code-scanner/16.1.0/play-services-code-scanner-16.1.0.aar",
        "https://repo1.maven.org/maven2/com/google/android/gms/play-services-code-scanner/16.1.0/play-services-code-scanner-16.1.0.aar",
        "https://dl.google.com/dl/android/maven2/com/google/android/gms/play-services-code-scanner/16.1.0/play-services-code-scanner-16.1.0.aar"
    ]
    for url in urls:
        try:
            urllib.request.urlretrieve(url, aar_path)
            if os.path.getsize(aar_path) > 1000:
                print(f"  ✅ AAR descargado desde {url}")
                return
        except:
            continue
    print("  ❌ No se pudo descargar el AAR - se creará un archivo vacío")
    with open(aar_path, "w") as f:
        f.write("")

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

    os.makedirs(os.path.join(project_dir, "app/src/main/java", PACKAGE_PATH))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/layout"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/values"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/drawable"))
    os.makedirs(os.path.join(project_dir, "app/src/main/res/mipmap-hdpi"))
    os.makedirs(os.path.join(project_dir, "gradle/wrapper"))
    os.makedirs(os.path.join(project_dir, "app/libs"))

    download_wrapper_jar(os.path.join(project_dir, "gradle/wrapper"))
    download_aar(os.path.join(project_dir, "app/libs"))

    # Icono
    icon_path = os.path.join(project_dir, "app/src/main/res/mipmap-hdpi", "ic_pharmatools.png")
    img = create_icon_png()
    img.save(icon_path)
    print("  ✅ ic_pharmatools.png (icono)")

    for dens in ["mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
        dest_dir = os.path.join(project_dir, "app/src/main/res", dens)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(icon_path, dest_dir)
        print(f"  ✅ ic_pharmatools.png copiado a {dens}")

    # Logo vectorial
    logo_path = os.path.join(project_dir, "app/src/main/res/drawable", "logo_pharmatools.xml")
    with open(logo_path, "w") as f:
        f.write(create_logo_xml())
    print("  ✅ logo_pharmatools.xml")

    # ===== ARCHIVOS GRADLE =====
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("""// Top-level build file
plugins {
    id 'com.android.application' version '7.4.2' apply false
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
""")

    with open(os.path.join(project_dir, "gradle/wrapper/gradle-wrapper.properties"), "w") as f:
        f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # app/build.gradle - CON AAR LOCAL
    with open(os.path.join(project_dir, "app/build.gradle"), "w") as f:
        f.write(f"""plugins {{
    id 'com.android.application'
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

    lintOptions {{
        abortOnError false
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    
    // ESCÁNER DE GOOGLE PLAY SERVICES (desde AAR local)
    implementation files('libs/play-services-code-scanner.aar')
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

    # ===== CLASES JAVA =====
    java_files = {
        "Producto.java": """
package com.pharmatools.inventario;

public class Producto {
    private String ref;
    private String art_des;
    private double prec_vta_usd;

    public Producto(String ref, String art_des, double prec_vta_usd) {
        this.ref = ref;
        this.art_des = art_des;
        this.prec_vta_usd = prec_vta_usd;
    }

    public String getRef() { return ref; }
    public String getArtDes() { return art_des; }
    public double getPrecio() { return prec_vta_usd; }
}
""",
        "DatabaseHelper.java": """
package com.pharmatools.inventario;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.util.ArrayList;
import java.util.List;

public class DatabaseHelper extends SQLiteOpenHelper {
    private static final String DB_NAME = "productos.db";
    private static final int VERSION = 1;

    public DatabaseHelper(Context context) { super(context, DB_NAME, null, VERSION); }

    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE productos (ref TEXT PRIMARY KEY, art_des TEXT, prec_vta_usd REAL)");
    }

    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS productos");
        onCreate(db);
    }

    public void sincronizarProductos(List<Producto> productos) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete("productos", null, null);
            for (Producto p : productos) {
                ContentValues cv = new ContentValues();
                cv.put("ref", p.getRef());
                cv.put("art_des", p.getArtDes());
                cv.put("prec_vta_usd", p.getPrecio());
                db.insert("productos", null, cv);
            }
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); db.close(); }
    }

    public Producto buscarPorRef(String ref) {
        SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.query("productos", null, "ref=?", new String[]{ref}, null, null, null);
        if (c != null && c.moveToFirst()) {
            return new Producto(c.getString(0), c.getString(1), c.getDouble(2));
        }
        return null;
    }

    public List<Producto> buscarProductos(String query) {
        List<Producto> resultados = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();
        String[] palabras = query.trim().split("\\\\s+");
        StringBuilder whereClause = new StringBuilder();
        List<String> args = new ArrayList<>();

        for (String palabra : palabras) {
            if (whereClause.length() > 0) whereClause.append(" AND ");
            whereClause.append("(art_des LIKE ? OR ref LIKE ?)");
            args.add("%" + palabra + "%");
            args.add("%" + palabra + "%");
        }

        Cursor c = db.query("productos", null, whereClause.toString(),
                args.toArray(new String[0]), null, null, "art_des ASC LIMIT 50");

        while (c.moveToNext()) {
            resultados.add(new Producto(c.getString(0), c.getString(1), c.getDouble(2)));
        }
        c.close(); db.close();
        return resultados;
    }

    public int getCantidadProductos() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.rawQuery("SELECT COUNT(*) FROM productos", null);
        int count = 0;
        if (c.moveToFirst()) count = c.getInt(0);
        c.close(); db.close();
        return count;
    }
}
""",
        "ApiClient.java": """
package com.pharmatools.inventario;

import android.content.Context;
import android.content.SharedPreferences;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class ApiClient {
    private static final String PREFS_NAME = "PharmatoolsPrefs";
    private static final String KEY_CO_ALMA = "co_alma";
    private static final String KEY_SERVIDOR_ID = "servidor_id";
    private static final String BASE_URL = "https://citasprevimedicaidb.com:3276/api/Art/";

    private Context context;
    private OkHttpClient client;
    private Gson gson;

    public ApiClient(Context context) {
        this.context = context;
        this.client = new OkHttpClient.Builder()
                .connectTimeout(120, TimeUnit.SECONDS)
                .readTimeout(120, TimeUnit.SECONDS)
                .writeTimeout(120, TimeUnit.SECONDS)
                .build();
        this.gson = new Gson();
    }

    private String getCoAlma() {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getString(KEY_CO_ALMA, "02");
    }

    private int getServidorId() {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getInt(KEY_SERVIDOR_ID, 1);
    }

    public List<Producto> obtenerTodosProductos() throws IOException {
        String coAlma = getCoAlma();
        int servidorId = getServidorId();
        String url = BASE_URL + "?page=1&perPage=10000&co_alma=" + coAlma + "&servidorId=" + servidorId;
        Request request = new Request.Builder().url(url).build();
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) throw new IOException("Error HTTP: " + response.code());
            String json = response.body().string();
            JsonObject root = gson.fromJson(json, JsonObject.class);
            JsonArray list = root.getAsJsonObject("result").getAsJsonArray("list");
            List<Producto> productos = new ArrayList<>();
            for (int i = 0; i < list.size(); i++) {
                JsonObject item = list.get(i).getAsJsonObject();
                productos.add(new Producto(item.get("ref").getAsString(), item.get("art_des").getAsString(), item.get("prec_vta_usd").getAsDouble()));
            }
            return productos;
        }
    }

    public Producto obtenerProductoPorRef(String ref) throws IOException {
        String coAlma = getCoAlma();
        int servidorId = getServidorId();
        String url = BASE_URL + "?page=1&perPage=1&filter=" + ref + "&co_alma=" + coAlma + "&servidorId=" + servidorId;
        Request request = new Request.Builder().url(url).build();
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) return null;
            String json = response.body().string();
            JsonObject root = gson.fromJson(json, JsonObject.class);
            if (root.get("succeeded").getAsBoolean()) {
                JsonArray list = root.getAsJsonObject("result").getAsJsonArray("list");
                if (list.size() > 0) {
                    JsonObject item = list.get(0).getAsJsonObject();
                    return new Producto(item.get("ref").getAsString(), item.get("art_des").getAsString(), item.get("prec_vta_usd").getAsDouble());
                }
            }
            return null;
        }
    }
}
""",
        "SedeApiClient.java": """
package com.pharmatools.inventario;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class SedeApiClient {
    private static final String BASE_URL = "https://citasprevimedicaidb.com:3276/api/Sucursal/ListarSedesCiudad/";
    private OkHttpClient client;
    private Gson gson;

    public SedeApiClient() {
        this.client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        this.gson = new Gson();
    }

    public List<Sede> obtenerSedes() throws IOException {
        Request request = new Request.Builder().url(BASE_URL).build();
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) throw new IOException("Error HTTP: " + response.code());
            String json = response.body().string();
            JsonArray jsonArray = gson.fromJson(json, JsonArray.class);
            List<Sede> sedes = new ArrayList<>();
            for (int i = 0; i < jsonArray.size(); i++) {
                JsonObject obj = jsonArray.get(i).getAsJsonObject();
                sedes.add(new Sede(obj.get("nombre").getAsString(), obj.get("ciudad").getAsString(),
                        obj.get("id_sucursal_ext").getAsString().trim(), obj.get("servidorId").getAsInt()));
            }
            return sedes;
        }
    }

    public static class Sede {
        public String nombre, ciudad, idSucursal;
        public int servidorId;
        public Sede(String nombre, String ciudad, String idSucursal, int servidorId) {
            this.nombre = nombre; this.ciudad = ciudad; this.idSucursal = idSucursal; this.servidorId = servidorId;
        }
    }
}
""",
        "BluetoothPrinterService.java": """
package com.pharmatools.inventario;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

public class BluetoothPrinterService {
    private static final String TAG = "BTPrinter";
    private static final UUID UUID_SPP = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private Handler handler = new Handler(Looper.getMainLooper());

    public interface Callback { void onSuccess(); void onError(String error); }

    public void print(BluetoothDevice device, String command, Callback callback) {
        new Thread(() -> {
            try (BluetoothSocket socket = device.createRfcommSocketToServiceRecord(UUID_SPP)) {
                BluetoothAdapter.getDefaultAdapter().cancelDiscovery();
                socket.connect();
                OutputStream out = socket.getOutputStream();
                out.write((command.trim() + "\\r\\n").getBytes(StandardCharsets.UTF_8));
                out.flush();
                Thread.sleep(500);
                handler.post(callback::onSuccess);
            } catch (Exception e) {
                handler.post(() -> callback.onError(e.getMessage()));
            }
        }).start();
    }
}
""",
        "TSPLGenerator.java": """
package com.pharmatools.inventario;

import java.util.ArrayList;
import java.util.List;

public class TSPLGenerator {
    private static final int ANCHO_TOTAL_DOTS = 440;
    private static final int MAX_CHARS_POR_LINEA = 32;
    private static final int DOT_POR_CAR = 12;
    private static final int OFFSET_CENTRADO_HORIZONTAL = -10;
    private static final int STEP_Y = 25;
    private static final int[] Y_BASE = {55, 40, 30, 25, 15};
    private static final int X_REF = 8, Y_REF = 182, Y_PRECIO = 150;
    private static final int OFFSET_PRECIO_HORIZONTAL = 35;
    private static final int ANCHO_DIGITO = 64, ANCHO_COMA = 38;

    public static String generar(String descripcion, double precio) {
        List<String> lineas = wrapText(descripcion, MAX_CHARS_POR_LINEA);
        if (lineas.size() > 5) lineas = lineas.subList(0, 5);
        String precioStr = String.format("%.2f", precio).replace('.', ',');
        String[] partes = precioStr.split(",");
        String entero = partes[0], decimal = partes[1];

        int anchoEntero = entero.length() * ANCHO_DIGITO;
        int anchoDecimal = 2 * ANCHO_DIGITO;
        int anchoTotalPrecio = anchoEntero + ANCHO_COMA + anchoDecimal;
        int xCentroTeorico = (ANCHO_TOTAL_DOTS - anchoTotalPrecio) / 2;
        int xEntero = xCentroTeorico + OFFSET_PRECIO_HORIZONTAL;
        int xComa = xEntero + anchoEntero;
        int xDecimal = xComa + ANCHO_COMA + 2;

        StringBuilder sb = new StringBuilder();
        sb.append("SIZE 55 mm, 40 mm\\r\\nGAP 0 mm, 0 mm\\r\\nDIRECTION 0,0\\r\\nREFERENCE 0,0\\r\\nOFFSET 0 mm\\r\\nSET TEAR ON\\r\\nCLS\\r\\n");

        int numLineas = lineas.size();
        int yBase = Y_BASE[numLineas - 1];
        for (int i = 0; i < numLineas; i++) {
            int x = (ANCHO_TOTAL_DOTS - lineas.get(i).length() * DOT_POR_CAR) / 2 + OFFSET_CENTRADO_HORIZONTAL;
            int y = yBase + i * STEP_Y;
            sb.append("TEXT ").append(x).append(",").append(y).append(",\\"2\\",0,1,1,\\"").append(lineas.get(i)).append("\\"\\r\\n");
        }

        sb.append("TEXT ").append(X_REF).append(",").append(Y_REF).append(",\\"4\\",0,1,1,\\"REF#\\"\\r\\n");
        for (int i = 0; i < 3; i++) {
            int dx = (i == 1) ? 1 : 0, dy = (i == 2) ? 1 : 0;
            sb.append("TEXT ").append(xEntero+dx).append(",").append(Y_PRECIO+dy).append(",\\"5\\",0,2,2,\\"").append(entero).append("\\"\\r\\n");
        }
        for (int i = 0; i < 3; i++) {
            int dx = (i == 1) ? 1 : 0, dy = (i == 2) ? 1 : 0;
            sb.append("TEXT ").append(xComa+dx).append(",").append(Y_PRECIO+dy).append(",\\"5\\",0,1.2,2,\\",\\"\\r\\n");
        }
        for (int i = 0; i < 3; i++) {
            int dx = (i == 1) ? 1 : 0, dy = (i == 2) ? 1 : 0;
            sb.append("TEXT ").append(xDecimal+dx).append(",").append(Y_PRECIO+dy).append(",\\"5\\",0,2,2,\\"").append(decimal).append("\\"\\r\\n");
        }
        sb.append("PRINT 1,1\\r\\n");
        return sb.toString();
    }

    public static String generarConCodigoBarras(String desc, double precio, String codigo) {
        return generar(desc, precio).replace("PRINT 1,1", "BARCODE 20,180,\\"128\\",80,1,0,2,4,\\"" + codigo + "\\"\\r\\nPRINT 1,1");
    }

    private static List<String> wrapText(String text, int maxChars) {
        List<String> lines = new ArrayList<>();
        String[] words = text.trim().split("\\\\s+");
        StringBuilder cur = new StringBuilder();
        for (String w : words) {
            if (cur.length() + w.length() + 1 <= maxChars) {
                if (cur.length() > 0) cur.append(" ");
                cur.append(w);
            } else {
                lines.add(cur.toString());
                cur = new StringBuilder(w);
            }
        }
        if (cur.length() > 0) lines.add(cur.toString());
        return lines;
    }
}
""",
        "MainActivity.java": """
package com.pharmatools.inventario;

import android.app.ProgressDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {
    private DatabaseHelper dbHelper;
    private ExecutorService executor = Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private TextView tvUltimaActualizacion;
    private Button btnSincronizar, btnControl, btnDirecto, btnConfig;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        dbHelper = new DatabaseHelper(this);
        prefs = getSharedPreferences("PharmatoolsPrefs", MODE_PRIVATE);
        tvUltimaActualizacion = findViewById(R.id.tvUltimaActualizacion);
        btnSincronizar = findViewById(R.id.btnSincronizar);
        btnControl = findViewById(R.id.btnControlEtiquetado);
        btnDirecto = findViewById(R.id.btnEtiquetado);
        btnConfig = findViewById(R.id.btnConfiguracion);
        btnSincronizar.setOnClickListener(v -> sincronizarProductos(true));
        btnControl.setOnClickListener(v -> startActivity(new Intent(this, ControlEtiquetadoActivity.class)));
        btnDirecto.setOnClickListener(v -> startActivity(new Intent(this, EtiquetadoDirectoActivity.class)));
        btnConfig.setOnClickListener(v -> startActivity(new Intent(this, ConfiguracionActivity.class)));
        mostrarUltimaActualizacion();
        if (dbHelper.getCantidadProductos() == 0) sincronizarProductos(true);
        else {
            long ultima = prefs.getLong("ultima_sincronizacion", 0);
            if (System.currentTimeMillis() - ultima > 24 * 60 * 60 * 1000) sincronizarProductos(false);
        }
    }

    private void sincronizarProductos(boolean mostrarDialogo) {
        ProgressDialog progress = null;
        if (mostrarDialogo) {
            progress = new ProgressDialog(this);
            progress.setTitle("Sincronizando");
            progress.setMessage("Descargando catálogo...");
            progress.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            progress.setCancelable(false);
            progress.show();
        }
        final ProgressDialog finalProgress = progress;
        executor.execute(() -> {
            try {
                List<Producto> productos = new ApiClient(this).obtenerTodosProductos();
                dbHelper.sincronizarProductos(productos);
                prefs.edit().putLong("ultima_sincronizacion", System.currentTimeMillis()).apply();
                runOnUiThread(() -> {
                    if (finalProgress != null) finalProgress.dismiss();
                    mostrarUltimaActualizacion();
                    Toast.makeText(MainActivity.this, "✅ " + productos.size() + " productos sincronizados", Toast.LENGTH_LONG).show();
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    if (finalProgress != null) finalProgress.dismiss();
                    Toast.makeText(MainActivity.this, "❌ Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
                });
            }
        });
    }

    private void mostrarUltimaActualizacion() {
        long fecha = prefs.getLong("ultima_sincronizacion", 0);
        tvUltimaActualizacion.setText(fecha == 0 ? "📅 Última actualización: Nunca" :
                "📅 Última actualización: " + new SimpleDateFormat("dd/MM/yyyy HH:mm:ss", Locale.getDefault()).format(new Date(fecha)));
    }
}
""",
        "ControlEtiquetadoActivity.java": """
package com.pharmatools.inventario;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.android.gms.code_scanner.GmsBarcodeScanner;
import com.google.android.gms.tasks.Task;
import com.google.mlkit.vision.barcode.common.Barcode;

import java.util.ArrayList;
import java.util.List;

public class ControlEtiquetadoActivity extends AppCompatActivity {
    private static final String PREFS_NAME = "PharmatoolsPrefs", KEY_MAC = "mac_impresora";
    private static final int CAMERA_PERMISSION_CODE = 100;
    private static final int BLUETOOTH_PERMISSION_CODE = 200;

    private DatabaseHelper dbHelper;
    private BluetoothPrinterService printerService;
    private GmsBarcodeScanner scanner;
    private TextView tvDescripcion, tvPrecio, tvEstado;
    private EditText etBusqueda;
    private ListView lvResultados;
    private Button btnOk, btnImprimir, btnVolver, btnEscanear, btnGenerarCodigo;
    private Producto ultimoProducto;
    private List<Producto> productosEncontrados = new ArrayList<>();
    private ArrayAdapter<String> adapter;
    private SharedPreferences prefs;
    private boolean isScanning = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_control_etiquetado);
        dbHelper = new DatabaseHelper(this);
        printerService = new BluetoothPrinterService();
        scanner = GmsBarcodeScanner.getInstance(this);
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        tvDescripcion = findViewById(R.id.tvDescripcion);
        tvPrecio = findViewById(R.id.tvPrecio);
        tvEstado = findViewById(R.id.tvEstado);
        etBusqueda = findViewById(R.id.etBusqueda);
        lvResultados = findViewById(R.id.lvResultados);
        btnOk = findViewById(R.id.btnOk);
        btnImprimir = findViewById(R.id.btnImprimir);
        btnVolver = findViewById(R.id.btnVolverControl);
        btnEscanear = findViewById(R.id.btnEscanearControl);
        btnGenerarCodigo = findViewById(R.id.btnGenerarCodigo);

        adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        lvResultados.setAdapter(adapter);

        etBusqueda.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { buscarProductos(s.toString()); }
            @Override public void afterTextChanged(Editable s) {}
        });

        lvResultados.setOnItemClickListener((parent, view, position, id) -> {
            Producto p = productosEncontrados.get(position);
            mostrarProducto(p);
            lvResultados.setVisibility(android.view.View.GONE);
            etBusqueda.setText("");
        });

        btnEscanear.setOnClickListener(v -> iniciarEscaneo());
        btnOk.setOnClickListener(v -> {
            if (ultimoProducto != null) { tvEstado.setText("Verificado. Escanea siguiente."); limpiarPantalla(); }
            else Toast.makeText(this, "No hay producto", Toast.LENGTH_SHORT).show();
        });
        btnImprimir.setOnClickListener(v -> {
            if (ultimoProducto != null) imprimirEtiqueta(ultimoProducto);
            else Toast.makeText(this, "No hay producto", Toast.LENGTH_SHORT).show();
        });
        btnGenerarCodigo.setOnClickListener(v -> {
            if (ultimoProducto != null) generarCodigoBarras(ultimoProducto);
            else Toast.makeText(this, "Selecciona un producto", Toast.LENGTH_SHORT).show();
        });
        btnVolver.setOnClickListener(v -> finish());
    }

    private void buscarProductos(String query) {
        if (query.length() < 2) { lvResultados.setVisibility(android.view.View.GONE); return; }
        productosEncontrados = dbHelper.buscarProductos(query);
        if (productosEncontrados.isEmpty()) {
            adapter.clear(); adapter.add("No se encontraron productos");
            lvResultados.setVisibility(android.view.View.VISIBLE); return;
        }
        List<String> opciones = new ArrayList<>();
        for (Producto p : productosEncontrados) opciones.add(p.getArtDes() + " - " + p.getRef());
        adapter.clear(); adapter.addAll(opciones);
        lvResultados.setVisibility(android.view.View.VISIBLE);
    }

    private void mostrarProducto(Producto p) {
        ultimoProducto = p;
        tvDescripcion.setText("📦 " + p.getArtDes());
        tvPrecio.setText("💰 Precio: " + String.format("%.2f", p.getPrecio()).replace('.', ','));
        tvEstado.setText("🔍 Verifica físicamente. ¿Está igual?");
        btnOk.setEnabled(true); btnImprimir.setEnabled(true); btnGenerarCodigo.setEnabled(true);
    }

    private void iniciarEscaneo() {
        if (isScanning) return;
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_CODE);
            return;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN)
                    != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{
                                Manifest.permission.BLUETOOTH_SCAN,
                                Manifest.permission.BLUETOOTH_CONNECT
                        }, BLUETOOTH_PERMISSION_CODE);
                return;
            }
        }
        isScanning = true;
        tvEstado.setText("📷 Escaneando...");
        Task<Barcode> task = scanner.startScan();
        task.addOnSuccessListener(barcode -> {
            String codigo = barcode.getRawValue();
            procesarCodigo(codigo);
            isScanning = false;
        }).addOnFailureListener(e -> {
            Toast.makeText(this, "Error al escanear: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            tvEstado.setText("❌ Error al escanear");
            isScanning = false;
        });
    }

    private void procesarCodigo(String codigo) {
        Producto p = dbHelper.buscarPorRef(codigo);
        if (p == null) { tvEstado.setText("❌ Producto no encontrado: " + codigo); limpiarPantalla(); }
        else mostrarProducto(p);
    }

    private void imprimirEtiqueta(Producto p) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.BLUETOOTH_CONNECT}, BLUETOOTH_PERMISSION_CODE);
                return;
            }
        }
        String tspl = TSPLGenerator.generar(p.getArtDes(), p.getPrecio());
        String mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4");
        try {
            BluetoothDevice device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac);
            tvEstado.setText("🖨️ Imprimiendo...");
            printerService.print(device, tspl, new BluetoothPrinterService.Callback() {
                @Override public void onSuccess() {
                    runOnUiThread(() -> { 
                        Toast.makeText(ControlEtiquetadoActivity.this, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show();
                        tvEstado.setText("✅ Etiqueta impresa. Escanea siguiente."); 
                        limpiarPantalla(); 
                    });
                }
                @Override public void onError(String error) { 
                    runOnUiThread(() -> {
                        tvEstado.setText("❌ Error: " + error);
                        Toast.makeText(ControlEtiquetadoActivity.this, "Error: " + error, Toast.LENGTH_SHORT).show();
                    });
                }
            });
        } catch (Exception e) {
            tvEstado.setText("❌ Error Bluetooth: " + e.getMessage());
            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void generarCodigoBarras(Producto p) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.BLUETOOTH_CONNECT}, BLUETOOTH_PERMISSION_CODE);
                return;
            }
        }
        String tspl = TSPLGenerator.generarConCodigoBarras(p.getArtDes(), p.getPrecio(), p.getRef());
        String mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4");
        try {
            BluetoothDevice device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac);
            tvEstado.setText("🖨️ Generando código...");
            printerService.print(device, tspl, new BluetoothPrinterService.Callback() {
                @Override public void onSuccess() {
                    runOnUiThread(() -> { 
                        Toast.makeText(ControlEtiquetadoActivity.this, "📦 Código de barras impreso", Toast.LENGTH_SHORT).show();
                        tvEstado.setText("✅ Código impreso. Escanea siguiente."); 
                        limpiarPantalla(); 
                    });
                }
                @Override public void onError(String error) { 
                    runOnUiThread(() -> {
                        tvEstado.setText("❌ Error: " + error);
                        Toast.makeText(ControlEtiquetadoActivity.this, "Error: " + error, Toast.LENGTH_SHORT).show();
                    });
                }
            });
        } catch (Exception e) {
            tvEstado.setText("❌ Error Bluetooth: " + e.getMessage());
            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void limpiarPantalla() {
        ultimoProducto = null;
        tvDescripcion.setText("");
        tvPrecio.setText("");
        btnOk.setEnabled(false); btnImprimir.setEnabled(false); btnGenerarCodigo.setEnabled(false);
        lvResultados.setVisibility(android.view.View.GONE);
        etBusqueda.setText("");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                iniciarEscaneo();
            } else {
                Toast.makeText(this, "Permiso de cámara necesario", Toast.LENGTH_SHORT).show();
            }
        } else if (requestCode == BLUETOOTH_PERMISSION_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                if (ultimoProducto != null) imprimirEtiqueta(ultimoProducto);
                else iniciarEscaneo();
            } else {
                Toast.makeText(this, "Permisos Bluetooth necesarios", Toast.LENGTH_SHORT).show();
            }
        }
    }
}
""",
        "EtiquetadoDirectoActivity.java": """
package com.pharmatools.inventario;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.android.gms.code_scanner.GmsBarcodeScanner;
import com.google.android.gms.tasks.Task;
import com.google.mlkit.vision.barcode.common.Barcode;

public class EtiquetadoDirectoActivity extends AppCompatActivity {
    private static final String PREFS_NAME = "PharmatoolsPrefs", KEY_MAC = "mac_impresora";
    private static final int CAMERA_PERMISSION_CODE = 100;
    private static final int BLUETOOTH_PERMISSION_CODE = 200;

    private DatabaseHelper dbHelper;
    private BluetoothPrinterService printerService;
    private GmsBarcodeScanner scanner;
    private TextView tvEstado;
    private Button btnVolver;
    private SharedPreferences prefs;
    private boolean isScanning = false, isPrinting = false;
    private Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_etiquetado_directo);
        dbHelper = new DatabaseHelper(this);
        printerService = new BluetoothPrinterService();
        scanner = GmsBarcodeScanner.getInstance(this);
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        tvEstado = findViewById(R.id.tvEstadoDirecto);
        btnVolver = findViewById(R.id.btnVolverDirecto);
        btnVolver.setOnClickListener(v -> finish());
        iniciarCicloEscaneo();
    }

    private void iniciarCicloEscaneo() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_CODE);
            return;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN)
                    != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{
                                Manifest.permission.BLUETOOTH_SCAN,
                                Manifest.permission.BLUETOOTH_CONNECT
                        }, BLUETOOTH_PERMISSION_CODE);
                return;
            }
        }
        tvEstado.setText("📷 Escanea un código...");
        if (isScanning) return;
        isScanning = true;
        Task<Barcode> task = scanner.startScan();
        task.addOnSuccessListener(barcode -> {
            isScanning = false;
            String codigo = barcode.getRawValue();
            procesarCodigo(codigo);
        }).addOnFailureListener(e -> {
            isScanning = false;
            tvEstado.setText("❌ Error al escanear: " + e.getMessage());
            handler.postDelayed(this::iniciarCicloEscaneo, 2000);
        });
    }

    private void procesarCodigo(String codigo) {
        Producto p = dbHelper.buscarPorRef(codigo);
        if (p == null) {
            tvEstado.setText("❌ Producto no encontrado: " + codigo);
            handler.postDelayed(this::iniciarCicloEscaneo, 2000);
            return;
        }
        tvEstado.setText("🖨️ Imprimiendo: " + p.getArtDes());
        imprimirEtiqueta(p);
    }

    private void imprimirEtiqueta(Producto p) {
        if (isPrinting) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.BLUETOOTH_CONNECT}, BLUETOOTH_PERMISSION_CODE);
                return;
            }
        }
        isPrinting = true;
        String tspl = TSPLGenerator.generar(p.getArtDes(), p.getPrecio());
        String mac = prefs.getString(KEY_MAC, "60:8A:10:19:48:B4");
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null || !adapter.isEnabled()) {
            tvEstado.setText("❌ Bluetooth no disponible");
            Toast.makeText(this, "Bluetooth no disponible", Toast.LENGTH_SHORT).show();
            isPrinting = false;
            handler.postDelayed(this::iniciarCicloEscaneo, 2000);
            return;
        }
        try {
            BluetoothDevice device = adapter.getRemoteDevice(mac);
            printerService.print(device, tspl, new BluetoothPrinterService.Callback() {
                @Override public void onSuccess() {
                    runOnUiThread(() -> {
                        Toast.makeText(EtiquetadoDirectoActivity.this, "🏷️ Etiqueta impresa", Toast.LENGTH_SHORT).show();
                        isPrinting = false;
                        tvEstado.setText("✅ Etiqueta impresa. Escanea otro.");
                        handler.postDelayed(() -> iniciarCicloEscaneo(), 1500);
                    });
                }
                @Override public void onError(String error) {
                    runOnUiThread(() -> {
                        tvEstado.setText("❌ Error: " + error);
                        Toast.makeText(EtiquetadoDirectoActivity.this, "Error al imprimir", Toast.LENGTH_SHORT).show();
                        isPrinting = false;
                        handler.postDelayed(() -> iniciarCicloEscaneo(), 2000);
                    });
                }
            });
        } catch (Exception e) {
            tvEstado.setText("❌ Error Bluetooth: " + e.getMessage());
            isPrinting = false;
            handler.postDelayed(this::iniciarCicloEscaneo, 2000);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_CODE || requestCode == BLUETOOTH_PERMISSION_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                iniciarCicloEscaneo();
            } else {
                Toast.makeText(this, "Permisos necesarios", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}
""",
        "ConfiguracionActivity.java": """
package com.pharmatools.inventario;

import android.app.ProgressDialog;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.util.ArrayList;
import java.util.List;

public class ConfiguracionActivity extends AppCompatActivity {
    private static final String PREFS_NAME = "PharmatoolsPrefs";
    private static final String KEY_SEDE = "sede_actual", KEY_CO_ALMA = "co_alma";
    private static final String KEY_SERVIDOR_ID = "servidor_id", KEY_MAC = "mac_impresora";
    private Spinner spinnerSede;
    private EditText etMacImpresora;
    private Button btnGuardar, btnVolver;
    private SharedPreferences prefs;
    private List<SedeApiClient.Sede> sedes = new ArrayList<>();
    private ArrayAdapter<String> adapter;
    private ProgressDialog progressDialog;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_configuracion);
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        spinnerSede = findViewById(R.id.spinnerSede);
        etMacImpresora = findViewById(R.id.etMacImpresora);
        btnGuardar = findViewById(R.id.btnGuardarConfig);
        btnVolver = findViewById(R.id.btnVolverConfig);
        adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>());
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerSede.setAdapter(adapter);
        btnGuardar.setOnClickListener(v -> guardarConfiguracion());
        btnVolver.setOnClickListener(v -> finish());
        cargarSedesRespaldo();
    }

    private void cargarSedesRespaldo() {
        sedes.clear();
        String[][] hardcoded = {
            {"CATEDRAL","Barquisimeto","02","1"},
            {"ESTE","Barquisimeto","03","1"},
            {"OESTE","Barquisimeto","04","1"},
            {"SAN BENITO (JEBE)","Barquisimeto","08","1"},
            {"LA FUNDACION","Barquisimeto","PRIN","3"},
            {"FARMACIA LA 21","Barquisimeto","09","1"},
            {"FARMACIA CERRITOS BLANCOS","Barquisimeto","11","1"},
            {"CLINIFARMA CABUDARE","Cabudare","01","1"},
            {"CHUCHO BRICEÑO","Cabudare","06","1"},
            {"LA MONTAÑITA","Cabudare","07","1"},
            {"PLAZA SAN PEDRO","Valera","13","1"},
            {"YARITAGUA","Yaritagua","PRIN","2"}
        };
        for (String[] s : hardcoded) {
            sedes.add(new SedeApiClient.Sede(s[0], s[1], s[2], Integer.parseInt(s[3])));
        }
        cargarSedesEnSpinner();
        cargarConfiguracionActual();
        Toast.makeText(this, "Usando lista de sedes local", Toast.LENGTH_LONG).show();
    }

    private void cargarSedesEnSpinner() {
        List<String> nombres = new ArrayList<>();
        for (SedeApiClient.Sede s : sedes) nombres.add(s.nombre + " (" + s.ciudad + ")");
        adapter.clear(); adapter.addAll(nombres); adapter.notifyDataSetChanged();
    }

    private void cargarConfiguracionActual() {
        String sedeActual = prefs.getString(KEY_SEDE, "CATEDRAL");
        etMacImpresora.setText(prefs.getString(KEY_MAC, "60:8A:10:19:48:B4"));
        for (int i = 0; i < sedes.size(); i++) {
            if (sedes.get(i).nombre.equals(sedeActual)) { spinnerSede.setSelection(i); break; }
        }
    }

    private void guardarConfiguracion() {
        int pos = spinnerSede.getSelectedItemPosition();
        if (pos < 0) { Toast.makeText(this, "Selecciona una sede", Toast.LENGTH_SHORT).show(); return; }
        SedeApiClient.Sede sede = sedes.get(pos);
        String mac = etMacImpresora.getText().toString().trim();
        if (mac.isEmpty()) { Toast.makeText(this, "Ingresa la MAC", Toast.LENGTH_SHORT).show(); return; }
        if (!mac.matches("^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")) {
            Toast.makeText(this, "MAC inválida. Ej: 60:8A:10:19:48:B4", Toast.LENGTH_SHORT).show(); return;
        }
        int servidorId = sede.nombre.equals("YARITAGUA") ? 2 : sede.nombre.equals("LA FUNDACION") ? 3 : 1;
        SharedPreferences.Editor editor = prefs.edit();
        editor.putString(KEY_SEDE, sede.nombre);
        editor.putString(KEY_CO_ALMA, sede.idSucursal);
        editor.putInt(KEY_SERVIDOR_ID, servidorId);
        editor.putString(KEY_MAC, mac);
        editor.apply();
        new AlertDialog.Builder(this)
            .setTitle("✅ Configuración guardada")
            .setMessage("Sede: " + sede.nombre + "\\nServidor ID: " + servidorId + "\\nMAC: " + mac +
                "\\n\\n📌 RECUERDA:\\n• La impresora debe estar EMPAREJADA por Bluetooth\\n• El PIN es: 0000")
            .setPositiveButton("Entendido", (d,w) -> finish())
            .setCancelable(false).show();
    }
}
"""
    }

    for fname, content in java_files.items():
        path = os.path.join(project_dir, "app/src/main/java", PACKAGE_PATH, fname)
        with open(path, "w") as f:
            f.write(content.strip())
        print(f"  ✅ {fname}")

    # gradlew
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

    print(f"\n✅ Proyecto creado en: {project_dir}")
    return project_dir

if __name__ == "__main__":
    create_project()