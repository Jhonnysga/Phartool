name: opencode

on:
  workflow_dispatch:
    inputs:
      instruccion:
        description: '💬 Instrucción para OpenCode'
        required: true
        type: string
        default: 'Continúa con el proyecto. Lee el contexto en .opencode/current_context.md'

jobs:
  opencode:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    permissions:
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
          node --version
          npm list -g --depth=0

      # ============================================================
      # PASO 4: Iniciar OmniRoute y configurar OpenCode
      # ============================================================
      - name: 🚀 Start OmniRoute and configure OpenCode
        run: |
          # Iniciar OmniRoute en segundo plano
          omniroute &
          
          # Esperar a que OmniRoute esté listo
          echo "⏳ Esperando a que OmniRoute esté listo..."
          sleep 10
          
          # Verificar que OmniRoute está corriendo
          if curl -s http://localhost:20128 > /dev/null; then
            echo "✅ OmniRoute está corriendo"
          else
            echo "⚠️ OmniRoute no responde, pero continuamos..."
          fi
          
          # Configurar OpenCode para usar OmniRoute
          omniroute config opencode \
            --base-url http://localhost:20128 \
            --api-key "sk_omniroute"
          
          echo "✅ OmniRoute configurado correctamente"

      # ============================================================
      # PASO 5: Cargar contexto actual
      # ============================================================
      - name: 📖 Load current context
        run: |
          echo "============================================================"
          echo "📖 CONTEXTO ACTUAL DEL PROYECTO"
          echo "============================================================"
          
          # Crear estructura de contexto si no existe
          mkdir -p .opencode/prompts
          mkdir -p .opencode/sessions
          
          if [ ! -f ".opencode/current_context.md" ]; then
            echo "⚠️ No hay contexto previo. Creando estructura inicial..."
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
          fi
          
          echo ""
          cat .opencode/current_context.md
          echo ""
          echo "============================================================"

      # ============================================================
      # PASO 6: Ejecutar OpenCode con contexto
      # ============================================================
      - name: 🤖 Run OpenCode with context
        uses: anomalyco/opencode/github@latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          model: auto
          prompt: |
            ============================================================
            INSTRUCCIÓN DEL USUARIO
            ============================================================
            ${{ github.event.inputs.instruccion }}

            ============================================================
            CONTEXTO ACTUAL DEL PROYECTO
            ============================================================
            $(cat .opencode/current_context.md 2>/dev/null || echo "Sin contexto previo.")

            ============================================================
            HISTORIAL DE INSTRUCCIONES
            ============================================================
            $(cat .opencode/prompts/historial-completo.md 2>/dev/null || echo "Sin historial previo.")

            ============================================================
            TAREAS OBLIGATORIAS AL FINALIZAR
            ============================================================
            1. ACTUALIZA .opencode/current_context.md con el NUEVO estado del proyecto.
            2. AÑADE esta instrucción al historial en .opencode/prompts/historial-completo.md.
            3. Si creaste o modificaste archivos, asegúrate de que queden guardados.
            4. Actualiza el estado del proyecto si es necesario.

      # ============================================================
      # PASO 7: Guardar estado y contexto
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

          ## 📂 Archivos modificados en esta sesión
          $(git status --porcelain 2>/dev/null || echo "Sin cambios")

          ## 📊 Estadísticas
          - Fecha: $(date '+%Y-%m-%d %H:%M:%S')
          - Repositorio: ${{ github.repository }}
          - Rama: ${{ github.ref_name }}
          - Ejecución: ${{ github.run_id }}

          ## ✅ Estado final del proyecto
          $(cat .opencode/current_context.md 2>/dev/null || echo "Contexto no disponible")
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
          echo "📝 Historial actualizado: .opencode/prompts/historial-completo.md"
          echo "📖 Contexto actual: .opencode/current_context.md"
          echo "✅ Estado guardado correctamente"
          echo "============================================================"

      # ============================================================
      # PASO 8: Finalizar y mostrar resumen
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
          echo "   (gracias al workflow de build que ya tienes)"
          echo ""
          echo "📊 ESTADÍSTICAS DE LA SESIÓN"
          echo "   - Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
          echo "   - Repositorio: ${{ github.repository }}"
          echo "   - Rama: ${{ github.ref_name }}"
          echo "   - Ejecución: ${{ github.run_id }}"
          echo ""
          echo "📖 Para continuar en la próxima sesión:"
          echo "   1. Ejecuta este workflow nuevamente"
          echo "   2. Escribe tu nueva instrucción"
          echo "   3. OpenCode leerá el contexto guardado y continuará"
          echo ""
          echo "🛑 Puedes cancelar este workflow en cualquier momento"
          echo "   (los cambios ya están guardados en el repositorio)"
          echo "============================================================"