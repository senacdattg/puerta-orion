#!/bin/sh
set -e

: "${VITE_API_URL:=auto}"

RUNTIME_DIR="/usr/share/nginx/html/config"
RUNTIME_FILE="${RUNTIME_DIR}/runtime-config.js"

mkdir -p "${RUNTIME_DIR}"

cat <<EOF > "${RUNTIME_FILE}"
(function () {
  const envApiUrl = "${VITE_API_URL}";
  const hostname = window.location.hostname;
  const isLocalhost = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "[::1]" || hostname === "::1";

  let apiUrl = envApiUrl;

  if (!apiUrl || apiUrl === "auto" || apiUrl === "undefined" || apiUrl === "null") {
    apiUrl = isLocalhost ? "http://localhost:5000" : "http://backend:5000";
  }

  window.RUNTIME_CONFIG = {
    VITE_API_URL: apiUrl
  };
})();
EOF

exec "$@"

