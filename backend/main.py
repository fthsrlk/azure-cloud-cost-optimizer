from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from .azure_client import (
    get_unattached_public_ips,
    get_cost_details,
    get_app_service_plan_recommendations,
    update_app_service_plan_sku,
    delete_app_service_plan,
    get_azure_vms_with_cpu,
    stop_and_deallocate_vm
)

app = FastAPI(
    title="Bulut Maliyet Optimizasyon Aracı API",
    description="Özel analizlerden (örn: sahipsiz genel IP'ler, App Service Plan optimizasyonları) maliyet optimizasyon önerileri ve eylemleri API'si.",
    version="0.7.0",
)

class AzureCredentials(BaseModel):
    subscription_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    tenant_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    client_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    client_secret: str = Field(..., description="Uygulama kaydının client secret değeri.")

class CustomRecommendationResourceMetadata(BaseModel):
    resource_id: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    resource_group: Optional[str] = None

class CustomRecommendation(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    category: str
    impact: Optional[str] = None
    impacted_field: Optional[str] = None
    impacted_value: Optional[str] = None
    short_description_problem: Optional[str] = None
    short_description_solution: Optional[str] = None
    potential_benefits: Optional[str] = None
    learn_more_link: Optional[str] = None
    extended_properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    resource_metadata: Optional[CustomRecommendationResourceMetadata] = None
    action_details: Optional[Dict[str, Any]] = None

class CostDetailsResponse(BaseModel):
    total_cost: float
    currency: str
    costs_by_service: Dict[str, float]
    costs_by_resource_group: Dict[str, float]
    from_date: str
    to_date: str
    raw_rows: Optional[List[Any]] = None

class CostDetailsRequest(BaseModel):
    credentials: AzureCredentials
    scope: str = Field(..., example="subscriptions/00000000-0000-0000-0000-000000000000")
    time_period_days: Optional[int] = 30

class ActionResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Any] = None

class UpdateAppServicePlanSkuRequest(BaseModel):
    credentials: AzureCredentials
    resource_group_name: str
    plan_name: str
    target_sku_name: str = Field(..., description="Hedef SKU adı (örn: F1, B1, S1, P1V2)")
    target_sku_tier: str = Field(..., description="Hedef SKU katmanı (örn: Free, Basic, Standard, PremiumV2)")
    target_sku_family: Optional[str] = Field(None, description="Hedef SKU ailesi (örn: F, B, S, P)")
    target_sku_size: Optional[str] = Field(None, description="Hedef SKU boyutu (örn: F1, B1, S1)")
    target_sku_capacity: Optional[int] = Field(1, description="Hedef örnek sayısı")

class DeleteAppServicePlanRequest(BaseModel):
    credentials: AzureCredentials
    resource_group_name: str
    plan_name: str

class VMListRequest(BaseModel):
    subscription_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    tenant_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    client_id: str = Field(..., example="00000000-0000-0000-0000-000000000000")
    client_secret: str = Field(..., description="Uygulama kaydının client secret değeri.")
    cpu_threshold: Optional[float] = Field(5.0, description="CPU kullanım eşik değeri (yüzde)")
    days_for_metrics: Optional[int] = Field(7, description="Kaç günlük metrik analizi")

class StopVMRequest(BaseModel):
    credentials: AzureCredentials
    vm_id: str = Field(..., description="Durdurulacak VM'in tam resource ID'si")

@app.get("/")
async def read_root():
    return {"message": "Bulut Maliyet Optimizasyon Aracı API'sine hoş geldiniz! Endpoint'ler: /list-custom-recommendations, /list-vms-detailed, /stop-vm, /cost-details, ve App Service Plan eylemleri."}

