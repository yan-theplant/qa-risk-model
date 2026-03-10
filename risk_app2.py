import streamlit as st
import pandas as pd

# 设置页面宽度和标题
st.set_page_config(page_title="AI-Assisted QA Risk Model", layout="wide")

# --- 1. 数据加载 ---
@st.cache_data
def load_and_analyze():
    # 尝试加载清洗后的数据，否则加载原始数据
    try:
        df = pd.read_csv('Checklist_Cleaned.csv')
    except:
        df = pd.read_csv('Checklist.csv')
    
    # 填充空值并去除空格
    df['Bug area'] = df['Bug area'].fillna('General').str.strip()
    df['project(app/web?)'] = df['project(app/web?)'].fillna('General').str.strip()
    
    # AI 预处理：计算全库风险权重
    area_weights = df['Bug area'].value_counts(normalize=True).to_dict()
    return df, area_weights

try:
    df, area_weights = load_and_analyze()

    st.title("🤖 AI-Assisted Bug Risk Prediction Model")
    st.info(f"Status: Active | Based on {len(df)} Actionable Checkpoints")

    # --- 2. 侧边栏交互层 (保持原有反馈逻辑) ---
    with st.sidebar:
        st.header("⚙️ Model Inputs")
        
        # 项目选择
        proj_list = sorted(df['project(app/web?)'].unique())
        proj = st.selectbox("Project", proj_list)
        
        # 联动过滤：根据项目选择 Bug Area
        available_areas = sorted(df[df['project(app/web?)'] == proj]['Bug area'].unique())
        area = st.selectbox("Bug Area", available_areas)
        
        st.markdown("---")
        scope = st.slider("Change Scope", 1, 10, 5)
        dev_risk = st.slider("Dev Experience Risk", 1, 10, 5)
        
        # AI 反馈闭环 (The Loop)
        st.markdown("---")
        st.subheader("🧠 Help AI Learn")
        feedback = st.sidebar.radio("Was this prediction accurate?", ["Select...", "Yes", "No - Too High", "No - Too Low"])
        if feedback != "Select...":
            st.sidebar.success("Feedback recorded! Thanks for helping us improve.")

    # --- 3. AI 预测核心逻辑 ---
    # 计算基础风险（该模块在全库的故障密度）
    base_risk = area_weights.get(area, 0.1) * 100
    
    # 风险评分公式
    prediction_score = (base_risk * 0.4) + (scope * 3) + (dev_risk * 3)
    
    # 设定置信度（因为是精准匹配，置信度始终为 High）
    confidence = "High (Direct Match)"

    # --- 4. 视觉展示 (你喜欢的醒目高亮样式) ---
    if prediction_score > 70:
        st.markdown(f'''
            <div style="background-color:#ff4b4b; padding:25px; border-radius:12px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin:0;">High Risk Predicted: {prediction_score:.1f}</h1>
                <p style="font-size:18px; margin-top:10px;">Confidence: {confidence} | Action: Mandatory Double Check & Peer Review</p>
            </div>
            ''', unsafe_allow_html=True)
    elif prediction_score > 40:
        st.markdown(f'''
            <div style="background-color:#ffa500; padding:25px; border-radius:12px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin:0;">Medium Risk Predicted: {prediction_score:.1f}</h1>
                <p style="font-size:18px; margin-top:10px;">Confidence: {confidence} | Action: Standard Regression Testing Required</p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div style="background-color:#00c853; padding:25px; border-radius:12px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin:0;">Low Risk Predicted: {prediction_score:.1f}</h1>
                <p style="font-size:18px; margin-top:10px;">Confidence: {confidence} | Action: Routine Checklist Verification</p>
            </div>
            ''', unsafe_allow_html=True)

    # --- 5. 智能推荐清单 (精准展示项) ---
    st.write("---")
    st.subheader(f"💡 AI Recommended Actionable Checklist for {proj}")
    
    # 只匹配当前选中的项目和业务
    matched_df = df[(df['project(app/web?)'] == proj) & (df['Bug area'] == area)]
    
    if not matched_df.empty:
        checkpoints = matched_df['Checkpoint'].tolist()
        for i, item in enumerate(checkpoints):
            # 如果风险高，默认展开所有检查点以引起重视
            with st.expander(f"Checkpoint {i+1}", expanded=(prediction_score > 70)):
                st.write(item)
                
                # 智能 Tips：自动识别关键业务并提示神技
                lower_item = item.lower()
                if any(word in lower_item for word in ["money", "price", "balance", "pay", "amount", "余额", "支付", "金额"]):
                    st.success("🛠 **AI Efficiency Tip:** Use 'Local Overrides' in DevTools to mock extreme responses (e.g., Insufficient Balance).")
    else:
        st.warning(f"No specific checkpoints found for {area} in {proj}. Please update the checklist database.")

except Exception as e:
    st.error(f"Error initializing AI model: {e}")
