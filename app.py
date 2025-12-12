import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ========== 页面配置 ==========
st.set_page_config(
    page_title="土壤流失量综合测算平台 (SL 773-2018)",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS样式 ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #374151;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<h1 class="main-header">🌍 生产建设项目土壤流失量综合测算平台</h1>', unsafe_allow_html=True)
st.markdown("**依据《生产建设项目土壤流失量测算导则》（SL 773-2018）**")
st.caption("Version 2.0 | 涵盖导则全部计算场景 | 支持多项目对比")

# ========== 侧边栏 - 项目配置 ==========
with st.sidebar:
    st.header("⚙️ 项目配置")
    
    project_name = st.text_input("项目名称", "示例水土保持项目")
    project_location = st.selectbox("项目所在地", 
        ["华北地区", "东北地区", "华东地区", "华中地区", "华南地区", "西南地区", "西北地区"])
    
    st.divider()
    st.header("📊 预设参数库")
    
    # R因子数据库
    r_factor_db = {
        "华北地区": 1800,
        "东北地区": 2200,
        "华东地区": 3500,
        "华中地区": 4200,
        "华南地区": 5800,
        "西南地区": 3800,
        "西北地区": 1200
    }
    
    # K因子数据库
    k_factor_db = {
        "砂土": 0.12,
        "砂壤土": 0.18,
        "轻壤土": 0.25,
        "中壤土": 0.32,
        "重壤土": 0.38,
        "黏土": 0.42
    }
    
    use_preset = st.checkbox("使用地区预设参数", value=True)
    
    if use_preset:
        r_preset = r_factor_db.get(project_location, 2000)
        st.info(f"📌 {project_location} R因子参考值: {r_preset} MJ·mm/(hm²·h)")
    
    st.divider()
    calculation_year = st.slider("测算年份", 2020, 2030, 2024)

# ========== 主界面 - 标签页布局 ==========
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 项目概览", 
    "📐 一般扰动地表", 
    "⚒️ 工程开挖面", 
    "⛰️ 工程堆积体", 
    "📈 结果汇总", 
    "⚙️ 参数查询"
])