@app.post("/list-custom-recommendations", response_model=List[CustomRecommendation], tags=["Özel Öneriler"])
async def list_custom_recommendations_endpoint(credentials: AzureCredentials):
    """Tüm özel maliyet optimizasyon önerilerini (sahipsiz genel IP'ler, App Service Plan optimizasyonları vb.) listeler."""
    all_recommendations = []
    
    # 1. Sahipsiz Genel IP Önerileri
    unattached_ip_recs = get_unattached_public_ips(
        subscription_id=credentials.subscription_id,
        tenant_id=credentials.tenant_id,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret
    )
    if unattached_ip_recs:
        all_recommendations.extend(unattached_ip_recs)
    
    # 2. App Service Plan Önerileri
    asp_recs = get_app_service_plan_recommendations(
        subscription_id=credentials.subscription_id,
        tenant_id=credentials.tenant_id,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret
    )
    if asp_recs:
        all_recommendations.extend(asp_recs)
        
    # Gelecekte diğer özel öneri türleri buraya eklenebilir
    # Örneğin: get_unattached_disks_recommendations(...)

    if not all_recommendations:
        # Eğer hiçbir öneri bulunamazsa boş liste döndürür, bu frontend tarafından normal karşılanmalı.
        return []
        
    return all_recommendations

@app.post("/debug/list-app-service-plans", tags=["Debug"])
async def debug_list_app_service_plans(credentials: AzureCredentials):
    """Debug: Tüm App Service planlarını listeler"""
    from .azure_client import get_app_service_plans_debug
    
    plans = get_app_service_plans_debug(
        subscription_id=credentials.subscription_id,
        tenant_id=credentials.tenant_id,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret
    )
    
    return plans

@app.get("/get-current-pricing/{region}", tags=["Fiyatlandırma"])
async def get_current_pricing_endpoint(region: str = "westeurope"):
    """Güncel Azure App Service planları fiyatlarını Microsoft'un resmi API'sinden çeker"""
    try:
        from .azure_pricing import get_current_app_service_pricing
        
        pricing_data = get_current_app_service_pricing("TRY", region)
        
        if not pricing_data:
            raise HTTPException(status_code=503, detail="Fiyat verisi alınamadı")
        
        return {
            "success": True,
            "region": region,
            "currency": "TRY",
            "pricing": pricing_data,
            "source": "Azure Retail Prices API",
            "updated_at": pricing_data.get(list(pricing_data.keys())[0], {}).get("last_updated") if pricing_data else None
        }
    
    except Exception as e:
        print(f"Fiyat endpoint'inde hata: {str(e)}")
        # Hata durumunda fallback fiyatları döndür
        from .azure_pricing import get_fallback_pricing
        fallback_pricing = get_fallback_pricing()
        
        return {
            "success": False,
            "region": region,
            "currency": "TRY", 
            "pricing": fallback_pricing,
            "source": "Fallback Pricing",
            "error": str(e),
            "updated_at": None
        }

