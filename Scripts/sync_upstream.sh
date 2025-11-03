git checkout main
git merge --no-edit upstream/main || true
#!/usr/bin/env bash
# Script para sincronizar main con upstream/main y empujar a origin
# Añade comprobaciones interactivas:
# - Si hay cambios sin commitear, ofrece stashearlos automáticamente.
# - Si hay commits locales que no están en upstream/main avisa antes de continuar.
# Uso: desde la raíz del repositorio: ./Scripts/sync_upstream.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Haciendo git fetch upstream..."
git fetch upstream

echo "Cambiando a rama main..."
git checkout main

# Comprobar cambios no committeados
STASHED=0
if ! git diff-index --quiet HEAD --; then
	echo "Hay cambios sin commitear en el árbol de trabajo."
	read -r -p "¿Deseas stashearlos automáticamente antes de sincronizar? [s/N]: " answer
	case "$answer" in
		[sS]|[yY])
			git stash push -u -m "auto-stash before sync_upstream.sh"
			STASHED=1
			echo "Cambios stasheados." ;;
		*)
			echo "Abortando. Haz commit o stash manualmente y vuelve a ejecutar.";
			exit 1 ;;
	esac
fi

# Comprobar si hay commits locales que no están en upstream/main
COUNTS=$(git rev-list --left-right --count main...upstream/main 2>/dev/null || echo "0 0")
LOCAL_AHEAD=$(echo "$COUNTS" | awk '{print $1}')
REMOTE_AHEAD=$(echo "$COUNTS" | awk '{print $2}')

if [ "$LOCAL_AHEAD" -gt 0 ]; then
	echo "Tu rama local 'main' tiene $LOCAL_AHEAD commits que no están en upstream/main."
	read -r -p "¿Deseas continuar con el merge igual? Esto puede crear un merge commit. [s/N]: " proceed
	case "$proceed" in
		[sS]|[yY])
			echo "Continuando con el merge..." ;;
		*)
			echo "Abortando sincronización.";
			if [ "$STASHED" -eq 1 ]; then
				echo "Restaurando stash..."
				git stash pop || true
			fi
			exit 1 ;;
	esac
fi

echo "Haciendo merge de upstream/main en main..."
# Intentar fast-forward/merge
git merge --no-edit upstream/main || true

if [ "$STASHED" -eq 1 ]; then
	echo "Aplicando stash guardado..."
	git stash pop || echo "No se pudo aplicar el stash automáticamente. Resuélvelo manualmente.";
fi

echo "Empujando main a origin..."
git push origin main

echo "Sincronización completa."
