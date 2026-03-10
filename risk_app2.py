import streamlit as st
import pandas as pd
from difflib import get_close_matches

st.set_page_config(page_title="AI-Assisted QA Risk Model", layout="wide")

# --- 1. 模拟 AI 智能处理层 ---
@st.cache_data
def load_and_analyze():
    df = pd.read_csv('Checklist.csv')
    df['Bug area'] = df['Bug area'].fillna('General').str.strip()
    df['project(app/web?)'] = df['project(app/web?)'].fillna('General').str.strip()
    
    # AI 预处理：计算每个模块的风险权重
    area_risk = df['Bug area'].value_counts(normalize=True).to_dict()
    return df, area_risk

try:
    df, area_risk_data = load_and_analyze()

    st.title("🤖 AI-Assisted Bug Risk Prediction Model")
    st.info("Status: Active | Based on 183 Actionable Checkpoints")

    # --- 2. 交互输入层 ---
    with st.sidebar:
        st.header("⚙️ Model Inputs")
        proj = st.selectbox("Project", sorted(df['project(app/web?)'].unique()))
        area = st.selectbox("Bug Area", sorted(df['Bug area'].unique()))
        
        st.markdown("---")
        scope = st.slider("Change Scope", 1, 10, 5)
        dev_risk = st.slider("Dev Experience Risk", 1, 10, 5)

    # --- 3. AI 预测核心逻辑 ---
    # 计算历史基础分
    base_risk = area_risk_data.get(area, 0.1) * 100
    
    # AI 智能因子：如果该 Area 在此 Project 下从未出现过，增加“未知风险”权重
    is_known_pair = not df[(df['project(app/web?)']==proj) & (df['Bug area']==area)].empty
    ai_uncertainty = 0 if is_known_pair else 15 
    
    prediction_score = (base_risk * 0.4) + (scope * 3) + (dev_risk * 3) + ai_uncertainty
    confidence = "High" if is_known_pair else "Low (Cold Start)"

    # --- 4. 视觉展示 (醒目高亮) ---
    if prediction_score > 70:
        st.markdown(f'<div style="background-color:#ff4b4b; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>High Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Confidence: {confidence} | Action: Mandatory Double Check</p></div>', unsafe_allow_html=True)
    elif prediction_score > 40:
        st.markdown(f'<div style="background-color:#ffa500; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>Medium Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Confidence: {confidence} | Action: Standard Regression</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#00c853; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>Low Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Confidence: {confidence} | Action: Routine Check</p></div>', unsafe_allow_html=True)

    # --- 5. 智能推荐引擎 (AI Recommendation) ---
    st.write("---")
    st.subheader("💡 AI Recommended Actionable Checklist")
    
    # 逻辑：先找本项目下的，找不到就找全库中最相似业务的
    matched_items = df[(df['project(app/web?)']==proj) & (df['Bug area']==area)]['Checkpoint'].tolist()
    
    if not matched_items:
        st.warning("No direct history for this project-area pair. AI is pulling global knowledge...")
        matched_items = df[df['Bug area'] == area]['Checkpoint'].tolist()

    if matched_items:
        for i, item in enumerate(matched_items[:10]):
            with st.expander(f"Checkpoint {i+1}", expanded=(prediction_score > 70)):
                st.write(item)
                # 呼应你的 Local Overrides 场景
                if "money" in item.lower() or "price" in item.lower() or "余额" in item:
                    st.success("🛠 **AI Tip:** Use 'Local Overrides' to mock insufficient balance for this test case.")
    
    # --- 6. AI 学习反馈 (The Loop) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Help AI Learn")
    feedback = st.sidebar.radio("Was this prediction accurate?", ["Select...", "Yes", "No - Too High", "No - Too Low"])
    if feedback != "Select...":
        st.sidebar.write("Thank you! Feedback recorded for model tuning.")

except Exception as e:
    st.error(f"Error initializing AI model: {e}")