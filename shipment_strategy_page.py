"""
Sevkiyat Stratejisi Sayfası
Transfer, Reorder ve Markdown Önerileri
"""
import streamlit as st
import pandas as pd
from utils.helpers import (
    format_number, format_currency, format_percentage,
    show_success, show_error, show_info, show_warning
)
from utils.constants import SEGMENT_COLORS, SEGMENT_EMOJI, TRANSFER_LEAD_TIME_DAYS

def show_shipment_strategy_page():
    """Sevkiyat Stratejisi Ana Sayfası"""
    
    st.markdown("## 📦 Sevkiyat Stratejisi & Transfer Yönetimi")
    
    # Session state kontrolü
    if not st.session_state.get('data_loaded'):
        st.warning("⚠️ Lütfen önce veriyi yükleyin!")
        return
    
    allocation_df = st.session_state.allocation_df
    optimizer = st.session_state.optimizer
    df = st.session_state.df
    
    # Transfer özet istatistikleri
    transfer_stats = optimizer.get_transfer_summary_stats()
    
    # 📊 Üst KPI Kartları
    st.markdown("### 📊 Transfer Özeti")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🚨 Acil Transfer",
            format_number(transfer_stats['urgent_transfers']),
            help=f"Lead time ({TRANSFER_LEAD_TIME_DAYS} gün) içinde stok bitecek ürünler"
        )
    
    with col2:
        st.metric(
            "🤖 Otomatik Transfer",
            format_number(transfer_stats['auto_transfers']),
            help="Auto-transfer aktif ürünler"
        )
    
    with col3:
        st.metric(
            "📦 Toplam Transfer Hacmi",
            format_number(transfer_stats['total_transfer_volume'], 0),
            help="Transfer edilmesi gereken toplam adet"
        )
    
    with col4:
        st.metric(
            "📏 Ortalama Transfer",
            format_number(transfer_stats['avg_transfer_size'], 0),
            help="Transfer başına ortalama adet"
        )
    
    with col5:
        st.metric(
            "🚛 Lead Time",
            f"{TRANSFER_LEAD_TIME_DAYS} gün",
            help="Ana Depo → Akyazı transfer süresi"
        )
    
    st.divider()
    
    # 🎯 Ana Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚛 Transfer Önerileri",
        "🛒 Sipariş (Reorder)",
        "🏷️ Markdown Adayları",
        "🎮 Transfer Simülatör",
        "📊 Depo Optimizasyonu"
    ])
    
    # TAB 1: Transfer Önerileri
    with tab1:
        show_transfer_recommendations_tab(optimizer, allocation_df, df)
    
    # TAB 2: Reorder Önerileri
    with tab2:
        show_reorder_recommendations_tab(optimizer, allocation_df, df)
    
    # TAB 3: Markdown Adayları
    with tab3:
        show_markdown_candidates_tab(optimizer, allocation_df, df)
    
    # TAB 4: Transfer Simülatör
    with tab4:
        show_transfer_simulator_tab(optimizer, df)
    
    # TAB 5: Depo Optimizasyonu
    with tab5:
        show_depot_optimization_tab(optimizer, allocation_df, df)


