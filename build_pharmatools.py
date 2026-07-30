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

    download_wrapper_jar(os.path.join(project_dir, "gradle/wrapper"))

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

    # Archivos Gradle
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("""plugins {
    id 'com.android.application' version '7.4.2' apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url 'https://dl.google.com/dl/android/maven2/' }
        maven { url 'https://maven.google.com' }
        maven { url 'https://jitpack.io' }
    }
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
        maven {{ url 'https://dl.google.com/dl/android/maven2/' }}
        maven {{ url 'https://maven.google.com' }}
        maven {{ url 'https://jitpack.io' }}
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
        maven {{ url 'https://dl.google.com/dl/android/maven2/' }}
        maven {{ url 'https://maven.google.com' }}
        maven {{ url 'https://jitpack.io' }}
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

    # app/build.gradle - CON PLAY SERVICES
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

// Forzar la descarga de dependencias
task forceDownloadDependencies {{
    doLast {{
        configurations.each {{ configuration ->
            if (configuration.name.contains('compile') || configuration.name.contains('implementation')) {{
                try {{
                    configuration.resolve()
                }} catch (Exception e) {{
                    println "Error al resolver configuración: ${{configuration.name}}"
                }}
            }}
        }}
    }}
}}
""")

    # AndroidManifest.xml
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

    # Recursos values
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

    # Layouts
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

    public void print(BluetoothDevice device, String command, Callback