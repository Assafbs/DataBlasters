function Redirect(path) {
  document.cookie = 'allowAccess=true'
  window.location.href = path;
}