# ========== 标签页1: 项目概览 ==========
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h3 class="sub-header">项目基本信息</h3>', unsafe_allow_html=True)
        
        info_cols = st.columns(2)
        with info_cols[0]:
            project_area = st.number_input("项目区面积 (hm²)", min_value=0.0, value=10.0, step=1.0)
            construction_period = st.number_input("建设工期 (月)", min_value=1, value=24, step=1)
        
        with info_cols[1]:
            soil_type_main = st.selectbox("主要土壤类型", list(k_factor_db.keys()))
            vegetation_coverage = st.slider("原地貌植被覆盖率 (%)", 0, 100, 60)
        
        # 扰动类型面积分配
        st.markdown('<h3 class="sub-header">扰动类型面积分配</h3>', unsafe_allow_html=True)
        
        dist_cols = st.columns(4)
        with dist_cols[0]:
            area_general = st.number_input("一般扰动地表 (hm²)", min_value=0.0, value=4.0, step=0.5)
        with dist_cols[1]:
            area_excavation = st.number_input("工程开挖面 (hm²)", min_value=0.0, value=2.0, step=0.5)
        with dist_cols[2]:
            area_pile = st.number_input("工程堆积体 (hm²)", min_value=0.0, value=3.0, step=0.5)
        with dist_cols[3]:
            area_other = st.number_input("其他扰动 (hm²)", min_value=0.0, value=1.0, step=0.5)
    
    with col2:
        st.markdown('<h3 class="sub-header">项目摘要</h3>', unsafe_allow_html=True)
        
        # 面积饼图
        areas = {
            '一般扰动地表': area_general,
            '工程开挖面': area_excavation,
            '工程堆积体': area_pile,
            '其他扰动': area_other
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(areas.keys()),
            values=list(areas.values()),
            hole=.3,
            marker_colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        )])
        fig.update_layout(
            title="扰动类型面积分布",
            height=300,
            showlegend=True,
            margin=dict(t=50, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 项目摘要指标
        total_area = sum(areas.values())
        st.metric("总扰动面积", f"{total_area:.2f} hm²")
        st.metric("植被覆盖率", f"{vegetation_coverage}%")
        if use_preset:
            st.metric("R因子预设值", f"{r_preset}")

# ========== 标签页2: 一般扰动地表计算 ==========
with tab2:
    st.markdown('<h3 class="sub-header">一般扰动地表土壤流失量计算</h3>', unsafe_allow_html=True)
    
    # 使用扩展或基本模式
    calculation_mode = st.radio("计算模式", ["基本计算", "详细计算（多坡段）"], horizontal=True)
    
    if calculation_mode == "基本计算":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**侵蚀因子**")
            R = st.number_input("R - 降雨侵蚀力因子", 
                               min_value=0.0, value=float(r_preset) if use_preset else 2000.0, 
                               step=100.0, key="r_gen")
            K = st.number_input("K - 土壤可蚀性因子", 
                               min_value=0.0, value=k_factor_db[soil_type_main], 
                               step=0.01, key="k_gen",
                               help="参考值: 砂土0.12, 壤土0.25-0.38, 黏土0.42")
            C = st.slider("C - 植被覆盖因子", 0.0, 1.0, 0.3, 0.05, key="c_gen",
                         help="0表示完全覆盖，1表示无覆盖")
        
        with col2:
            st.markdown("**地形因子**")
            slope_length = st.number_input("λ - 坡长 (m)", min_value=0.0, value=50.0, step=5.0)
            slope_angle = st.slider("θ - 坡度 (°)", 0.0, 90.0, 15.0, 1.0)
            
            # 根据坡度确定m,n值
            if slope_angle < 20:
                m, n = 0.3, 1.2
                slope_type = "缓坡"
            else:
                m, n = 0.5, 1.3
                slope_type = "陡坡"
            
            st.info(f"坡度类型: {slope_type} (m={m}, n={n})")
        
        with col3:
            st.markdown("**工程因子**")
            P = st.slider("P - 水土保持措施因子", 0.0, 1.0, 1.0, 0.1,
                         help="1表示无措施，值越小表示措施效果越好")
            T = st.selectbox("T - 耕作管理因子", [1.0, 0.8, 0.6, 0.4], index=0,
                           help="反映耕作方式对侵蚀的影响")
        
        # 计算LS因子和土壤流失量
        slope_rad = math.radians(slope_angle)
        LS = math.pow(slope_length / 20, m) * math.pow(math.sin(slope_rad) / 0.3, n)
        A_general = R * K * LS * C * P * T * area_general
        
        # 显示结果卡片
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        res_cols = st.columns(4)
        with res_cols[0]:
            st.metric("LS因子", f"{LS:.4f}")
        with res_cols[1]:
            st.metric("单位面积流失量", f"{R * K * LS * C * P * T:.2f} t/hm²")
        with res_cols[2]:
            st.metric("计算面积", f"{area_general} hm²")
        with res_cols[3]:
            st.metric("总流失量", f"{A_general:.2f} t", delta=None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("多坡段详细计算功能需要更多参数输入...")
        # 这里可以扩展多坡段计算逻辑

# ========== 标签页3: 工程开挖面计算 ==========
with tab3:
    st.markdown('<h3 class="sub-header">工程开挖面土壤流失量计算</h3>', unsafe_allow_html=True)
    
    exc_cols = st.columns([2, 1])
    
    with exc_cols[0]:
        # 开挖面参数
        exc_params = st.columns(3)
        with exc_params[0]:
            R_ex = st.number_input("R因子", value=float(r_preset) if use_preset else 2000.0, 
                                  key="r_ex")
            slope_height = st.number_input("坡高 H (m)", min_value=0.0, value=8.0, step=0.5)
            slope_angle_ex = st.slider("坡度 β (°)", 0.0, 90.0, 45.0, 5.0, key="sa_ex")
        
        with exc_params[1]:
            soil_type_ex = st.selectbox("土体类型", ["砂土", "壤土", "黏土", "砾石土"], key="st_ex")
            saturation = st.radio("土体饱和度", ["湿润", "半湿润", "干燥"], horizontal=True, key="sat_ex")
            exposure_time = st.slider("裸露时间 (月)", 1, 36, 12, key="time_ex")
        
        with exc_params[2]:
            # 确定开挖面参数
            if soil_type_ex == "砂土":
                k_ex = 0.12
                porosity = "高"
            elif soil_type_ex == "壤土":
                k_ex = 0.25
                porosity = "中"
            elif soil_type_ex == "黏土":
                k_ex = 0.30
                porosity = "低"
            else:
                k_ex = 0.10
                porosity = "很高"
            
            sat_factor_map = {"湿润": 1.0, "半湿润": 0.85, "干燥": 0.7}
            sat_factor = sat_factor_map[saturation]
            
            st.info(f"土体参数: K={k_ex}, 孔隙度={porosity}")
    
    with exc_cols[1]:
        # 开挖面示意图
        st.markdown("**开挖面示意图**")
        fig = go.Figure()
        
        # 绘制边坡
        x = [0, slope_height / math.tan(math.radians(slope_angle_ex)), slope_height / math.tan(math.radians(slope_angle_ex))]
        y = [0, 0, slope_height]
        
        fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', fillcolor='rgba(139,69,19,0.3)',
                                line=dict(color='saddlebrown', width=3),
                                name=f"开挖面 β={slope_angle_ex}°"))
        
        fig.update_layout(
            title=f"坡高: {slope_height}m, 坡度: {slope_angle_ex}°",
            xaxis_title="水平距离 (m)",
            yaxis_title="高度 (m)",
            height=250,
            showlegend=True,
            margin=dict(t=40, b=20, l=40, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 计算开挖面土壤流失量
    slope_rad_ex = math.radians(slope_angle_ex)
    A_excavation = 4.41 * R_ex * k_ex * sat_factor * slope_height * math.sin(slope_rad_ex) * area_excavation
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    exc_res_cols = st.columns(3)
    with exc_res_cols[0]:
        st.metric("饱和影响系数", f"{sat_factor}")
    with exc_res_cols[1]:
        st.metric("单位面积流失量", f"{4.41 * R_ex * k_ex * sat_factor * slope_height * math.sin(slope_rad_ex):.2f} t/hm²")
    with exc_res_cols[2]:
        st.metric("开挖面总流失量", f"{A_excavation:.2f} t")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 标签页4: 工程堆积体计算 ==========
with tab4:
    st.markdown('<h3 class="sub-header">工程堆积体土壤流失量计算</h3>', unsafe_allow_html=True)
    
    pile_tabs = st.tabs(["基本参数", "堆积体形态", "材料特性"])
    
    with pile_tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            R_pile = st.number_input("R因子", value=float(r_preset) if use_preset else 2000.0, 
                                    key="r_pile")
            pile_height = st.number_input("堆高 H (m)", min_value=0.0, value=6.0, step=0.5)
            pile_angle = st.slider("堆积坡度 φ (°)", 0.0, 90.0, 28.0, 2.0, key="pa_pile")
        
        with col2:
            pile_length = st.number_input("坡长 L (m)", min_value=0.0, value=25.0, step=2.0)
            pile_shape = st.selectbox("堆积体形状", ["锥形", "脊形", "扇形", "不规则形"])
            compaction = st.slider("压实度 (%)", 50, 100, 75, 5)
    
    with pile_tabs[1]:
        # 形状系数
        shape_factors = {
            "锥形": 0.75,
            "脊形": 1.00,
            "扇形": 0.80,
            "不规则形": 0.90
        }
        
        shape_factor = shape_factors[pile_shape]
        
        # 绘制堆积体示意图
        fig = go.Figure()
        
        if pile_shape == "锥形":
            # 简化锥形表示
            theta = np.linspace(0, 2*np.pi, 100)
            r = pile_height
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            fig.add_trace(go.Scatter(x=x, y=y, fill='toself', fillcolor='rgba(210,180,140,0.5)'))
        elif pile_shape == "脊形":
            # 脊形表示
            x = [-pile_length/2, 0, pile_length/2]
            y = [0, pile_height, 0]
            fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', fillcolor='rgba(210,180,140,0.5)'))
        
        fig.update_layout(
            title=f"{pile_shape}堆积体示意图",
            xaxis_title="距离 (m)",
            yaxis_title="高度 (m)",
            height=200,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"形状系数: {shape_factor}")
    
    with pile_tabs[2]:
        material_type = st.selectbox("堆积材料", ["弃渣", "表土", "混合料", "建筑垃圾"])
        gradation = st.selectbox("级配情况", ["良好", "一般", "不良"])
        contains_clay = st.checkbox("含黏粒成分", value=True)
        
        # 材料系数
        if material_type == "弃渣":
            material_factor = 1.0
        elif material_type == "表土":
            material_factor = 0.8
        elif material_type == "建筑垃圾":
            material_factor = 0.6
        else:
            material_factor = 0.9
        
        gradation_factor = 1.0 if gradation == "良好" else 1.2 if gradation == "一般" else 1.5
        clay_factor = 0.9 if contains_clay else 1.0
        compaction_factor = 0.7 + (compaction / 100) * 0.3
    
    # 计算堆积体土壤流失量
    slope_rad_pile = math.radians(pile_angle)
    base_calc = 0.21 * R_pile * pile_height * pile_length * shape_factor * math.pow(math.sin(slope_rad_pile), 1.5)
    material_adjustment = material_factor * gradation_factor * clay_factor * compaction_factor
    A_pile = base_calc * material_adjustment * area_pile
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    pile_res_cols = st.columns(4)
    with pile_res_cols[0]:
        st.metric("形状系数", f"{shape_factor}")
    with pile_res_cols[1]:
        st.metric("材料调整系数", f"{material_adjustment:.3f}")
    with pile_res_cols[2]:
        st.metric("基础计算值", f"{base_calc:.2f} t/hm²")
    with pile_res_cols[3]:
        st.metric("堆积体总流失量", f"{A_pile:.2f} t")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 标签页5: 结果汇总与分析 ==========
with tab5:
    st.markdown('<h3 class="sub-header">📊 土壤流失量测算结果汇总</h3>', unsafe_allow_html=True)
    
    # 汇总数据
    summary_data = {
        "扰动类型": ["一般扰动地表", "工程开挖面", "工程堆积体", "其他扰动"],
        "面积(hm²)": [area_general, area_excavation, area_pile, area_other],
        "单位流失量(t/hm²)": [
            (R * K * LS * C * P * T) if 'A_general' in locals() else 0,
            (4.41 * R_ex * k_ex * sat_factor * slope_height * math.sin(slope_rad_ex)) if 'A_excavation' in locals() else 0,
            (base_calc * material_adjustment) if 'A_pile' in locals() else 0,
            0
        ],
        "总流失量(t)": [
            A_general if 'A_general' in locals() else 0,
            A_excavation if 'A_excavation' in locals() else 0,
            A_pile if 'A_pile' in locals() else 0,
            0
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    
    # 计算总计
    total_loss = df_summary["总流失量(t)"].sum()
    avg_unit_loss = df_summary["单位流失量(t/hm²)"].mean()
    
    # 显示汇总表格
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.dataframe(
            df_summary.style.format({
                "面积(hm²)": "{:.2f}",
                "单位流失量(t/hm²)": "{:.2f}",
                "总流失量(t)": "{:.2f}"
            }).background_gradient(subset=["总流失量(t)"], cmap="YlOrRd"),
            use_container_width=True
        )
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🌍 项目总流失量", f"{total_loss:.2f} t")
        st.metric("📦 平均单位流失量", f"{avg_unit_loss:.2f} t/hm²")
        st.metric("⏱️ 测算年份", f"{calculation_year}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 可视化图表
    st.markdown('<h3 class="sub-header">📈 流失量分布可视化</h3>', unsafe_allow_html=True)
    
    viz_cols = st.columns(2)
    
    with viz_cols[0]:
        # 流失量构成饼图
        fig_pie = px.pie(
            df_summary, 
            values='总流失量(t)', 
            names='扰动类型',
            title='土壤流失量构成',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with viz_cols[1]:
        # 单位流失量柱状图
        fig_bar = px.bar(
            df_summary,
            x='扰动类型',
            y='单位流失量(t/hm²)',
            title='单位面积流失量对比',
            color='单位流失量(t/hm²)',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 报告生成
    st.markdown('<h3 class="sub-header">📄 生成测算报告</h3>', unsafe_allow_html=True)
    
    if st.button("📥 生成完整测算报告", type="primary"):
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
        # 生产建设项目土壤流失量测算报告
        
        ## 1. 项目基本信息
        - **项目名称**: {project_name}
        - **项目地点**: {project_location}
        - **测算年份**: {calculation_year}
        - **总扰动面积**: {total_area:.2f} hm²
        - **主要土壤类型**: {soil_type_main}
        
        ## 2. 测算结果汇总
        - **土壤流失总量**: {total_loss:.2f} t
        - **平均单位流失量**: {avg_unit_loss:.2f} t/hm²
        
        ## 3. 分项计算结果
        {df_summary.to_markdown(index=False)}
        
        ## 4. 主要计算参数
        - R因子（降雨侵蚀力）: {R if 'R' in locals() else '未计算'}
        - K因子（土壤可蚀性）: {K if 'K' in locals() else '未计算'}
        - 植被覆盖率: {vegetation_coverage}%
        
        ## 5. 报告信息
        - 生成时间: {report_time}
        - 测算标准: SL 773-2018
        - 工具版本: 2.0
        
        **注意**: 本报告为自动生成的计算结果，实际应用需结合现场勘察数据。
        """
        
        st.download_button(
            label="下载报告 (Markdown格式)",
            data=report,
            file_name=f"土壤流失测算报告_{project_name}_{calculation_year}.md",
            mime="text/markdown"
        )
        
        st.success("报告已生成！点击上方按钮下载。")

# ========== 标签页6: 参数查询 ==========
with tab6:
    st.markdown('<h3 class="sub-header">📚 SL 773-2018 参数查询手册</h3>', unsafe_allow_html=True)
    
    param_tabs = st.tabs(["R因子", "K因子", "C因子", "其他参数"])
    
    with param_tabs[0]:
        st.markdown("### 降雨侵蚀力因子 R (MJ·mm/(hm²·h))")
        st.markdown("""
        | 地区 | R值范围 | 典型值 | 适用季节 |
        |------|---------|--------|----------|
        | 华南地区 | 5000-7000 | 5800 | 全年，夏季为主 |
        | 华东地区 | 3000-4500 | 3500 | 春夏为主 |
        | 华中地区 | 3500-5000 | 4200 | 夏季集中 |
        | 西南地区 | 3000-4500 | 3800 | 夏季为主 |
        | 华北地区 | 1500-2500 | 1800 | 夏季集中 |
        | 东北地区 | 1800-2800 | 2200 | 夏季为主 |
        | 西北地区 | 800-1800 | 1200 | 夏季短暂 |
        
        **计算方法**: R = ∑(Ei × I30)，其中Ei为次降雨动能，I30为最大30分钟雨强。
        """)
    
    with param_tabs[1]:
        st.markdown("### 土壤可蚀性因子 K (t·hm²·h/(hm²·MJ·mm))")
        st.markdown("""
        | 土壤类型 | K值范围 | 典型值 | 侵蚀敏感性 |
        |----------|---------|--------|------------|
        | 砂土 | 0.10-0.15 | 0.12 | 低 |
        | 砂壤土 | 0.15-0.22 | 0.18 | 较低 |
        | 轻壤土 | 0.22-0.28 | 0.25 | 中等 |
        | 中壤土 | 0.28-0.35 | 0.32 | 较高 |
        | 重壤土 | 0.35-0.40 | 0.38 | 高 |
        | 黏土 | 0.40-0.45 | 0.42 | 很高 |
        
        **影响因素**: 有机质含量、土壤结构、渗透性等。
        """)
    
    with param_tabs[2]:
        st.markdown("### 植被覆盖与管理因子 C")
        st.markdown("""
        | 植被覆盖度 | C值 | 典型植被类型 |
        |------------|-----|--------------|
        | >90% | 0.001-0.01 | 茂密森林、成熟草地 |
        | 70-90% | 0.01-0.05 | 一般林地、灌木丛 |
        | 50-70% | 0.05-0.10 | 稀疏林地、中度草地 |
        | 30-50% | 0.10-0.20 | 退化草地、幼林 |
        | 10-30% | 0.20-0.40 | 严重退化草地 |
        | <10% | 0.40-1.00 | 裸地、施工区 |
        
        **注意**: C因子受植被类型、生长季节、枯落物层等多因素影响。
        """)
    
    with param_tabs[3]:
        st.markdown("### 其他关键参数")
        st.markdown("""
        #### P因子（水土保持措施因子）
        - 无措施: 1.0
        - 简易措施: 0.7-0.9
        - 工程措施: 0.3-0.7
        - 综合措施: 0.1-0.3
        
        #### LS因子（坡度坡长因子）
        - 计算公式: LS = (λ/20)^m × (sinθ/0.3)^n
        - θ<20°时: m=0.3, n=1.2
        - θ≥20°时: m=0.5, n=1.3
        
        #### 开挖面参数
        - 砂土: k=0.12
        - 壤土: k=0.25
        - 黏土: k=0.30
        """)

# ========== 页脚 ==========
st.divider()
footer_cols = st.columns(3)
with footer_cols[0]:
    st.caption("📖 依据标准: SL 773-2018")
with footer_cols[1]:
    st.caption("⚠️ 计算结果需现场验证")
with footer_cols[2]:
    st.caption(f"🕒 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
  Commit message: 首次提交：完整的土壤流失测算工具
