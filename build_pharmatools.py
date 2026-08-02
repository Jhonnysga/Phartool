name: opencode

on:
  workflow_dispatch:
    inputs:
      instruccion:
        description: '💬 Instrucción para OpenCode'
        required: true
        type: string
        default: 'Continúa con el proyecto'

jobs:
  opencode:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    permissions:
      id-token: write
      contents: write
      pull-requests: write
      issues: write

    steps:
      # ============================================================
      # PASO 1: Clonar repositorio
      # ============================================================
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # ============================================================
      # PASO 2: Instalar Node.js 20 LTS
      # ============================================================
      - name: 🟢 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      # ============================================================
      # PASO 3: Instalar OpenCode + OmniRoute
      # ============================================================
      - name: 📦 Install OpenCode and OmniRoute
        run: |
          npm install -g opencode-ai omniroute
          echo "✅ OpenCode y OmniRoute instalados"

      # ============================================================
      # PASO 4: Iniciar OmniRoute
      # ============================================================
      - name: 🚀 Start OmniRoute
        run: |
          echo "⏳ Iniciando OmniRoute..."
          omniroute &
          sleep 10
          echo "✅ OmniRoute iniciado en http://localhost:20128"

      # ============================================================
      # PASO 5: Configurar OpenCode usando el comando correcto
      # ============================================================
      - name: 🔧 Configure OpenCode
        run: |
          echo "⏳ Configurando OpenCode para usar OmniRoute..."
          
          # Agregar OmniRoute como proveedor
          opencode providers add omniroute \
            --base-url http://localhost:20128/v1 \
            --api-key sk_omniroute
          
          echo "✅ OpenCode configurado correctamente"
          
          # Verificar configuración
          echo ""
          echo "📄 Proveedores configurados:"
          opencode providers list

      # ============================================================
      # PASO 6: Cargar contexto actual
      # ============================================================
      - name: 📖 Load current context
        run: |
          echo "============================================================"
          echo "📖 CONTEXTO ACTUAL DEL PROYECTO"
          echo "============================================================"
          
          mkdir -p .opencode/prompts
          mkdir -p .opencode/sessions
          
          if [ ! -f ".opencode/current_context.md" ]; then
            cat > .opencode/current_context.md << 'EOF'
          # Estado actual del proyecto

          ## 🎯 Objetivo general
          App Android para inventario de farmacia.

          ## 📝 Siguiente tarea pendiente
          Definir la estructura del proyecto Android.

          ## 📂 Archivos clave
          - (Pendiente de definir)

          ## 🧠 Notas
          - Usar Material Design.
          - Base de datos SQLite local.
          EOF
            echo "✅ Contexto inicial creado"
          fi
          
          echo ""
          cat .opencode/current_context.md
          echo ""

      # ============================================================
      # PASO 7: Ejecutar OpenCode con contexto
      # ============================================================
      - name: 🤖 Run OpenCode with context
        uses: anomalyco/opencode/github@latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          model: omniroute/auto/best-coding
          prompt: |
            INSTRUCCIÓN DEL USUARIO:
            ${{ github.event.inputs.instruccion }}

            CONTEXTO ACTUAL DEL PROYECTO:
            $(cat .opencode/current_context.md 2>/dev/null || echo "Sin contexto previo.")

            HISTORIAL DE INSTRUCCIONES:
            $(cat .opencode/prompts/historial-completo.md 2>/dev/null || echo "Sin historial previo.")

            TAREAS OBLIGATORIAS AL FINALIZAR:
            1. ACTUALIZA .opencode/current_context.md con el nuevo estado del proyecto.
            2. AÑADE esta instrucción al historial en .opencode/prompts/historial-completo.md.

      # ============================================================
      # PASO 8: Guardar estado y contexto
      # ============================================================
      - name: 💾 Save session state
        run: |
          echo "============================================================"
          echo "💾 Guardando estado de la sesión"
          echo "============================================================"
          
          # Guardar instrucción en el historial
          echo "## $(date '+%Y-%m-%d %H:%M') - Sesión" >> .opencode/prompts/historial-completo.md
          echo "${{ github.event.inputs.instruccion }}" >> .opencode/prompts/historial-completo.md
          echo "" >> .opencode/prompts/historial-completo.md

          # Guardar resumen de la sesión
          SESSION_FILE=".opencode/sessions/$(date '+%Y-%m-%d_%H-%M')_session.md"
          cat > $SESSION_FILE << EOF
          # Sesión del $(date '+%Y-%m-%d %H:%M')

          ## 📝 Instrucción recibida
          ${{ github.event.inputs.instruccion }}

          ## 📂 Archivos modificados
          $(git status --porcelain 2>/dev/null || echo "Sin cambios")

          ## ✅ Estado final
          Fecha: $(date '+%Y-%m-%d %H:%M:%S')
          EOF

          # Configurar usuario de git
          git config user.name "OpenCode Bot"
          git config user.email "opencode@pharmatools.local"

          # Hacer commit de todos los cambios
          git add .opencode/ . || true
          git add . || true
          
          if git diff --staged --quiet; then
            echo "✅ No hay cambios nuevos para commit"
          else
            git commit -m "🧠 [OpenCode] Sesión $(date '+%Y-%m-%d %H:%M') - ${{ github.event.inputs.instruccion }}"
            git push
            echo "✅ Cambios guardados en el repositorio"
          fi

          echo ""
          echo "============================================================"
          echo "📋 RESUMEN DE LA SESIÓN"
          echo "============================================================"
          echo "📂 Sesión guardada en: $SESSION_FILE"
          echo "📝 Historial: .opencode/prompts/historial-completo.md"
          echo "📖 Contexto: .opencode/current_context.md"
          echo "============================================================"

      # ============================================================
      # PASO 9: Finalizar
      # ============================================================
      - name: ✅ Workflow completed
        run: |
          echo ""
          echo "============================================================"
          echo "🎉 TRABAJO COMPLETADO CON ÉXITO"
          echo "============================================================"
          echo "📂 Los cambios están en tu repositorio:"
          echo "   https://github.com/${{ github.repository }}"
          echo ""
          echo "📱 La APK se compilará AUTOMÁTICAMENTE si hay cambios en 'main'"
          echo ""
          echo "📖 Para continuar en la próxima sesión:"
          echo "   1. Ejecuta este workflow nuevamente"
          echo "   2. Escribe tu nueva instrucción"
          echo "   3. OpenCode leerá el contexto guardado"
          echo "============================================================"