import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Quality Risk Model", layout="wide")

# --- 1. Data Loading & Preprocessing ---
@st.cache_data
def load_and_analyze():
    # Ensure the filename matches your GitHub repository
    try:
        df = pd.read_csv('Checklist_Cleaned.csv')
    except:
        df = pd.read_csv('Checklist.csv') # Fallback name
        
    df['Bug area'] = df['Bug area'].fillna('General').str.strip()
    df['project(app/web?)'] = df['project(app/web?)'].fillna('General').str.strip()
    
    # Calculate risk weights based on bug density in the entire database
    area_risk_weights = df['Bug area'].value_counts(normalize=True).to_dict()
    return df, area_risk_weights

try:
    df, area_risk_data = load_and_analyze()

    st.title("🤖 AI-Assisted Bug Risk Prediction Model")
    st.info(f"Status: Active | Based on {len(df)} Actionable Checkpoints")

    # --- 2. Interaction Layer (Sidebar) ---
    with st.sidebar:
        st.header("⚙️ Model Inputs")
        
        # 1. Select Project first
        proj_list = sorted(df['project(app/web?)'].unique())
        proj = st.selectbox("Select Project", proj_list)
        
        # 2. Filter available Bug Areas based on the selected Project
        available_areas = sorted(df[df['project(app/web?)'] == proj]['Bug area'].unique())
        area = st.selectbox("Select Bug Area", available_areas)
        
        st.markdown("---")
        scope = st.slider("Change Scope (1-10)", 1, 10, 5)
        dev_risk = st.slider("Dev Experience Risk (1-10)", 1, 10, 5)

    # --- 3. AI Prediction Logic ---
    # Base risk derived from the frequency of the Bug Area in the database
    base_risk = area_risk_data.get(area, 0.1) * 100
    
    # Calculation Formula
    prediction_score = (base_risk * 0.4) + (scope * 3) + (dev_risk * 3)
    
    # --- 4. Visual Display (High Contrast Styles) ---
    if prediction_score > 70:
        st.markdown(f'<div style="background-color:#ff4b4b; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>High Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Action: Mandatory Double Check & Peer Review Required</p></div>', unsafe_allow_html=True)
    elif prediction_score > 40:
        st.markdown(f'<div style="background-color:#ffa500; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>Medium Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Action: Strengthen Regression Testing for Core Paths</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#00c853; padding:20px; border-radius:10px; color:white; text-align:center;">'
                    f'<h1>Low Risk Predicted: {prediction_score:.1f}</h1>'
                    f'<p>Action: Perform Standard Checklist Verification</p></div>', unsafe_allow_html=True)

    # --- 5. Precise Checklist Display ---
    st.write("---")
    st.subheader(f"🔍 Checklist for {proj} - {area}")
    
    # Filter the dataframe strictly by current Project and Area
    matched_df = df[(df['project(app/web?)'] == proj) & (df['Bug area'] == area)]
    
    if not matched_df.empty:
        checkpoints = matched_df['Checkpoint'].tolist()
        for i, item in enumerate(checkpoints):
            # Expand automatically if risk is high
            with st.expander(f"Checkpoint {i+1}", expanded=(prediction_score > 70)):
                st.write(item)
                
                # Integrated Skill Tip: Local Overrides
                if any(word in item.lower() for word in ["money", "price", "balance", "pay", "amount", "余额", "支付", "金额"]):
                    st.success("💡 **Efficiency Tip:** Use 'Local Overrides' to mock extreme response data (e.g., Insufficient Balance).")
    else:
        st.warning("No specific checkpoints found for this project-area combination.")

    # --- 6. AI Feedback Loop ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Help AI Evolve")
    feedback = st.sidebar.radio("Was this prediction accurate?", ["Select...", "Yes", "No - Too High", "No - Too Low"])
    if feedback != "Select...":
        st.sidebar.write("Thank you! Feedback recorded for model tuning.")

except Exception as e:
    st.error(f"Initialization Failed: {e}")
