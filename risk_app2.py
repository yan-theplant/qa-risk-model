import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="QA Risk Assessment Center", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for enhanced UI
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
    # Load data
    try:
        # Using Checklist.csv as requested
        df = pd.read_csv('Checklist.csv')
    except:
        # Fallback to cleaned version if exists
        df = pd.read_csv('Checklist_Cleaned.csv')
        
    # Data Cleaning
    df['project(app/web?)'] = df['project(app/web?)'].fillna('Unknown').str.strip()
    df['Bug area'] = df['Bug area'].fillna('Unknown').str.strip()
    
    # AI Logic: Calculate risk weight for Project + Area
    df['Project_Area'] = df['project(app/web?)'] + " | " + df['Bug area']
    pair_counts = df['Project_Area'].value_counts()
    max_count = pair_counts.max()
    risk_weights = (pair_counts / max_count).to_dict()
    
    return df, risk_weights

try:
    df, risk_weights = load_and_process_data()

    st.title("🛡️ AI-Assisted Bug Prediction & Risk Assessment")
    # Dynamic data count
    st.caption(f"Driving Data: {len(df)} Historical Bug Checkpoints")
    st.write("")

    # --- Sidebar ---
    st.sidebar.header("📋 Assessment Parameters")
    project_list = sorted(df['project(app/web?)'].unique())
    selected_project = st.sidebar.selectbox("1. Project", project_list)
    
    # Linked Dropdown: Filter Areas based on Project
    available_areas = sorted(df[df['project(app/web?)'] == selected_project]['Bug area'].unique())
    selected_area = st.sidebar.selectbox("2. Bug Area", available_areas)
    
    st.sidebar.markdown("---")
    scope_score = st.sidebar.slider("3. Change Scope (1-10)", 1, 10, 5,
                                    help="1: Copy change, 5: New feature, 10: Core architecture refactor")
    dev_exp = st.sidebar.slider("4. Dev Experience Risk (1-10)", 1, 10, 5,
                                help="1: Senior Expert, 10: Newcomer or unfamiliar with this module")

    # --- Calculation Logic ---
    combined_key = f"{selected_project} | {selected_area}"
    hist_val = risk_weights.get(combined_key, 0.2) * 100
    final_score = (hist_val * 0.4) + (scope_score * 3) + (dev_exp * 3)

    # --- Visual Display ---
    if final_score > 70:
        st.markdown(f'<div class="risk-high">🚨 High Risk Alert (Score: {final_score:.1f})</div>', unsafe_allow_html=True)
    elif final_score > 40:
        st.markdown(f'<div class="risk-medium">⚠️ Medium Risk (Score: {final_score:.1f})</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low">✅ Risk Controlled (Score: {final_score:.1f})</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Risk Factor Analysis")
        stats_data = pd.DataFrame({
            'Factor': ['Historical Bug Data', 'Change Scope', 'Dev Risk'],
            'Weight': [hist_val * 0.4, scope_score * 3, dev_exp * 3]
        })
        st.bar_chart(stats_data, x='Factor', y='Weight', color="#ff4b4b" if final_score > 70 else "#00c853")
        
        if final_score > 70:
            st.warning("👉 **Double Check Mandatory!** Please contact the core QA team for a cross-review.")

    with col2:
        st.subheader(f"💡 {selected_project} | {selected_area} Actionable Checklist")
        # Filter Checklist
        matched_df = df[(df['project(app/web?)'] == selected_project) & (df['Bug area'] == selected_area)]
        
        if not matched_df.empty:
            st.write(f"Based on history, please **prioritize** the following {len(matched_df.head(10))} items:")
            for i, row in enumerate(matched_df['Checkpoint'].tolist()[:10]):
                # Highlight if high risk
                if final_score > 70:
                    st.error(f"**Critical Check {i+1}:** {row}")
                else:
                    st.info(f"**Suggested Check {i+1}:** {row}")
                
                # Integration with "Local Overrides" Tip
                lower_row = row.lower()
                if any(k in lower_row for k in ["money", "price", "balance", "pay", "amount", "余额", "支付", "金额"]):
                    st.success("🛠 **Efficiency Tip:** Use 'Local Overrides' to mock extreme responses (e.g., Insufficient Balance).")
        else:
            st.info("ℹ️ No specific historical bug records for this project module. Please refer to general checklists.")

except Exception as e:
    st.error(f"❌ Application Error: {e}")
