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

    # Archivos Gradle con repositorios extras
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("""plugins {
    id 'com.android.application' version '7.4.2' apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
        // Repositorios adicionales para Google Play Services
        maven { url 'https://dl.google.com/dl/android/maven2/' }
        maven { url 'https://maven.google.com' }
        maven { url 'https://jitpack.io' }
        maven { url 'https://repo.maven.apache.org/maven2' }
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
    // Dependencias necesarias para que funcione
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
        configurations.each { configuration ->
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

    # Recursos (igual que antes - omito por brevedad, pero deberías mantenerlos)
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

    # Layouts y Java classes (omitido por brevedad - igual que antes)
    # IMPORTANTE: Mantén el resto del código igual

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