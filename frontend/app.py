import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Sayfa yapılandırması
st.set_page_config(
    page_title="Azure App Service Plan Optimizasyon Aracı",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stil Enjeksiyonu
st.markdown('''
<style>
    .stMetric {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .cost-chart-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    .solution-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stExpander {
        border: 1px solid #e0e0e0 !important;
        border-radius: 0.5rem !important;
        box-shadow: 0 0 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem !important;
    }
    .success-message { color: #28a745; font-weight: bold; }
    .error-message { color: #dc3545; font-weight: bold; }
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .savings-highlight {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
</style>
''', unsafe_allow_html=True)

# Uygulama başlığı
st.title("⚙️ Azure App Service Plan Maliyet Optimizasyon Aracı")

# Ana bilgilendirme
st.markdown('''
<div class="info-box">
    <h4>🎯 Bu Araç Ne Yapar?</h4>
    <p>Azure App Service planlarınızı analiz eder ve <strong>maliyet optimizasyon önerileri</strong> sunar:</p>
    <ul>
        <li>💰 <strong>Sahipsiz App Service planlarını</strong> tespit eder</li>
        <li>📊 <strong>Plan kullanımlarını</strong> analiz eder</li>
        <li>⚙️ <strong>SKU optimizasyonları</strong> önerir</li>
        <li>💲 <strong>Potansiyel tasarruf miktarlarını</strong> hesaplar</li>
        <li>📈 <strong>İnteraktif maliyet grafiklerini</strong> gösterir</li>
    </ul>
</div>
''', unsafe_allow_html=True)

BACKEND_URL = "http://127.0.0.1:8000"

# Session State Başlatma
if 'custom_recommendations' not in st.session_state:
    st.session_state.custom_recommendations = []
if 'credentials_stored' not in st.session_state:
    st.session_state.credentials_stored = False
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'info_message' not in st.session_state:
    st.session_state.info_message = ""
if 'total_potential_savings' not in st.session_state:
    st.session_state.total_potential_savings = 0.0
if 'current_pricing' not in st.session_state:
    st.session_state.current_pricing = {}
if 'pricing_source' not in st.session_state:
    st.session_state.pricing_source = "Varsayılan"

# Kenar Çubuğu: Azure Bağlantı Bilgileri
st.sidebar.header("⚙️ Azure Bağlantı Bilgileri")

with st.sidebar.expander("🔑 Abonelik ve Service Principal Bilgileri", expanded=not st.session_state.credentials_stored):
    subscription_id = st.text_input("Abonelik ID'si", value=st.session_state.get("subscription_id", ""))
    tenant_id = st.text_input("Kiracı ID'si (Tenant ID)", value=st.session_state.get("tenant_id", ""))
    client_id = st.text_input("Client ID (Uygulama ID)", value=st.session_state.get("client_id", ""))
    client_secret = st.text_input("Client Secret", type="password", value=st.session_state.get("client_secret", ""))

    if st.button("💾 Bilgileri Kaydet ve Analizi Başlat", type="primary"):
        if all([subscription_id, tenant_id, client_id, client_secret]):
            st.session_state.subscription_id = subscription_id
            st.session_state.tenant_id = tenant_id
            st.session_state.client_id = client_id
            st.session_state.client_secret = client_secret
            st.session_state.credentials_stored = True
            st.session_state.error_message = ""
            st.session_state.info_message = "Azure bilgileri kaydedildi. Analiz başlatılıyor..."
            st.session_state.custom_recommendations = []
            st.rerun()
        else:
            st.session_state.error_message = "Lütfen tüm Azure bağlantı bilgilerini eksiksiz girin."
            st.session_state.credentials_stored = False

# API fonksiyonları
def get_credentials_payload():
    return {
        "subscription_id": st.session_state.subscription_id,
        "tenant_id": st.session_state.tenant_id,
        "client_id": st.session_state.client_id,
        "client_secret": st.session_state.client_secret
    }

def fetch_custom_recommendations():
    """Custom recommendations API'sini çağırır."""
    try:
        with st.spinner("Azure'dan optimizasyon önerileri alınıyor..."):
            response = requests.post(
                f"{BACKEND_URL}/list-custom-recommendations",
                json=get_credentials_payload(),
                timeout=30
            )
            response.raise_for_status()
            st.session_state.custom_recommendations = response.json()
            st.session_state.error_message = ""
            calculate_potential_savings()
    except requests.exceptions.RequestException as e:
        handle_api_error(e, "Azure önerileri alınırken")

def calculate_potential_savings():
    """Toplam potansiyel tasarruf hesaplar."""
    total_savings = 0.0
    
    for rec in st.session_state.custom_recommendations:
        extended_props = rec.get('extended_properties', {})
        estimated_cost = extended_props.get('estimated_monthly_cost_usd', 0)
        if estimated_cost:
            total_savings += estimated_cost
    
    st.session_state.total_potential_savings = total_savings * 30  # USD to TRY conversion

def handle_api_error(e, context_message):
    """API hatalarını düzenli şekilde işler."""
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_detail = e.response.json().get('detail', str(e))
        except:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
    else:
        error_detail = str(e)
    
    st.session_state.error_message = f"{context_message} hata oluştu: {error_detail}"
    st.session_state.info_message = ""

def fetch_current_pricing(region="westeurope"):
    """Güncel Azure fiyatlarını çeker."""
    try:
        with st.spinner("Microsoft'tan güncel fiyatlar çekiliyor..."):
            response = requests.get(f"{BACKEND_URL}/get-current-pricing/{region}", timeout=30)
            response.raise_for_status()
            
            pricing_data = response.json()
            
            if pricing_data.get("success", False):
                st.session_state.current_pricing = pricing_data.get("pricing", {})
                st.session_state.pricing_source = pricing_data.get("source", "API")
                st.session_state.pricing_last_updated = pricing_data.get("updated_at")
                st.success("✅ Güncel fiyatlar başarıyla yüklendi!")
            else:
                st.session_state.current_pricing = pricing_data.get("pricing", {})
                st.session_state.pricing_source = pricing_data.get("source", "Fallback")
                st.warning("⚠️ API'den fiyat alınamadı, varsayılan fiyatlar kullanılıyor.")
                
    except Exception as e:
        st.error(f"Fiyat bilgileri alınırken hata: {str(e)}")

# Ana içerik
if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.info_message:
    st.info(st.session_state.info_message)

# Azure bilgileri kaydedildiyse analiz yap
if st.session_state.credentials_stored:
    if not st.session_state.custom_recommendations:
        fetch_custom_recommendations()
    
    # Güncel fiyatları yükle
    if not st.session_state.current_pricing:
        fetch_current_pricing()
    
    # Dashboard metrikleri
    st.markdown("## 📊 Dashboard Metrikleri")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        recommendation_count = len(st.session_state.custom_recommendations)
        st.metric(
            label="🎯 Toplam Öneri",
            value=recommendation_count,
            help="Tespit edilen optimizasyon önerisi sayısı"
        )
    
    with col2:
        st.metric(
            label="💰 Potansiyel Aylık Tasarruf",
            value=f"₺{st.session_state.total_potential_savings:,.0f}",
            help="Öneriler uygulandığında elde edilebilecek aylık tasarruf"
        )
    
    with col3:
        app_service_plans = len([r for r in st.session_state.custom_recommendations if r.get('category') == 'Cost_Custom_AppServicePlan'])
        st.metric(
            label="⚙️ App Service Plan",
            value=app_service_plans,
            help="Optimizasyona ihtiyaç duyan App Service planı sayısı"
        )
    
    with col4:
        yearly_savings = st.session_state.total_potential_savings * 12
        st.metric(
            label="🎊 Yıllık Tasarruf",
            value=f"₺{yearly_savings:,.0f}",
            help="Yıllık tasarruf potansiyeli"
        )
    
    # Tasarruf özetini göster
    if st.session_state.total_potential_savings > 0:
        st.markdown(f'''
        <div class="savings-highlight">
            <h4>💰 Tasarruf Potansiyeli</h4>
            <p>Öneriler uygulandığında:</p>
            <ul>
                <li><strong>Aylık tasarruf:</strong> ₺{st.session_state.total_potential_savings:,.0f}</li>
                <li><strong>Yıllık tasarruf:</strong> ₺{yearly_savings:,.0f}</li>
                <li><strong>3 yıllık tasarruf:</strong> ₺{yearly_savings * 3:,.0f}</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    # App Service Plan önerileri
    if st.session_state.custom_recommendations:
        st.markdown("## ⚙️ App Service Plan Optimizasyon Önerileri")
        
        app_service_recs = [r for r in st.session_state.custom_recommendations if r.get('category') == 'Cost_Custom_AppServicePlan']
        
        if app_service_recs:
            for i, rec in enumerate(app_service_recs):
                with st.expander(f"📋 {rec.get('name', 'Unknown')} - {rec.get('short_description_problem', '')}", expanded=i == 0):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**🔍 Problem:** {rec.get('short_description_problem', 'N/A')}")
                        st.markdown(f"**💡 Çözüm:** {rec.get('short_description_solution', 'N/A')}")
                        
                        extended_props = rec.get('extended_properties', {})
                        if extended_props:
                            st.markdown("**📊 Teknik Detaylar:**")
                            st.markdown(f"- Mevcut SKU: `{extended_props.get('current_sku', 'N/A')}`")
                            st.markdown(f"- Mevcut Tier: `{extended_props.get('current_tier', 'N/A')}`")
                            st.markdown(f"- Önerilen SKU: `{extended_props.get('recommended_sku', 'N/A')}`")
                            st.markdown(f"- Önerilen Tier: `{extended_props.get('recommended_tier', 'N/A')}`")
                            st.markdown(f"- Uygulama sayısı: {extended_props.get('apps_count', 0)}")
                    
                    with col2:
                        potential_benefit = rec.get('potential_benefits', 'N/A')
                        st.markdown(f'''
                        <div class="solution-box">
                            <h5>💰 Tasarruf</h5>
                            <p>{potential_benefit}</p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Konum ve resource group bilgileri
                        resource_metadata = rec.get('resource_metadata', {})
                        if resource_metadata:
                            st.markdown("**📍 Konum Bilgileri:**")
                            st.markdown(f"- Bölge: `{resource_metadata.get('location', 'N/A')}`")
                            st.markdown(f"- Resource Group: `{resource_metadata.get('resource_group', 'N/A')}`")
        else:
            st.success("🎉 Tüm App Service planlarınız optimal durumda!")
    
    # Fiyat bilgileri
    with st.sidebar.expander("💰 Gerçek Azure Fiyatları", expanded=False):
        st.markdown(f"**Kaynak:** {st.session_state.pricing_source}")
        if st.session_state.pricing_last_updated:
            st.markdown(f"**Son Güncelleme:** {st.session_state.pricing_last_updated[:19]}")
        
        if st.button("🔄 Microsoft'tan Güncel Fiyatları Çek"):
            fetch_current_pricing()
        
        if st.session_state.current_pricing:
            st.markdown("**Güncel Fiyat Örnekleri (TL/ay):**")
            sample_skus = ["B1", "B2", "S1", "P1V3"]
            for sku in sample_skus:
                if sku in st.session_state.current_pricing:
                    price = st.session_state.current_pricing[sku].get("price", 0)
                    st.markdown(f"- {sku}: ₺{price:,.0f}")

else:
    st.markdown('''
    <div class="info-box">
        <h4>🚀 Başlamak için:</h4>
        <ol>
            <li>Sol menüden <strong>Azure Service Principal bilgilerinizi</strong> girin</li>
            <li><strong>"Analizi Başlat"</strong> butonuna tıklayın</li>
            <li>Sistem otomatik olarak <strong>optimizasyon önerilerinizi</strong> hazırlayacak</li>
        </ol>
        <p><strong>💡 İpucu:</strong> Service Principal oluşturmak için Azure CLI kullanabilirsiniz:</p>
        <code>az ad sp create-for-rbac --name "CostOptimizerApp" --role "Reader"</code>
    </div>
    ''', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>Azure Bulut Maliyet Optimizasyon Aracı v2.0 | 
    FastAPI + Streamlit | 
    Microsoft Azure Retail Prices API Entegrasyonu</p>
</div>
''', unsafe_allow_html=True)