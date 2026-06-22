// Pindahkan nama admin ke navbar (pojok kanan atas)
document.addEventListener('DOMContentLoaded', function () {
    var icon = document.querySelector('#jazzy-navbar .far.fa-user');
    if (!icon) return;

    var link = icon.closest('a.nav-link');
    if (!link) return;

    var name = link.getAttribute('title');
    if (!name) return;

    var label = document.createElement('span');
    label.className = 'admin-username';
    label.textContent = ' ' + name;
    label.style.marginLeft = '4px';
    label.style.fontSize = '14px';

    link.appendChild(label);
});