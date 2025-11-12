(function () {
  const hostname = window.location.hostname || '';
  const protocol = window.location.protocol || 'http:';
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]' || hostname === '::1';

  let apiUrl;

  if (isLocalhost) {
    apiUrl = 'http://localhost:5000';
  } else if (hostname) {
    apiUrl = protocol + '//' + hostname;
  } else {
    apiUrl = 'http://localhost:5000';
  }

  window.RUNTIME_CONFIG = {
    VITE_API_URL: apiUrl
  };
})();
