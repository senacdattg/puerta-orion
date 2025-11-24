(function () {
  const hostname = globalThis.location.hostname || '';
  const protocol = globalThis.location.protocol || 'http:';
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]' || hostname === '::1';

  let apiUrl;

  if (isLocalhost) {
    apiUrl = 'http://localhost:5000';
  } else if (hostname) {
    apiUrl = protocol + '//' + hostname;
  } else {
    apiUrl = 'http://localhost:5000';
  }

  globalThis.RUNTIME_CONFIG = {
    VITE_API_URL: apiUrl
  };
})();
