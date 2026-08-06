# PharmaTools Inventario

Aplicación Android para el **inventario de una farmacia**. Permite registrar productos, controlar stock mínimo, escanear códigos de barras y buscar artículos de forma local.

## Características

- Registro y edición de productos (nombre, categoría, precio, cantidad y stock mínimo).
- Alerta visual de **stock bajo** cuando la cantidad cae por debajo del mínimo.
- **Escaneo de códigos de barras** con `play-services-code-scanner`.
- Búsqueda en tiempo real por nombre o código.
- Persistencia local con **Room (SQLite)**.

## Stack

- Kotlin
- Material Design 3
- Room + Coroutines
- Google Play Services Code Scanner
- Gradle 8.2 / AGP 8.1 / JDK 17

## Compilar

### Local (Android Studio)

Abre la carpeta `PharmaTools_Inventario/` como proyecto y ejecuta el módulo `app` en un dispositivo/emulador (Android 8.0+, API 26+).

### CI (GitHub Actions)

Cada push a `main` ejecuta el workflow `.github/workflows/build.yml`, que compila la APK debug y la deja disponible como *artifact* descargable en el run.

Para disparar manualmente: **Actions → Build PharmaTools APK → Run workflow**.

## Estructura

```
app/src/main/java/com/pharmatools/inventario/
├── data/        # Room: Product, ProductDao, AppDatabase y Repositorio
├── ui/          # ViewModel, Adapter del RecyclerView
└── MainActivity # Pantalla principal, diálogos y escáner
```

## Licencia

Sin licencia definida. Ver [LICENSE](LICENSE) cuando se agregue.