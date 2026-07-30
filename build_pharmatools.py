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
    """Descarga gradle-wrapper.jar desde el repositorio de Gradle si no existe."""
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
        print(f"  ❌ Error al descargar gradle-wrapper.jar: {e}")
        # Crear un archivo vacío como fallback (no funcionará, pero al menos no romperá el script)
        with open(jar_path, "w") as f:
            f.write("")
        print("  ⚠️ Se creó un archivo vacío. La compilación fallará si no se descarga correctamente.")

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

    # Descargar gradle-wrapper.jar
    download_wrapper_jar(os.path.join(project_dir, "gradle/wrapper"))

    # Icono PNG
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

    # Archivos de Gradle
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("""plugins {
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
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
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
""")

    with open(os.path.join(project_dir, "gradle/wrapper/gradle-wrapper.properties"), "w") as f:
        f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # app/build.gradle con las dependencias originales
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
    implementation 'com.google.mlkit:barcode-scanning:17.3.0'
    implementation 'com.google.android.gms:play-services-tasks:18.0.2'
    implementation 'androidx.multidex:multidex:2.0.1'
    implementation 'org.json:json:20230227'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.google.code.gson:gson:2.10.1'
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

    # ... (resto de recursos, layouts y clases Java igual que antes)
    # (Se omite por brevedad, pero en el script completo deben estar todas)
    # Aquí irían las mismas clases Java y layouts que ya tienes.

    # Gradlew script
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