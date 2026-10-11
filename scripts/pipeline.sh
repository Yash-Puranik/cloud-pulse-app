#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_ROOT}"

if [ -z "${VIRTUAL_ENV:-}" ] && [ -f ".venv/bin/activate" ]; then
    echo ">>> Activating local virtual environment (.venv)..."
    source .venv/bin/activate
fi

APP_NAME="cloud-pulse"
IMG_TAG="local"
IMG_NAME="${APP_NAME}:${IMG_TAG}"
HOST_PORT="8080"
CONT_PORT="8080"
HEALTH="http://127.0.0.1:${HOST_PORT}/health"
HEALTH_INTERVAL_SECONDS=1

echo ">>> [STAGE 1/6] Initialized configuration for ${APP_NAME}."

echo ">>> [STAGE 2/6] Running pre-flight system checks..."

if ! docker info > /dev/null 2>&1; then
	echo "ERROR: Docker daemon is not running or current user lacks docker group permissions."
	exit 1
fi

for cmd in curl pytest docker; do
	if ! command -v "${cmd}" > /dev/null 2>&1; then
	echo "Required tool:'${cmd}' not found!"
	exit 1
	fi
done

echo ">>> [STAGE 3/6] Running unit tests via pytest..."

TEST_DIR="tests/"

pytest "${TEST_DIR}" -v

echo ">>> [STAGE 4/6] Building hardened container image using BuildKit..."

export DOCKER_BUILDKIT=1

docker build -t "${IMG_NAME}" .

echo ">>> [STAGE 5/6] Managing container lifecycle and launching sandbox..."

CONTAINER_NAME="cloud-pulse-app"

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
	echo "Removing and stopping an existing container: ${CONTAINER_NAME}"
	docker rm -f "${CONTAINER_NAME}" > /dev/null 
fi

docker run -d -p "${HOST_PORT}":"${CONT_PORT}" --name "${CONTAINER_NAME}" --read-only --cap-drop=ALL --security-opt=no-new-privileges:true --tmpfs /tmp:rw,noexec,nosuid,size=64m "${IMG_NAME}" > /dev/null

echo "The container '${CONTAINER_NAME}' has started."

echo ">>> [STAGE 6/6] Verifying service availability at ${HEALTH}..."

MAX_HEALTH_ATTEMPTS=15


if ! docker ps --filter "name=^/${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[-] ERROR: Container '${CONTAINER_NAME}' is not running!"
  echo "[-] Dumping container exit code and logs:"
  docker ps -a --filter "name=^/${CONTAINER_NAME}$"
  docker logs "${CONTAINER_NAME}"
  exit 1
fi

ATTEMPTS=1
SUCCESS=0

while [ "${ATTEMPTS}" -le "${MAX_HEALTH_ATTEMPTS}" ]; do
	http_code=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH}") 

	if [ "${http_code}" -eq 200 ]; then
		echo "SUCCESS: Service is healthy (HTTP 200) after ${ATTEMPTS} attempt(s)!"
		SUCCESS=1
		break
	else
		echo "FAIL: Service is not healthy after ${ATTEMPTS}"
		sleep "${HEALTH_INTERVAL_SECONDS}"
		ATTEMPTS=$((ATTEMPTS+1))
		
	fi
done

if [ "${SUCCESS}" -ne 1 ]; then
	echo "ERROR: Health check failed after ${MAX_HEALTH_ATTEMPTS} attempts." >&2
	docker logs "${CONTAINER_NAME}" > /dev/null 2>&1
	exit 1
fi


echo " Pipeline execution completed successfully."
echo " Endpoint: ${HEALTH}"
echo " Container: ${CONTAINER_NAME}"
