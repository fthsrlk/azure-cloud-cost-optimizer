# 🚀 Azure Bulut Maliyet Optimizasyon Aracı (MVP)

Azure App Service planlarınızı analiz ederek maliyet optimizasyonu önerileri sunan modern web uygulaması.

## 🎯 Özellikler

- **📊 Real-time Azure Fiyat Entegrasyonu**: Microsoft'un resmi Azure Retail Prices API'si ile güncel fiyat verisi
- **🔍 Otomatik Plan Analizi**: App Service planlarını analiz ederek sahipsiz kaynakları tespit etme
- **💰 Maliyet Optimizasyonu**: SKU bazlı optimizasyon önerileri ve tasarruf hesaplamaları
- **📈 İnteraktif Dashboard**: Plotly ile oluşturulmuş dinamik grafikler ve karşılaştırmalar
- **🔧 Manual Action Guide**: Azure Portal'da değişiklik yapma rehberi
- **⚡ Modern Teknoloji**: FastAPI backend + Streamlit frontend

## 🏗️ Teknoloji Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **Azure Integration**: Azure SDK, Azure Service Principal Authentication
- **Data Visualization**: Plotly, Pandas
- **API**: REST API with automatic documentation

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.8+
- Azure Service Principal (kimlik doğrulama için)
- İnternet bağlantısı (Azure API erişimi için)

### Kurulum

1. **Repository'yi klonlayın**
```bash
git clone https://github.com/fthsrlk/azure-cloud-cost-optimizer.git
cd azure-cloud-cost-optimizer
```

2. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

3. **Backend'i başlatın**
```bash
uvicorn backend.main:app --reload
```

4. **Frontend'i başlatın** (yeni terminal)
```bash
streamlit run frontend/app.py
```

5. **Tarayıcıda açın**
- Frontend: http://localhost:8501
- Backend API Docs: http://localhost:8000/docs

## 📋 Kullanım

1. **Azure Kimlik Bilgileri**: Sol sidebar'dan Azure Service Principal bilgilerinizi girin
2. **Analiz Başlatma**: "Analizi Başlat" butonuna tıklayın
3. **Sonuçları İnceleme**: Dashboard'da öneriler ve tasarruf hesaplamalarını görün
4. **Plan Karşılaştırması**: İnteraktif araçla farklı planları karşılaştırın

## 📊 Demo

Detaylı demo rehberi için [DEMO_GUIDE.md](DEMO_GUIDE.md) dosyasını inceleyin.

## 🔧 Azure Service Principal Kurulumu

Azure Service Principal oluşturmak için:

```bash
az ad sp create-for-rbac --name "CostOptimizerApp" --role "Reader" --scopes "/subscriptions/{subscription-id}"
```

## 📁 Proje Yapısı

```
azure-cloud-cost-optimizer/
├── backend/
│   ├── main.py           # FastAPI ana dosyası
│   ├── azure_client.py   # Azure SDK entegrasyonu
│   └── azure_pricing.py  # Fiyat API entegrasyonu
├── frontend/
│   └── app.py           # Streamlit frontend
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.

---

**⚡ 2025'te Azure fiyatları önemli ölçüde arttı (B1 planı %331 artış). Maliyet optimizasyonu artık daha kritik!**