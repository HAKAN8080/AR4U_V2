"""
Seasonal Forecasting Modülü
Hierarchical forecast: Product → SubCat → MainGroup
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SeasonalForecaster:
    """
    Mevsimsel trend tahmin motoru
    Ürün -> SubCat -> MainGroup hiyerarşik fallback ile çalışır
    """
    
    def __init__(self, historical_data_path=None):
        """
        Args:
            historical_data_path: Haftalık historik data CSV yolu
        """
        self.historical_df = None
        self.seasonal_indices = {}
        self.promo_impact = {}
        
        if historical_data_path:
            self.load_historical_data(historical_data_path)
    
    def load_historical_data(self, file_path):
        """
        Historik veriyi yükle
        
        Beklenen format:
        - sku (veya boş ise kategori seviyesi)
        - MainGroup
        - SubGroupDesc
        - year (2023, 2024)
        - week (1-52)
        - sales (satış miktarı)
        - stock (stok)
        - gross_margin (brüt kar marjı)
        - promo (1=kampanyalı, 0=normal)
        """
        try:
            self.historical_df = pd.read_csv(file_path)
            
            # Veri validasyonu
            required_cols = ['MainGroup', 'SubGroupDesc', 'year', 'week', 'sales']
            missing = [col for col in required_cols if col not in self.historical_df.columns]
            
            if missing:
                raise ValueError(f"Eksik kolonlar: {missing}")
            
            # Promo kolonu yoksa ekle
            if 'promo' not in self.historical_df.columns:
                self.historical_df['promo'] = 0
            
            print(f"✅ Historik veri yüklendi: {len(self.historical_df)} kayıt")
            
            # Seasonal index'leri hesapla
            self.calculate_all_seasonal_indices()
            
        except Exception as e:
            print(f"❌ Historik veri yükleme hatası: {e}")
            self.historical_df = None
    
    def calculate_all_seasonal_indices(self):
        """
        Tüm seviyelerde (Product, SubCat, MainGroup) seasonal index hesapla
        """
        if self.historical_df is None:
            return
        
        print("📊 Seasonal index hesaplanıyor...")
        
        # 1. Ürün seviyesinde
        self._calculate_product_seasonal_index()
        
        # 2. SubCat seviyesinde
        self._calculate_subcat_seasonal_index()
        
        # 3. MainGroup seviyesinde
        self._calculate_maingroup_seasonal_index()
        
        # 4. Promo impact hesapla
        self._calculate_promo_impact()
        
        print(f"✅ Seasonal index hazır: {len(self.seasonal_indices)} grup")
    
    def _calculate_product_seasonal_index(self):
        """
        Ürün bazlı haftalık seasonal index
        """
        if 'sku' not in self.historical_df.columns:
            return
        
        # SKU'su olan kayıtları al
        product_data = self.historical_df[self.historical_df['sku'].notna()].copy()
        
        if len(product_data) == 0:
            return
        
        # Her ürün için haftalık ortalama
        for sku in product_data['sku'].unique():
            sku_data = product_data[product_data['sku'] == sku]
            
            # Haftalık ortalama satış
            weekly_avg = sku_data.groupby('week')['sales'].mean()
            
            # Yıllık ortalama satış
            yearly_avg = sku_data['sales'].mean()
            
            # Seasonal Index = Haftalık / Yıllık
            if yearly_avg > 0:
                seasonal_index = (weekly_avg / yearly_avg).to_dict()
                self.seasonal_indices[f"product_{sku}"] = seasonal_index
    
    def _calculate_subcat_seasonal_index(self):
        """
        SubCategory bazlı haftalık seasonal index
        """
        for subcat in self.historical_df['SubGroupDesc'].unique():
            subcat_data = self.historical_df[
                self.historical_df['SubGroupDesc'] == subcat
            ]
            
            # Haftalık ortalama
            weekly_avg = subcat_data.groupby('week')['sales'].mean()
            yearly_avg = subcat_data['sales'].mean()
            
            if yearly_avg > 0:
                seasonal_index = (weekly_avg / yearly_avg).to_dict()
                self.seasonal_indices[f"subcat_{subcat}"] = seasonal_index
    
    def _calculate_maingroup_seasonal_index(self):
        """
        MainGroup bazlı haftalık seasonal index
        """
        for maingroup in self.historical_df['MainGroup'].unique():
            mg_data = self.historical_df[
                self.historical_df['MainGroup'] == maingroup
            ]
            
            weekly_avg = mg_data.groupby('week')['sales'].mean()
            yearly_avg = mg_data['sales'].mean()
            
            if yearly_avg > 0:
                seasonal_index = (weekly_avg / yearly_avg).to_dict()
                self.seasonal_indices[f"maingroup_{maingroup}"] = seasonal_index
    
    def _calculate_promo_impact(self):
        """
        Kampanya etkisini hesapla
        """
        if self.historical_df is None:
            return
        
        # Promo vs Normal satış karşılaştırması
        for subcat in self.historical_df['SubGroupDesc'].unique():
            subcat_data = self.historical_df[
                self.historical_df['SubGroupDesc'] == subcat
            ]
            
            promo_sales = subcat_data[subcat_data['promo'] == 1]['sales'].mean()
            normal_sales = subcat_data[subcat_data['promo'] == 0]['sales'].mean()
            
            # Promo Lift = Kampanyalı / Normal
            if normal_sales > 0:
                promo_lift = promo_sales / normal_sales
                self.promo_impact[f"subcat_{subcat}"] = promo_lift
            else:
                self.promo_impact[f"subcat_{subcat}"] = 1.0
    
    def get_seasonal_factor(self, sku=None, subcat=None, maingroup=None, 
                           week=None, is_promo=False):
        """
        Ürün için seasonal factor döndür (hierarchical fallback ile)
        
        Args:
            sku: Ürün kodu
            subcat: Alt kategori
            maingroup: Ana grup
            week: Hafta numarası (1-52)
            is_promo: Kampanyalı mı?
            
        Returns:
            float: Seasonal factor (1.0 = normal, >1.0 = yüksek sezon, <1.0 = düşük)
        """
        if week is None:
            # Şu anki hafta numarasını al
            week = datetime.now().isocalendar()[1]
        
        seasonal_factor = 1.0
        
        # 1. Önce ürün seviyesinde ara
        if sku and f"product_{sku}" in self.seasonal_indices:
            seasonal_index = self.seasonal_indices[f"product_{sku}"]
            seasonal_factor = seasonal_index.get(week, 1.0)
            source = "product"
        
        # 2. Yoksa SubCat seviyesinde
        elif subcat and f"subcat_{subcat}" in self.seasonal_indices:
            seasonal_index = self.seasonal_indices[f"subcat_{subcat}"]
            seasonal_factor = seasonal_index.get(week, 1.0)
            source = "subcat"
        
        # 3. Yoksa MainGroup seviyesinde
        elif maingroup and f"maingroup_{maingroup}" in self.seasonal_indices:
            seasonal_index = self.seasonal_indices[f"maingroup_{maingroup}"]
            seasonal_factor = seasonal_index.get(week, 1.0)
            source = "maingroup"
        
        else:
            # Hiçbir data yok, genel mevsimsellik kullan
            seasonal_factor = self._get_default_seasonal_factor(week)
            source = "default"
        
        # Kampanya etkisini ekle
        if is_promo:
            promo_key = f"subcat_{subcat}" if subcat else None
            promo_lift = self.promo_impact.get(promo_key, 1.2)  # Default %20 artış
            seasonal_factor *= promo_lift
        
        return {
            'factor': seasonal_factor,
            'source': source,
            'week': week,
            'promo_adjusted': is_promo
        }
    
    def _get_default_seasonal_factor(self, week):
        """
        Genel mevsimsellik (data yoksa)
        
        Varsayılan pattern:
        - Kasım (44-47): Peak season (1.5x)
        - Ocak (1-4): Düşük (0.7x)
        - Yaz (22-35): Orta-düşük (0.9x)
        - Diğer: Normal (1.0x)
        """
        if 44 <= week <= 47:  # Kasım (Black Friday)
            return 1.5
        elif 1 <= week <= 4:  # Ocak (Post-holiday slump)
            return 0.7
        elif 22 <= week <= 35:  # Yaz (Haziran-Ağustos)
            return 0.9
        else:
            return 1.0
    
    def forecast_next_weeks(self, sku=None, subcat=None, maingroup=None,
                           base_daily_sales=10, weeks_ahead=4, is_promo=False):
        """
        Önümüzdeki haftalar için tahmin yap
        
        Args:
            sku, subcat, maingroup: Ürün bilgisi
            base_daily_sales: Günlük baseline satış
            weeks_ahead: Kaç hafta ileriye?
            is_promo: Kampanyalı mı?
            
        Returns:
            pd.DataFrame: Haftalık tahminler
        """
        current_week = datetime.now().isocalendar()[1]
        
        forecasts = []
        
        for i in range(weeks_ahead):
            target_week = (current_week + i) % 52
            if target_week == 0:
                target_week = 52
            
            seasonal_info = self.get_seasonal_factor(
                sku=sku,
                subcat=subcat,
                maingroup=maingroup,
                week=target_week,
                is_promo=is_promo
            )
            
            # Tahmini haftalık satış
            forecasted_weekly = base_daily_sales * 7 * seasonal_info['factor']
            
            forecasts.append({
                'week': target_week,
                'forecasted_daily_sales': base_daily_sales * seasonal_info['factor'],
                'forecasted_weekly_sales': forecasted_weekly,
                'seasonal_factor': seasonal_info['factor'],
                'source': seasonal_info['source'],
                'is_promo': is_promo
            })
        
        return pd.DataFrame(forecasts)
    
    def get_yoy_growth(self, sku=None, subcat=None, maingroup=None):
        """
        Year-over-year growth hesapla (2023 vs 2024)
        
        Returns:
            float: YoY growth rate (0.2 = %20 artış)
        """
        if self.historical_df is None:
            return 0.0
        
        # Filtreleme
        if sku:
            data = self.historical_df[self.historical_df['sku'] == sku]
        elif subcat:
            data = self.historical_df[self.historical_df['SubGroupDesc'] == subcat]
        elif maingroup:
            data = self.historical_df[self.historical_df['MainGroup'] == maingroup]
        else:
            return 0.0
        
        # 2023 vs 2024 satış
        sales_2023 = data[data['year'] == 2023]['sales'].sum()
        sales_2024 = data[data['year'] == 2024]['sales'].sum()
        
        if sales_2023 > 0:
            yoy_growth = (sales_2024 - sales_2023) / sales_2023
            return yoy_growth
        
        return 0.0
    
    def generate_seasonal_report(self):
        """
        Seasonal analiz raporu oluştur
        
        Returns:
            dict: Hafta bazlı toplam seasonal index
        """
        if not self.seasonal_indices:
            return {}
        
        # Tüm kategorilerin ortalaması
        all_weeks = {}
        
        for key, indices in self.seasonal_indices.items():
            for week, factor in indices.items():
                if week not in all_weeks:
                    all_weeks[week] = []
                all_weeks[week].append(factor)
        
        # Her hafta için ortalama
        avg_seasonal = {
            week: np.mean(factors) 
            for week, factors in all_weeks.items()
        }
        
        return avg_seasonal
