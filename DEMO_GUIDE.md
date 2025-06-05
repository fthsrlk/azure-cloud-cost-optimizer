# DEMO GUIDE - Azure Cost Optimizer MVP
## Phase 2 Interim Demo Rehberi

---

## 🎯 DEMO HAZIRLIK CHECKLIST

### **Sistem Gereksinimleri**
- [ ] Python 3.8+ yüklü
- [ ] Tüm dependencies kurulu (`pip install -r requirements.txt`)
- [ ] Azure Service Principal credentials hazır
- [ ] İnternet bağlantısı stabil (Azure API erişimi için)
- [ ] 2 ayrı terminal window/tab açık

### **Pre-Demo Setup (5 dakika önce)**
```bash
# Terminal 1: Backend başlat
cd azure-cloud-cost-optimizer
python -m uvicorn backend.main:app --reload

# Terminal 2: Frontend başlat  
cd azure-cloud-cost-optimizer/frontend
streamlit run app.py
```

### **Test Credentials (Demo için)**
```
Subscription ID: [DEMO-SUBSCRIPTION-ID]
Tenant ID: [DEMO-TENANT-ID]  
Client ID: [DEMO-CLIENT-ID]
Client Secret: [DEMO-CLIENT-SECRET]
```

---

## 🚀 STEP-BY-STEP DEMO SCRIPT

### **ADIM 1: Demo Başlatma** ⏱️ (30 saniye)

**Action:**
```bash
# Browser'da açılacak URL'ler:
Frontend: http://localhost:8501
Backend API Docs: http://localhost:8000/docs
```

**Demo Words:**
"Uygulamamız iki bileşenden oluşuyor: kullanıcı dostu Streamlit frontend'i ve güçlü FastAPI backend'i. İki ayrı sunucu çalışıyor ve birbirleriyle REST API üzerinden konuşuyorlar."

---

### **ADIM 2: Azure Connection** ⏱️ (1 dakika)

**Actions:**
1. Streamlit sayfasında sol sidebar'ı aç
2. "🔑 Abonelik ve Service Principal Bilgileri" expander'ı aç
3. Demo credentials'ı gir:
   - Subscription ID
   - Tenant ID  
   - Client ID
   - Client Secret
4. "💾 Bilgileri Kaydet ve Kapsamlı Analizi Başlat" butonuna tıkla
5. Spinning loader'ı göster
6. Başarı mesajını bekle

**Demo Words:**
"Azure Service Principal kullanarak güvenli kimlik doğrulama yapıyoruz. Bu production-grade bir güvenlik yöntemi. Bilgileri girdikten sonra sistem otomatik olarak Azure'a bağlanıp App Service planlarını analiz etmeye başlıyor."

**Troubleshooting:**
```
Hata: "API Hatası" - Backend'in çalıştığını kontrol et
Hata: "Authentication failed" - Credentials'ı kontrol et  
Hata: "Connection timeout" - İnternet bağlantısını kontrol et
```

---

### **ADIM 3: Dashboard Metrikleri** ⏱️ (1 dakika)

**Actions:**
1. Ana dashboard'daki 4 metriği göster:
   - 🎯 Toplam Öneri
   - 💰 Potansiyel Aylık Tasarruf  
   - ⚙️ App Service Plan
   - 🎊 Yıllık Tasarruf
2. Maliyet trend grafiğini açıkla
3. Tasarruf highlight box'ını göster

**Demo Words:**
"Dashboard bize hızlı bir genel bakış sunuyor. Bu demo aboneliğinde X öneri tespit ettik ve toplam Y TL aylık tasarruf potansiyeli var. Bu 3 yılda Z TL tasarruf anlamına geliyor - oldukça önemli bir miktar!"

**Sample Data Points:**
```
Toplam Öneri: 3-5 adet
Aylık Tasarruf: ₺2,000-5,000  
App Service Plans: 2-4 adet
Yıllık Tasarruf: ₺24,000-60,000
```

---

### **ADIM 4: App Service Plan Analizleri** ⏱️ (2 dakika)

**Actions:**
1. "⚙️ App Service Plan Optimizasyon Önerileri" bölümüne scroll
2. İlk app service plan önerisini aç (expander)
3. Plan detaylarını göster:
   - Plan adı ve konum
   - Mevcut SKU
   - Problem açıklaması
   - Önerilen çözüm
   - Tasarruf miktarı
4. Konum ve resource group bilgilerini göster

**Demo Words:**
"İşte gerçek bir App Service plan analizi. Bu plan şu anda B2 SKU'da çalışıyor ama içinde hiç aktif uygulama yok. Bu tipik bir 'sahipsiz kaynak' durumu. Sistemimiş planı F1 Free tier'a taşımayı öneriyor, bu da aylık ₺3,570 tasarruf sağlar."

**Key Points:**
- Sahipsiz kaynakları nasıl tespit ettiğimizi açıkla
- SKU optimizasyon mantığını anla
- Risk analizi (düşük risk, zero downtime)

