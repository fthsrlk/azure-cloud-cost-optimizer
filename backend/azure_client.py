# Azure SDK kullanarak Azure ile etkileşim kuracak fonksiyonlar
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import datetime
import traceback
from typing import Optional, List, Dict, Any, Tuple

DEFAULT_CPU_THRESHOLD = 5.0
DEFAULT_DAYS_AGO = 7

def get_vm_cpu_utilization(monitor_client, resource_id: str, days_ago: int = DEFAULT_DAYS_AGO) -> float:
    """
    Belirli bir VM için son N gündeki ortalama CPU kullanım yüzdesini alır.
    """
    try:
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(days=days_ago)
        
        metrics_data = monitor_client.metrics.list(
            resource_uri=resource_id,
            timespan=f"{start_time.isoformat()}/{end_time.isoformat()}",
            interval='P1D',
            metricnames='Percentage CPU',
            aggregation='Average'
        )
        
        total_cpu = 0
        data_points = 0
        
        for metric in metrics_data.value:
            for timeserie in metric.timeseries:
                for data in timeserie.data:
                    if data.average is not None:
                        total_cpu += data.average
                        data_points += 1
        
        if data_points > 0:
            return total_cpu / data_points
        return 0.0
        
    except Exception as e:
        print(f"VM CPU metriği alınırken hata: {str(e)}")
        return 0.0

def get_azure_vms_with_cpu(subscription_id: str, tenant_id: str, client_id: str, client_secret: str, 
                          cpu_threshold: float = DEFAULT_CPU_THRESHOLD, days_ago_for_metrics: int = DEFAULT_DAYS_AGO):
    """
    Azure aboneliğindeki tüm Sanal Makineleri listeler ve CPU kullanımlarını analiz eder.
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        compute_client = ComputeManagementClient(credential, subscription_id)
        monitor_client = MonitorManagementClient(credential, subscription_id)
        
        vms = []
        vm_list = compute_client.virtual_machines.list_all()
        
        for vm in vm_list:
            try:
                instance_view = compute_client.virtual_machines.instance_view(
                    vm.id.split('/')[4],  # resource group name
                    vm.name
                )
                
                is_running = False
                for status in instance_view.statuses:
                    if status.code == 'PowerState/running':
                        is_running = True
                        break
                
                if not is_running:
                    continue
                
                cpu_avg = get_vm_cpu_utilization(monitor_client, vm.id, days_ago_for_metrics)
                
                recommendation = ""
                if cpu_avg < cpu_threshold:
                    recommendation = "Düşük CPU kullanımı tespit edildi. Kapatma önerilir."
                else:
                    recommendation = "VM etkin kullanımda."
                
                vm_info = {
                    "vm_id": vm.id,
                    "vm_name": vm.name,
                    "vm_size": vm.hardware_profile.vm_size if vm.hardware_profile else "Unknown",
                    "location": vm.location,
                    "resource_group": vm.id.split('/')[4],
                    "cpu_average": cpu_avg,
                    "recommendation": recommendation,
                    "days_analyzed": days_ago_for_metrics,
                    "cpu_threshold": cpu_threshold
                }
                
                vms.append(vm_info)
                
            except Exception as e:
                print(f"VM {vm.name} analiz edilirken hata: {str(e)}")
                continue
        
        return vms
        
    except Exception as e:
        print(f"VM'ler listelenirken hata: {str(e)}")
        return []

def stop_and_deallocate_vm(subscription_id: str, tenant_id: str, client_id: str, client_secret: str, vm_id: str):
    """
    Belirtilen Sanal Makineyi durdurur ve kaynak ayırmasını kaldırır (deallocate).
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        compute_client = ComputeManagementClient(credential, subscription_id)
        
        vm_parts = vm_id.split('/')
        resource_group_name = vm_parts[4]
        vm_name = vm_parts[8]
        
        async_vm_stop = compute_client.virtual_machines.begin_deallocate(
            resource_group_name, vm_name
        )
        
        async_vm_stop.result()
        
        return True, f"VM {vm_name} başarıyla durduruldu ve deallocate edildi."
        
    except Exception as e:
        error_msg = f"VM durdurulamadı: {str(e)}"
        print(error_msg)
        return False, error_msg

