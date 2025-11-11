#!/bin/sh
set -e

: "${VITE_API_URL:=auto}"

RUNTIME_DIR="/usr/share/nginx/html/config"
RUNTIME_FILE="${RUNTIME_DIR}/runtime-config.js"

mkdir -p "${RUNTIME_DIR}"

cat <<EOF > "${RUNTIME_FILE}"
(function () {
  var envApiUrl = "${VITE_API_URL}";
  var hostname = window.location.hostname || "";
  var protocol = window.location.protocol || "http:";
  var isLocalhost = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "[::1]" || hostname === "::1";
  var apiUrl = envApiUrl;

  if (!apiUrl || apiUrl === "auto" || apiUrl === "undefined" || apiUrl === "null") {
    if (isLocalhost) {
      apiUrl = "http://localhost:5000";
    } else if (hostname) {
      apiUrl = protocol + "//" + hostname;
    } else {
      apiUrl = "http://localhost:5000";
    }
  }

  window.RUNTIME_CONFIG = {
    VITE_API_URL: apiUrl
  };
})();
EOF

exec "$@"