---

### **ADIM 5: İnteraktif Plan Karşılaştırması** ⏱️ (2 dakika)

**Actions:**
1. "📊 İnteraktif Plan Karşılaştırması" bölümüne scroll
2. Farklı plan butonlarını tıkla (F1, B1, B2, S1)
3. Her tıklamada değişen:
   - Plan detayları
   - Maliyet karşılaştırması
   - Tasarruf hesaplamaları
   - Plotly grafiği
4. Aylık/6 aylık/yıllık/3 yıllık projeksiyonları göster

**Demo Words:**
"Bu interaktif karşılaştırma aracı kullanıcıların farklı planları kolayca analiz etmesini sağlıyor. B2'den B1'e geçerseniz aylık ₺1,774 tasarruf sağlarsınız. Grafik size visual comparison sunuyor - yeşil barlar tasarruf, kırmızı barlar maliyet artışını gösteriyor."

**Interactive Elements:**
```
Plan seçici butonları: F1, B1, B2, S1, S2, P1V2
Maliyet grafik: Plotly interactive chart
Plan detayları: CPU, RAM, Disk, Tier bilgileri
Tasarruf calculations: Real-time hesaplama
```

---

### **ADIM 6: Güncel Fiyat Entegrasyonu** ⏱️ (1 dakika)

**Actions:**
1. Sol sidebar'da "💰 Gerçek Azure Fiyatları" expander'ı aç
2. Fiyat kaynağını göster (Microsoft Resmi API)
3. Son güncelleme tarihini göster
4. "🔄 Microsoft'tan Güncel Fiyatları Çek" butonuna tıkla
5. Güncel fiyat örneklerini göster (B1, B2, S1, P1V3)

**Demo Words:**
"En kritik özelliğimizden biri Microsoft'un resmi Azure Retail Prices API'si ile real-time entegrasyon. Sistem otomatik olarak güncel fiyatları çekiyor. 2025'te Microsoft önemli fiyat artışları yaptı - B1 planı %331 arttı! Bu yüzden optimizasyon çok daha kritik hale geldi."

**Price Examples:**
```
B1: ₺1,796/ay ($59.86 × 30 TL kuru)
B2: ₺3,570/ay ($118.99 × 30 TL kuru)  
S1: ₺2,052/ay
P1V3: ₺4,071/ay
```

---

### **ADIM 7: Manual Action Guide** ⏱️ (30 saniye)

**Actions:**
1. Herhangi bir plan önerisinde "🔧 Manuel Değişiklik Rehberi" bölümünü göster
2. Step-by-step Azure Portal talimatlarını oku
3. Süre ve risk bilgilerini vurgula

**Demo Words:**
"Sistem sadece öneri sunmuyor, kullanıcıya nasıl implement edeceğini de gösteriyor. Azure Portal'da plan değişikliği 2-5 dakika sürüyor ve zero downtime ile yapılabiliyor. Düşük riskli bir operasyon."

---

## 🔧 TROUBLESHOOTING GUIDE

### **Backend Sorunları**
```bash
Problem: "uvicorn" command not found
Çözüm: pip install uvicorn

Problem: Port 8000 already in use  
Çözüm: lsof -ti:8000 | xargs kill -9

Problem: Module import errors
Çözüm: PYTHONPATH=. python -m uvicorn backend.main:app
```

### **Frontend Sorunları**  
```bash
Problem: "streamlit" command not found
Çözüm: pip install streamlit

Problem: Port 8501 already in use
Çözüm: streamlit run app.py --server.port 8502
```

### **Azure Connection Sorunları**
```bash
Problem: "Authentication failed" 
Çözüm: Service Principal credentials'ları kontrol et

Problem: "Subscription not found"
Çözüm: Subscription ID'nin doğru olduğunu kontrol et
```

---

## 📈 DEMO METRICS TRACKER

| Metric | Target | Actual | Status |
|--------|--------|--------|---------|
| Demo Süresi | 8 dakika | ___ dakika | ⏱️ |
| API Response Time | < 3 saniye | ___ saniye | ⚡ |
| Tespit Edilen Öneriler | 3-5 adet | ___ adet | 🎯 |
| Tasarruf Potansiyeli | ₺2,000+ | ₺___ | 💰 |
| Audience Engagement | Yüksek | ___ | 👥 |

---

## 🎬 POST-DEMO ACTIONS

### **Immediate Follow-up**
- [ ] Demo feedback toplanması
- [ ] Soru-cevap session'ı
- [ ] Repository link paylaşımı
- [ ] Documentation erişimi

### **Next Steps**
- [ ] Production deployment planı
- [ ] Additional feature requests
- [ ] Security review scheduling
- [ ] Performance optimization

---

**📝 Not:** Bu demo rehberi Phase 2 interim sunumu için hazırlanmıştır. Güncel version'lar için repository'yi kontrol edin.