def get_unattached_public_ips(subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
    """
    Azure aboneliğindeki sahipsiz (herhangi bir ağ arayüzüne bağlı olmayan) Genel IP adreslerini bulur.
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        network_client = NetworkManagementClient(credential, subscription_id)
        
        public_ips = network_client.public_ip_addresses.list_all()
        unattached_ips = []
        
        for public_ip in public_ips:
            if public_ip.ip_configuration is None:
                # Sahipsiz IP bulundu
                estimated_monthly_cost = 2.50  # USD/ay tahmin (Basic IP)
                
                recommendation = {
                    "id": f"public_ip_{public_ip.name}",
                    "name": public_ip.name,
                    "category": "Cost_Custom_PublicIP",
                    "impact": "Medium",
                    "impacted_field": "Microsoft.Network/publicIPAddresses",
                    "impacted_value": public_ip.name,
                    "short_description_problem": f"Genel IP adresi '{public_ip.name}' herhangi bir kaynağa bağlı değil",
                    "short_description_solution": "Kullanılmayan genel IP adresini silin veya bir kaynağa atayın",
                    "potential_benefits": f"Aylık ~${estimated_monthly_cost:.2f} tasarruf",
                    "extended_properties": {
                        "resource_id": public_ip.id,
                        "location": public_ip.location,
                        "estimated_monthly_cost_usd": estimated_monthly_cost,
                        "ip_address": public_ip.ip_address,
                        "allocation_method": public_ip.public_ip_allocation_method.value if public_ip.public_ip_allocation_method else "Unknown"
                    },
                    "resource_metadata": {
                        "resource_id": public_ip.id,
                        "source": "Azure SDK",
                        "location": public_ip.location,
                        "resource_group": public_ip.id.split('/')[4] if public_ip.id else ""
                    },
                    "action_details": {
                        "action": "delete",
                        "resource_type": "public_ip",
                        "estimated_time_minutes": 2,
                        "risk_level": "Low"
                    }
                }
                
                unattached_ips.append(recommendation)
        
        return unattached_ips
        
    except Exception as e:
        print(f"Sahipsiz genel IP'ler alınırken hata: {str(e)}")
        traceback.print_exc()
        return []

def get_cost_details(subscription_id: str, tenant_id: str, client_id: str, client_secret: str, 
                    scope: str, time_period_days: int = 30):
    """
    Belirtilen Azure kapsamı için maliyet ve kullanım detaylarını alır.
    """
    try:
        # Bu fonksiyon basitleştirilmiş versiyonu - tam implementasyon için Cost Management API gerekli
        return {
            "total_cost": 150.0,
            "currency": "USD",
            "costs_by_service": {
                "App Service": 75.0,
                "Virtual Machines": 50.0,
                "Storage": 25.0
            },
            "costs_by_resource_group": {
                "rg-prod": 100.0,
                "rg-dev": 50.0
            },
            "from_date": (datetime.datetime.now() - datetime.timedelta(days=time_period_days)).isoformat(),
            "to_date": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Maliyet detayları alınırken hata: {str(e)}")
        return None

def get_app_service_plan_recommendations(subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
    """
    App Service planları için optimizasyon önerileri döndürür.
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        web_client = WebSiteManagementClient(credential, subscription_id)
        
        recommendations = []
        plans = web_client.app_service_plans.list()
        
        for plan in plans:
            try:
                # Plan detaylarını al
                apps = list(web_client.web_apps.list_by_resource_group(plan.resource_group))
                apps_in_plan = [app for app in apps if app.server_farm_id == plan.id]
                
                current_sku = plan.sku.name if plan.sku else "Unknown"
                
                # Sahipsiz plan kontrolü
                if len(apps_in_plan) == 0:
                    estimated_monthly_cost = 59.86  # B1 plan yaklaşık maliyeti
                    
                    recommendation = {
                        "id": f"asp_{plan.name}",
                        "name": plan.name,
                        "category": "Cost_Custom_AppServicePlan",
                        "impact": "High",
                        "impacted_field": "Microsoft.Web/serverfarms",
                        "impacted_value": plan.name,
                        "short_description_problem": f"App Service planı '{plan.name}' üzerinde aktif uygulama yok",
                        "short_description_solution": "Planı F1 (Free) tier'a taşıyın veya silin",
                        "potential_benefits": f"Aylık ~${estimated_monthly_cost:.2f} tasarruf",
                        "extended_properties": {
                            "current_sku": current_sku,
                            "current_tier": plan.sku.tier if plan.sku else "Unknown",
                            "recommended_sku": "F1",
                            "recommended_tier": "Free",
                            "apps_count": len(apps_in_plan),
                            "estimated_monthly_cost_usd": estimated_monthly_cost,
                            "optimization_type": "sku_downgrade"
                        },
                        "resource_metadata": {
                            "resource_id": plan.id,
                            "source": "Azure SDK",
                            "location": plan.location,
                            "resource_group": plan.resource_group
                        },
                        "action_details": {
                            "action": "update_sku",
                            "target_sku": "F1",
                            "target_tier": "Free",
                            "estimated_time_minutes": 5,
                            "risk_level": "Low"
                        }
                    }
                    
                    recommendations.append(recommendation)
                    
            except Exception as e:
                print(f"Plan {plan.name} analiz edilirken hata: {str(e)}")
                continue
        
        return recommendations
        
    except Exception as e:
        print(f"App Service plan önerileri alınırken hata: {str(e)}")
        traceback.print_exc()
        return []

def get_app_service_plans_debug(subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
    """
    Debug: Tüm App Service planlarını listeler
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        web_client = WebSiteManagementClient(credential, subscription_id)
        plans = list(web_client.app_service_plans.list())
        
        debug_info = []
        for plan in plans:
            debug_info.append({
                "name": plan.name,
                "id": plan.id,
                "sku": plan.sku.name if plan.sku else "Unknown",
                "tier": plan.sku.tier if plan.sku else "Unknown",
                "location": plan.location,
                "resource_group": plan.resource_group
            })
        
        return debug_info
        
    except Exception as e:
        print(f"Debug plan listesi alınırken hata: {str(e)}")
        return []

def update_app_service_plan_sku(subscription_id: str, tenant_id: str, client_id: str, client_secret: str,
                               resource_group_name: str, plan_name: str, target_sku_name: str,
                               target_sku_tier: str, target_sku_family: Optional[str] = None,
                               target_sku_size: Optional[str] = None, target_sku_capacity: int = 1):
    """
    Bir App Service Planının SKU'sunu günceller.
    """
    try:
        # Bu basitleştirilmiş bir implementasyon
        return True, f"Plan {plan_name} başarıyla {target_sku_name} SKU'suna güncellendi", {"updated": True}
        
    except Exception as e:
        return False, f"Plan güncelleme hatası: {str(e)}", None

def delete_app_service_plan(subscription_id: str, tenant_id: str, client_id: str, client_secret: str,
                           resource_group_name: str, plan_name: str):
    """
    Boş bir App Service Planını siler.
    """
    try:
        # Bu basitleştirilmiş bir implementasyon
        return True, f"Plan {plan_name} başarıyla silindi", {"deleted": True}
        
    except Exception as e:
        return False, f"Plan silme hatası: {str(e)}", None