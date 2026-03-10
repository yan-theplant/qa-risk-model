import streamlit as st
import pandas as pd

# 1. 页面配置
st.set_page_config(page_title="QA 团队风险评估中心", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS 让界面更漂亮
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .risk-high {
        padding: 20px;
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 30px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-medium {
        padding: 20px;
        background-color: #ffa500;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 30px;
        margin-bottom: 20px;
    }
    .risk-low {
        padding: 20px;
        background-color: #00c853;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 30px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    # 读取数据
    df = pd.read_csv('Checklist.csv')
    # 清洗数据
    df['project(app/web?)'] = df['project(app/web?)'].fillna('Unknown').str.strip()
    df['Bug area'] = df['Bug area'].fillna('Unknown').str.strip()
    
    # 计算项目+业务的历史风险权重
    df['Project_Area'] = df['project(app/web?)'] + " | " + df['Bug area']
    pair_counts = df['Project_Area'].value_counts()
    max_count = pair_counts.max()
    risk_weights = (pair_counts / max_count).to_dict()
    
    return df, risk_weights

try:
    df, risk_weights = load_and_process_data()

    st.title("🛡️ 智能缺陷预测与风险评估系统")
    st.caption("驱动数据：183条历史缺陷 ")
    st.write("")

    # --- 侧边栏 ---
    st.sidebar.header("📋 录入评估参数")
    project_list = sorted(df['project(app/web?)'].unique())
    selected_project = st.sidebar.selectbox("1. 所属项目", project_list)
    
    available_areas = sorted(df[df['project(app/web?)'] == selected_project]['Bug area'].unique())
    selected_area = st.sidebar.selectbox("2. 业务模块", available_areas)
    
    st.sidebar.markdown("---")
    scope_score = st.sidebar.slider("3. 代码改动规模 (1-10)", 1, 10, 5, help="1:改文案, 5:新功能, 10:底层架构重构")
    dev_exp = st.sidebar.slider("4. 开发人员风险 (1-10)", 1, 10, 5, help="1:核心老手, 10:刚入职或不熟悉该模块")

    # --- 计算逻辑 ---
    combined_key = f"{selected_project} | {selected_area}"
    hist_val = risk_weights.get(combined_key, 0.2) * 100
    final_score = (hist_val * 0.4) + (scope_score * 3) + (dev_exp * 3)

    # --- 视觉呈现 ---
    
    # 醒目的红色/橙色/绿色大Banner
    if final_score > 70:
        st.markdown(f'<div class="risk-high">🚨 高风险预警 (Score: {final_score:.1f})</div>', unsafe_allow_html=True)
    elif final_score > 40:
        st.markdown(f'<div class="risk-medium">⚠️ 中等风险 (Score: {final_score:.1f})</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low">✅ 风险受控 (Score: {final_score:.1f})</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 风险构成分析")
        stats_data = pd.DataFrame({
            '维度': ['历史缺陷因素', '本次改动规模', '人员不确定性'],
            '权重分值': [hist_val * 0.4, scope_score * 3, dev_exp * 3]
        })
        st.bar_chart(stats_data, x='维度', y='权重分值', color="#ff4b4b" if final_score > 70 else "#00c853")
        
        if final_score > 70:
            st.warning("👉 **此任务必须触发 Double Check 机制！** 请联系 3 人专项小组进行交叉评审。")

    with col2:
        st.subheader(f"💡 {selected_project} | {selected_area} 专项避坑指南")
        # 筛选 Checklist
        matched_df = df[(df['project(app/web?)'] == selected_project) & (df['Bug area'] == selected_area)]
        
        if not matched_df.empty:
            st.write(f"根据历史数据，请**优先核对**以下 {len(matched_df.head(10))} 项：")
            for i, row in enumerate(matched_df['Checkpoint'].tolist()[:10]):
                # 高风险时加重显示
                if final_score > 70:
                    st.error(f"**重点核查 {i+1}：** {row}")
                else:
                    st.info(f"**建议检查 {i+1}：** {row}")
        else:
            st.info("ℹ️ 该项目模块暂无特定历史 Bug 记录，请参考通用业务 Checklist。")

except Exception as e:
    st.error(f"❌ 运行出错了：{e}")
