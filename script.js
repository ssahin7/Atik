// === MODAL KONTROL ===
function openModal(type) {
    document.getElementById('blur-background').style.display = 'block';
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('register-modal').style.display = 'none';
    document.getElementById('profile-modal').style.display = 'none';

    if (type === 'login') {
        document.getElementById('login-modal').style.display = 'block';
    } else if (type === 'register') {
        document.getElementById('register-modal').style.display = 'block';
    } else if (type === 'profile') {
        document.getElementById('profile-modal').style.display = 'block';
        loadProfile();
    }
}

function closeModal() {
    document.getElementById('blur-background').style.display = 'none';
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('register-modal').style.display = 'none';
    document.getElementById('profile-modal').style.display = 'none';
}

// === GİRİŞ ===
function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            closeModal();
            document.querySelector("button[onclick=\"openModal('login')\"]").style.display = "none";
            document.querySelector("button[onclick=\"openModal('register')\"]").style.display = "none";
            document.getElementById("profile-btn").style.display = "inline-flex";
        }
    });
}

// === KAYIT ===
function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const password2 = document.getElementById('register-password2').value;
    const company = document.getElementById('register-company').value;
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    const address = document.getElementById('register-address').value;

    if (!username || !password || !password2 || !company || !email || !phone || !address) {
        alert('Lütfen tüm alanları doldurunuz.');
        return;
    }

    if (password !== password2) {
        alert('Şifreler uyuşmuyor.');
        return;
    }

    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            username, password, password2, company, email, phone, address
        }).toString()
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            closeModal();
            openModal('login');
        }
    })
    .catch(error => {
        console.error('Kayıt hatası:', error);
    });
}

// === PROFİL YÜKLE ===
function loadProfile() {
    fetch('/get_profile')
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('profile-company').value = data.company || "";
            document.getElementById('profile-email').value = data.email || "";
            document.getElementById('profile-phone').value = data.phone || "";
            document.getElementById('profile-address').value = data.address || "";
            document.getElementById('profile-tax-no').value = data.vergi_no || "";
            document.getElementById('profile-sicil-no').value = data.sicil_no || "";
            document.getElementById('profile-web').value = data.web || "";
            document.getElementById('profile-earsiv').value = data.earsiv || "";
            document.getElementById('profile-nace').value = data.nace || "";
        } else {
            alert("Profil bilgisi alınamadı: " + data.message);
        }
    });
}

// === PROFİL GÜNCELLE ===
function updateProfile() {
    const body = new URLSearchParams({
        company: document.getElementById('profile-company').value,
        email: document.getElementById('profile-email').value,
        phone: document.getElementById('profile-phone').value,
        address: document.getElementById('profile-address').value,
        vergi_no: document.getElementById('profile-tax-no').value,
        sicil_no: document.getElementById('profile-sicil-no').value,
        web: document.getElementById('profile-web').value,
        earsiv: document.getElementById('profile-earsiv').value,
        nace: document.getElementById('profile-nace').value
    });

    fetch('/update_profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('✅ Profil başarıyla güncellendi!');
            closeModal();
        } else {
            alert('❌ Profil güncellenemedi: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Güncelleme hatası:', error);
        alert('Sunucu hatası oluştu.');
    });
}

// === ATIK ARAMA ===
function searchWaste() {
    const query = document.getElementById('waste_input').value;
    if (!query) {
        alert('Lütfen atık türü veya kodu girin.');
        return;
    }

    fetch('/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `query=${encodeURIComponent(query)}`
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '';

        if (data.message) {
            resultDiv.innerText = data.message;
        } else {
            data.forEach(item => {
                const p = document.createElement('p');
                p.innerHTML = `
                    <b>Atık Kodu:</b> ${item['Atık Kodu'] ?? '-'}<br>
                    <b>Atık Açıklaması:</b> ${item['Atık Açıklaması'] ?? '-'}<br>
                    <b>NACE Kodu:</b> ${item['NACE Kodu'] ?? '-'}<br>
                    <b>NACE Açıklaması:</b> ${item['NACE Açıklaması'] ?? '-'}<br><hr>`;
                resultDiv.appendChild(p);
            });
        }
    })
    .catch(error => {
        console.error('Arama hatası:', error);
    });
}

function firmalariGoster() {
    const atikKodu = document.getElementById('waste_input').value;
    const adres = document.getElementById('profile-address').value;

    if (!atikKodu || !adres) {
        alert("Lütfen atık kodu ve profil adresinizi girin.");
        return;
    }

    fetch('/tahmin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `atik_kodu=${encodeURIComponent(atikKodu)}&adres=${encodeURIComponent(adres)}`
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "";

        if (data.success) {
            resultDiv.innerHTML = `
                <h3>Önerilen Firma:</h3>
                <div style="border:1px solid #ccc;padding:10px;margin:10px;">
                    <b>${data.firma}</b><br>
                    📍 ${data.adres}<br>
                    ⭐ Puan: ${data.puan}<br>
                    🌿 Karbon Ayak İzi: ${data.karbon}<br>
                    📏 Mesafe: ${data.mesafe} km<br>
                    🔗 Eşleşme Oranı: ${data.eslesme}%
                </div>`;
        } else {
            resultDiv.innerHTML = `<p style="color: red;">❌ ${data.message}</p>`;
        }
    })
    .catch(error => {
        console.error("Tahmin hatası:", error);
        alert("Sunucu hatası oluştu.");
    });
}
function openCompanyList() {
    const atikKodu = prompt("Lütfen aramak istediğiniz atık kodunu girin:");
    if (!atikKodu) return;

    fetch('/isletmeler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `atik_kodu=${encodeURIComponent(atikKodu)}`
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById("recommendation-result");
        resultDiv.innerHTML = "";

        if (data.success) {
            let html = `<h3>Bu atıkla ilgili işletmeler:</h3>`;
            data.firmalar.forEach(firma => {
                html += `
                    <div style="border:1px solid #ccc; margin:10px; padding:10px;">
                        <b>${firma.firma_adi || "Firma Adı Yok"}</b><br>
                        🏢 Adres: ${firma.adres || "-"}<br>
                        ♻️ Atık Kodu: ${firma.waste || "-"}<br>
                        📞 Telefon: ${firma.telefon || "-"}
                    </div>`;
            });
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<p style="color:red;">❌ ${data.message}</p>`;
        }
    })
    .catch(error => {
        console.error("İşletme getirme hatası:", error);
        alert("Sunucu hatası oluştu.");
    });
}