@app.post("/list-vms-detailed", response_model=List[Dict], tags=["VM Analizi"])
async def list_vms_detailed_endpoint(request_data: VMListRequest):
    """Tüm VM'leri listeler ve CPU kullanım analizleriyle birlikte döndürür."""
    try:
        vms_data = get_azure_vms_with_cpu(
            subscription_id=request_data.subscription_id,
            tenant_id=request_data.tenant_id,
            client_id=request_data.client_id,
            client_secret=request_data.client_secret,
            cpu_threshold=request_data.cpu_threshold,
            days_ago_for_metrics=request_data.days_for_metrics
        )
        return vms_data
    except Exception as e:
        print(f"VM listesi endpoint'inde hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"VM'ler listelenirken hata: {str(e)}")

@app.post("/stop-vm", response_model=Dict, tags=["VM Eylemleri"])
async def stop_vm_endpoint(request_data: StopVMRequest):
    """Belirtilen VM'i durdurur ve deallocate eder."""
    try:
        success, message = stop_and_deallocate_vm(
            subscription_id=request_data.credentials.subscription_id,
            tenant_id=request_data.credentials.tenant_id,
            client_id=request_data.credentials.client_id,
            client_secret=request_data.credentials.client_secret,
            vm_id=request_data.vm_id
        )
        return {"success": success, "message": message}
    except Exception as e:
        print(f"VM durdurma endpoint'inde hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"VM durdurulamadı: {str(e)}")

@app.post("/cost-details", response_model=Optional[CostDetailsResponse], tags=["Maliyet Detayları"])
async def get_cost_details_endpoint(request_data: CostDetailsRequest):
    """Belirtilen Azure kapsamı için maliyet ve kullanım detaylarını alır."""
    cost_data = get_cost_details(
        subscription_id=request_data.credentials.subscription_id,
        tenant_id=request_data.credentials.tenant_id,
        client_id=request_data.credentials.client_id,
        client_secret=request_data.credentials.client_secret,
        scope=request_data.scope,
        time_period_days=request_data.time_period_days
    )
    if not cost_data:
        return None
    return cost_data

@app.post("/actions/update-app-service-plan-sku", response_model=ActionResponse, tags=["Eylemler - App Service Plan"])
async def update_asp_sku_endpoint(request_data: UpdateAppServicePlanSkuRequest):
    """Bir App Service Planının SKU'sunu günceller."""
    try:
        success, message, details = update_app_service_plan_sku(
            subscription_id=request_data.credentials.subscription_id,
            tenant_id=request_data.credentials.tenant_id,
            client_id=request_data.credentials.client_id,
            client_secret=request_data.credentials.client_secret,
            resource_group_name=request_data.resource_group_name,
            plan_name=request_data.plan_name,
            target_sku_name=request_data.target_sku_name,
            target_sku_tier=request_data.target_sku_tier,
            target_sku_family=request_data.target_sku_family,
            target_sku_size=request_data.target_sku_size,
            target_sku_capacity=request_data.target_sku_capacity
        )
        if success:
            return ActionResponse(success=True, message=message, details=details)
        else:
            raise HTTPException(status_code=400, detail=message or "App Service Plan SKU güncelleme başarısız.")
    except HTTPException: 
        raise
    except Exception as e:
        print(f"Update ASP SKU endpoint'inde beklenmedik hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"App Service Plan SKU güncellenirken sunucu hatası: {str(e)}")

@app.post("/actions/delete-app-service-plan", response_model=ActionResponse, tags=["Eylemler - App Service Plan"])
async def delete_asp_endpoint(request_data: DeleteAppServicePlanRequest):
    """Boş bir App Service Planını siler."""
    try:
        success, message, details = delete_app_service_plan(
            subscription_id=request_data.credentials.subscription_id,
            tenant_id=request_data.credentials.tenant_id,
            client_id=request_data.credentials.client_id,
            client_secret=request_data.credentials.client_secret,
            resource_group_name=request_data.resource_group_name,
            plan_name=request_data.plan_name
        )
        if success:
            return ActionResponse(success=True, message=message, details=details)
        else:
            # Eğer client fonksiyonu zaten anlamlı bir mesajla False döndürdüyse (örn: plan boş değil),
            # bu mesajı direkt HTTPException ile kullanabiliriz.
            status_code = 400 # Genel bir client hatası
            if details and isinstance(details, dict) and details.get("app_count", 0) > 0:
                 message = message or f"{request_data.plan_name} planı üzerinde uygulamalar olduğu için silinemedi."
            
            raise HTTPException(status_code=status_code, detail=message or "App Service Plan silme başarısız.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete ASP endpoint'inde beklenmedik hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"App Service Plan silinirken sunucu hatası: {str(e)}")

# Sahipsiz Genel IP silme endpoint'i (Yorum satırı olarak kalabilir veya gelecekte eklenebilir)
# class DeletePublicIpRequest(BaseModel): # Eğer kullanılacaksa yukarıya taşınmalı
#     credentials: AzureCredentials
#     resource_group_name: str
#     ip_name: str

# @app.post("/actions/delete-unattached-public-ip", response_model=ActionResponse, tags=["Eylemler - Genel IP"])
# async def delete_unattached_public_ip_endpoint(request_data: DeletePublicIpRequest):
#     ... (kod) ...

# Eğer uvicorn doğrudan bu dosyadan çalıştırılacaksa (önerilmez):
# if __name__ == "__main__":
#     import uvicorn
#     # Projenin kök dizininden çalıştırırken:
#     # python -m uvicorn backend.main:app --reload
#     uvicorn.run(app, host="0.0.0.0", port=8000) 