def show_transfer_recommendations_tab(optimizer, allocation_df, df):
    """Transfer önerileri tab'ı"""
    
    st.markdown("### 🚛 Transfer Önerileri (Ana Depo → Akyazı)")
    
    # Sub-tabs: Urgent, Auto, All
    subtab1, subtab2, subtab3 = st.tabs(["🚨 ACİL", "🤖 OTOMATİK", "📋 TÜMÜ"])
    
    # ACİL TRANSFERLER
    with subtab1:
        st.info(f"""
        **🚨 Acil Transfer Kriterleri:**
        - Akyazı stoğu {TRANSFER_LEAD_TIME_DAYS} gün içinde bitecek
        - Transfer lead time ({TRANSFER_LEAD_TIME_DAYS} gün) boyunca stoksuz kalma riski var
        - HOT veya RISING_STAR segmentinde
        """)
        
        urgent_transfers = optimizer.get_transfer_recommendations(
            min_transfer=1, 
            priority='urgent'
        )
        
        if len(urgent_transfers) == 0:
            st.success("✅ Acil transfer ihtiyacı yok!")
        else:
            st.error(f"⚠️ {len(urgent_transfers)} ürün için ACİL transfer gerekiyor!")
            
            # Styled dataframe
            styled_urgent = urgent_transfers.copy()
            styled_urgent['segment_emoji'] = styled_urgent['segment'].map(SEGMENT_EMOJI)
            styled_urgent = styled_urgent[[
                'segment_emoji', 'sku', 'product_name', 'segment',
                'transfer_from_ana_depo', 'days_until_stockout_akyazi',
                'stock_consumed_during_transfer', 'forecasted_daily_sales'
            ]]
            
            st.dataframe(
                styled_urgent.style.format({
                    'transfer_from_ana_depo': '{:.0f}',
                    'days_until_stockout_akyazi': '{:.1f}',
                    'stock_consumed_during_transfer': '{:.1f}',
                    'forecasted_daily_sales': '{:.2f}'
                }).background_gradient(
                    subset=['days_until_stockout_akyazi'],
                    cmap='RdYlGn',
                    vmin=0,
                    vmax=TRANSFER_LEAD_TIME_DAYS
                ),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # CSV Export
            csv_urgent = urgent_transfers.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Acil Transfer Listesini İndir (CSV)",
                csv_urgent,
                "acil_transfer_listesi.csv",
                "text/csv",
                key='download-urgent'
            )
    
    # OTOMATİK TRANSFERLER
    with subtab2:
        st.info("""
        **🤖 Otomatik Transfer Kriterleri:**
        - Segment auto_transfer parametresi aktif (HOT, RISING_STAR)
        - Optimal allocation'a ulaşmak için transfer gerekli
        - Minimum 10 adet transfer miktarı
        """)
        
        auto_transfers = optimizer.get_transfer_recommendations(
            min_transfer=10, 
            priority='auto'
        )
        
        if len(auto_transfers) == 0:
            st.success("✅ Otomatik transfer ihtiyacı yok!")
        else:
            st.warning(f"📦 {len(auto_transfers)} ürün için otomatik transfer öneriliyor")
            
            # Segment filtreleme
            segments_in_data = auto_transfers['segment'].unique().tolist()
            selected_segments = st.multiselect(
                "Segment Filtrele:",
                segments_in_data,
                default=segments_in_data,
                key='auto_segment_filter'
            )
            
            filtered_auto = auto_transfers[auto_transfers['segment'].isin(selected_segments)]
            
            # Styled dataframe
            st.dataframe(
                filtered_auto.style.format({
                    'transfer_from_ana_depo': '{:.0f}',
                    'days_until_stockout_akyazi': '{:.1f}',
                    'stock_consumed_during_transfer': '{:.1f}',
                    'forecasted_daily_sales': '{:.2f}'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Özet
            col1, col2 = st.columns(2)
            with col1:
                total_to_transfer = filtered_auto['transfer_from_ana_depo'].sum()
                st.metric("Toplam Transfer Adedi", format_number(total_to_transfer, 0))
            with col2:
                avg_transfer = filtered_auto['transfer_from_ana_depo'].mean()
                st.metric("Ortalama Transfer", format_number(avg_transfer, 0))
            
            # CSV Export
            csv_auto = filtered_auto.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Otomatik Transfer Listesini İndir (CSV)",
                csv_auto,
                "otomatik_transfer_listesi.csv",
                "text/csv",
                key='download-auto'
            )
    
    # TÜM TRANSFERLER
    with subtab3:
        all_transfers = optimizer.get_transfer_recommendations(
            min_transfer=1, 
            priority='all'
        )
        
        if len(all_transfers) == 0:
            st.success("✅ Transfer ihtiyacı yok!")
        else:
            st.info(f"📋 Toplam {len(all_transfers)} ürün için transfer önerisi var")
            
            # Filtreleme seçenekleri
            col1, col2, col3 = st.columns(3)
            
            with col1:
                segments_all = all_transfers['segment'].unique().tolist()
                selected_seg = st.multiselect(
                    "Segment:",
                    segments_all,
                    default=segments_all,
                    key='all_segment_filter'
                )
            
            with col2:
                min_qty = st.number_input(
                    "Min Transfer Adedi:",
                    min_value=1,
                    value=10,
                    key='min_qty_filter'
                )
            
            with col3:
                urgent_only = st.checkbox("Sadece Acil", key='urgent_only_filter')
            
            # Filtreleme
            filtered_all = all_transfers[all_transfers['segment'].isin(selected_seg)]
            filtered_all = filtered_all[filtered_all['transfer_from_ana_depo'] >= min_qty]
            if urgent_only:
                filtered_all = filtered_all[filtered_all['is_urgent_transfer'] == True]
            
            st.dataframe(
                filtered_all,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # CSV Export
            csv_all = filtered_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Tüm Transfer Listesini İndir (CSV)",
                csv_all,
                "tum_transfer_listesi.csv",
                "text/csv",
                key='download-all'
            )


def show_reorder_recommendations_tab(optimizer, allocation_df, df):
    """Reorder (sipariş) önerileri tab'ı"""
    
    st.markdown("### 🛒 Sipariş Önerileri (Reorder)")
    
    st.info("""
    **📋 Sipariş Kriterleri:**
    - Toplam stok < Reorder Point (segment bazlı)
    - Kritik stok seviyesinde
    - Acil tedarik gerekli
    """)
    
    reorder_df = optimizer.get_reorder_recommendations()
    
    if len(reorder_df) == 0:
        st.success("✅ Sipariş gerektiren ürün yok! Tüm stoklar yeterli seviyede.")
    else:
        st.error(f"⚠️ {len(reorder_df)} ürün için ACİL SİPARİŞ gerekiyor!")
        
        # Segment bazlı filtreleme
        segments_reorder = reorder_df['segment'].unique().tolist()
        selected_segments_reorder = st.multiselect(
            "Segment Filtrele:",
            segments_reorder,
            default=segments_reorder,
            key='reorder_segment_filter'
        )
        
        filtered_reorder = reorder_df[reorder_df['segment'].isin(selected_segments_reorder)]
        
        # Styled dataframe
        st.dataframe(
            filtered_reorder.style.format({
                'current_stock': '{:.0f}',
                'reorder_point': '{:.0f}',
                'days_of_stock': '{:.1f}',
                'suggested_order_qty': '{:.0f}'
            }).background_gradient(
                subset=['days_of_stock'],
                cmap='RdYlGn_r',  # Reverse: Düşük = kırmızı
                vmin=0,
                vmax=10
            ),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Özet metrikleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_order_qty = filtered_reorder['suggested_order_qty'].sum()
            st.metric("Toplam Sipariş Adedi", format_number(total_order_qty, 0))
        
        with col2:
            avg_days = filtered_reorder['days_of_stock'].mean()
            st.metric("Ortalama Stok Günü", f"{avg_days:.1f}")
        
        with col3:
            critical_count = len(filtered_reorder[filtered_reorder['days_of_stock'] < 3])
            st.metric("Kritik Ürün (<3 gün)", critical_count)
        
        # CSV Export
        csv_reorder = filtered_reorder.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Sipariş Listesini İndir (CSV)",
            csv_reorder,
            "siparis_listesi.csv",
            "text/csv",
            key='download-reorder'
        )


def show_markdown_candidates_tab(optimizer, allocation_df, df):
    """Markdown adayları tab'ı"""
    
    st.markdown("### 🏷️ Markdown (İndirim) Adayları")
    
    st.warning("""
    **🏷️ Markdown Kriterleri:**
    - DYING segmenti → URGENT (7 gün içinde markdown)
    - Fazla stoklu ürünler (days_of_stock > eşik) → CONSIDER
    - Potansiyel kayıp: %30 indirim varsayımı ile hesaplanmış
    """)
    
    markdown_df = optimizer.get_markdown_candidates()
    
    if len(markdown_df) == 0:
        st.success("✅ Markdown gerektiren ürün yok!")
    else:
        st.info(f"🏷️ {len(markdown_df)} ürün için markdown önerisi var")
        
        # Urgent / Consider tabs
        markdown_tab1, markdown_tab2 = st.tabs(["🚨 URGENT", "⚠️ CONSIDER"])
        
        with markdown_tab1:
            urgent_markdown = markdown_df[markdown_df['markdown_recommendation'] == 'URGENT']
            
            if len(urgent_markdown) == 0:
                st.success("✅ Acil markdown gerektiren ürün yok")
            else:
                st.error(f"⚠️ {len(urgent_markdown)} ürün için ACİL MARKDOWN gerekiyor!")
                
                st.dataframe(
                    urgent_markdown.style.format({
                        'current_stock': '{:.0f}',
                        'days_of_stock': '{:.0f}',
                        'potential_loss': '₺{:,.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )
                
                total_loss = urgent_markdown['potential_loss'].sum()
                st.metric("💰 Toplam Potansiyel Kayıp (%30 indirim)", format_currency(total_loss))
        
        with markdown_tab2:
            consider_markdown = markdown_df[markdown_df['markdown_recommendation'] == 'CONSIDER']
            
            if len(consider_markdown) == 0:
                st.success("✅ Markdown düşünülecek ürün yok")
            else:
                st.warning(f"⚠️ {len(consider_markdown)} ürün için markdown düşünülebilir")
                
                st.dataframe(
                    consider_markdown.style.format({
                        'current_stock': '{:.0f}',
                        'days_of_stock': '{:.0f}',
                        'potential_loss': '₺{:,.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )
                
                total_loss = consider_markdown['potential_loss'].sum()
                st.metric("💰 Toplam Potansiyel Kayıp (%30 indirim)", format_currency(total_loss))
        
        # CSV Export
        csv_markdown = markdown_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Markdown Listesini İndir (CSV)",
            csv_markdown,
            "markdown_listesi.csv",
            "text/csv",
            key='download-markdown'
        )


def show_transfer_simulator_tab(optimizer, df):
    """Transfer simülatörü tab'ı"""
    
    st.markdown("### 🎮 Transfer Simülatörü")
    
    st.info("""
    **💡 Transfer Simülatörü:**
    Bir ürünü bir depodan diğerine transfer etmeyi simüle eder.
    Lead time etkisini gösterir ve stoksuz kalma riskini hesaplar.
    """)
    
    # SKU seçimi
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sku_list = df['sku'].tolist()
        product_names = df['product_name'].tolist()
        options = [f"{sku} - {name}" for sku, name in zip(sku_list, product_names)]
        
        selected_option = st.selectbox(
            "Ürün Seçin:",
            options,
            key='sim_product_select'
        )
        
        selected_sku = selected_option.split(' - ')[0]
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        product_info = df[df['sku'] == selected_sku].iloc[0]
        st.caption(f"**Segment:** {SEGMENT_EMOJI.get(product_info['segment'], '❓')} {product_info['segment']}")
    
    # Transfer parametreleri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from_depot = st.selectbox(
            "Kaynak Depo:",
            ['ana_depo', 'akyazi', 'oms_total'],
            key='sim_from_depot'
        )
    
    with col2:
        to_depot = st.selectbox(
            "Hedef Depo:",
            ['akyazi', 'ana_depo', 'oms_total'],
            key='sim_to_depot'
        )
    
    with col3:
        max_stock = int(product_info[f'stock_{from_depot}'])
        transfer_qty = st.number_input(
            "Transfer Adedi:",
            min_value=1,
            max_value=max_stock if max_stock > 0 else 1000,
            value=min(50, max_stock) if max_stock > 0 else 50,
            key='sim_qty'
        )
    
    # Simülasyon butonu
    if st.button("🎮 Simülasyonu Çalıştır", use_container_width=True, type="primary"):
        if from_depot == to_depot:
            st.error("❌ Kaynak ve hedef depo aynı olamaz!")
        elif max_stock == 0:
            st.error(f"❌ {from_depot} deposunda stok yok!")
        else:
            # Simülasyonu çalıştır
            sim_result = optimizer.simulate_transfer(
                sku=selected_sku,
                from_depot=from_depot,
                to_depot=to_depot,
                quantity=transfer_qty
            )
            
            # Sonuçları göster
            st.success("✅ Simülasyon tamamlandı!")
            
            st.divider()
            
            # Mevcut durum vs Yeni durum
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Mevcut Durum")
                st.metric("Kaynak Depo", format_number(sim_result['current_from'], 0))
                st.metric("Hedef Depo", format_number(sim_result['current_to'], 0))
                st.metric("Stok Günü", f"{sim_result['current_days_of_stock']:.1f}")
            
            with col2:
                st.markdown("#### 📊 Transfer Sonrası")
                st.metric(
                    "Kaynak Depo",
                    format_number(sim_result['new_from'], 0),
                    delta=format_number(sim_result['new_from'] - sim_result['current_from'], 0)
                )
                st.metric(
                    "Hedef Depo",
                    format_number(sim_result['new_to'], 0),
                    delta=format_number(sim_result['new_to'] - sim_result['current_to'], 0)
                )
                st.metric(
                    "Stok Günü",
                    f"{sim_result['new_days_of_stock']:.1f}",
                    delta=f"{sim_result['new_days_of_stock'] - sim_result['current_days_of_stock']:.1f}"
                )
            
            # Lead time uyarısı
            if to_depot == 'akyazi' and sim_result.get('will_stockout_during_transfer'):
                st.error(f"""
                ⚠️ **DİKKAT: STOKSUZLUK RİSKİ!**
                
                Transfer süresince ({sim_result['transfer_lead_time']} gün) Akyazı'da stok tükenecek!
                Günlük satış: {sim_result['daily_sales_forecast']:.2f} adet
                """)
            elif to_depot == 'akyazi':
                st.success(f"""
                ✅ **Transfer Güvenli**
                
                {sim_result['transfer_lead_time']} günlük lead time boyunca stok yeterli olacak.
                Günlük satış: {sim_result['daily_sales_forecast']:.2f} adet
                """)


def show_depot_optimization_tab(optimizer, allocation_df, df):
    """Depo optimizasyonu analizi tab'ı"""
    
    st.markdown("### 📊 Depo Dağılım Optimizasyonu")
    
    st.info("""
    **📦 Optimal Dağılım Mantığı:**
    - HOT: %80 Akyazı, %20 Ana Depo/OMS
    - RISING_STAR: %70 Akyazı, %30 Ana Depo/OMS
    - STEADY: %60 Akyazı, %40 Ana Depo/OMS
    - SLOW: %30 Akyazı, %70 Ana Depo/OMS
    - DYING: %0 Akyazı (tümü OMS'e)
    """)
    
    reallocation_df = optimizer.optimize_depot_allocation()
    
    if len(reallocation_df) == 0:
        st.success("✅ Tüm ürünler optimal dağılımda! Reallocation gerekmiyor.")
    else:
        st.warning(f"⚠️ {len(reallocation_df)} ürün için reallocation önerisi var")
        
        # Filtreler
        col1, col2 = st.columns(2)
        
        with col1:
            segments_realloc = reallocation_df['segment'].unique().tolist()
            selected_seg_realloc = st.multiselect(
                "Segment Filtrele:",
                segments_realloc,
                default=segments_realloc,
                key='realloc_seg_filter'
            )
        
        with col2:
            action_type = st.multiselect(
                "Aksiyon Tipi:",
                ['Transfer to Akyazı', 'Reduce Akyazı'],
                default=['Transfer to Akyazı', 'Reduce Akyazı'],
                key='realloc_action_filter'
            )
        
        filtered_realloc = reallocation_df[
            (reallocation_df['segment'].isin(selected_seg_realloc)) &
            (reallocation_df['action_needed'].isin(action_type))
        ]
        
        st.dataframe(
            filtered_realloc.style.format({
                'current_akyazi_pct': '{:.1f}%',
                'optimal_akyazi_pct': '{:.1f}%',
                'suggested_transfer': '{:.0f}'
            }),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Özet
        col1, col2, col3 = st.columns(3)
        
        with col1:
            needs_increase = len(filtered_realloc[filtered_realloc['action_needed'] == 'Transfer to Akyazı'])
            st.metric("Akyazı'ya Transfer", needs_increase)
        
        with col2:
            needs_decrease = len(filtered_realloc[filtered_realloc['action_needed'] == 'Reduce Akyazı'])
            st.metric("Akyazı'dan Çıkar", needs_decrease)
        
        with col3:
            total_volume = filtered_realloc['suggested_transfer'].sum()
            st.metric("Toplam Hacim", format_number(total_volume, 0))
        
        # CSV Export
        csv_realloc = filtered_realloc.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Reallocation Listesini İndir (CSV)",
            csv_realloc,
            "reallocation_listesi.csv",
            "text/csv",
            key='download-realloc'
        )
    
    st.divider()
    
    # Genel depo durumu
    st.markdown("### 📈 Genel Depo Durumu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🏢 Akyazı Toplam Stok",
            format_number(df['stock_akyazi'].sum(), 0)
        )
        akyazi_value = (df['stock_akyazi'] * df['price']).sum()
        st.caption(f"Değer: {format_currency(akyazi_value)}")
    
    with col2:
        st.metric(
            "🏭 Ana Depo Toplam Stok",
            format_number(df['stock_ana_depo'].sum(), 0)
        )
        ana_value = (df['stock_ana_depo'] * df['price']).sum()
        st.caption(f"Değer: {format_currency(ana_value)}")
    
    with col3:
        st.metric(
            "🏪 OMS Toplam Stok",
            format_number(df['stock_oms_total'].sum(), 0)
        )
        oms_value = (df['stock_oms_total'] * df['price']).sum()
        st.caption(f"Değer: {format_currency(oms_value)}")
