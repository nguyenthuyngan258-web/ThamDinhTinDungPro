import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Cấu hình giao diện (Layout)
st.set_page_config(page_title="Hệ thống Thẩm định Tín dụng Pro", layout="wide")

# 2. CSS tùy chỉnh (Giao diện hiện đại)
st.markdown("""
    <style>
    .metric-card {background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #004a99; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .stApp {background-color: #f4f7f6;}
    h1 {color: #004a99; text-align: center; font-weight: 800;}
    </style>
""", unsafe_allow_html=True)

# 3. Tiêu đề
st.markdown("<h1>🏦 HỆ THỐNG THẨM ĐỊNH TÍN DỤNG CÁ NHÂN</h1>", unsafe_allow_html=True)

# 4. Sidebar - Nhập liệu chuyên nghiệp
with st.sidebar:
    st.header("⚙️ Cấu hình Hồ sơ Thẩm định")
    
    st.subheader("I. Thông tin Khoản vay")
    amount = st.number_input("Số tiền vay (Triệu VNĐ)", 50, 10000, 500)
    term = st.number_input("Thời hạn (tháng)", 6, 360, 36)
    rate = st.slider("Lãi suất (%/năm)", 5.0, 20.0, 10.0)
    
    st.subheader("II. Thông tin Tài chính")
    income = st.number_input("Thu nhập hàng tháng (Triệu VNĐ)", 10.0)
    dependents = st.number_input("Số người phụ thuộc", 0, 10, 0)
    old_debt = st.number_input("Dư nợ hiện tại (Triệu VNĐ)", 0.0)
    
    st.subheader("III. TSĐB & CIC")
    asset_value = st.number_input("Giá trị TSĐB (Triệu VNĐ)", 0.0)
    cic_score = st.selectbox("Kết quả CIC", ["Tốt", "Trung bình", "Xấu"])

# 5. Logic xử lý (Tính toán DTI, LAV)
monthly_pmt = (amount / term) + (amount * (rate/100) / 12)
# DTI tính trên thu nhập sau khi trừ chi phí sinh hoạt (giả định 3tr/người)
net_income = income - (dependents * 3.0)
dti = ((monthly_pmt + old_debt) / net_income) * 100 if net_income > 0 else 100
lav = (amount / asset_value) * 100 if asset_value > 0 else 0

# 6. Dashboard kết quả
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("📊 Kết quả Thẩm định")
    st.metric("Tỷ lệ DTI", f"{dti:.1f}%")
    st.metric("Tỷ lệ LAV", f"{lav:.1f}%")
    
    if dti < 40 and lav < 80 and cic_score == "Tốt":
        st.success("✅ TRẠNG THÁI: PHÊ DUYỆT")
    elif dti < 60 and cic_score != "Xấu":
        st.warning("⚠️ TRẠNG THÁI: CHUYỂN THẨM ĐỊNH CHUYÊN SÂU")
    else:
        st.error("❌ TRẠNG THÁI: TỪ CHỐI")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("📈 Thước đo Rủi ro Tài chính")
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = dti,
        gauge = {'axis': {'range': [0, 100]}, 
                 'bar': {'color': "#004a99"},
                 'steps': [{'range': [0, 40], 'color': "lightgreen"},
                           {'range': [40, 60], 'color': "orange"}]},
        title = {'text': "DTI Risk Meter"}))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 7. Tính năng xuất báo cáo chuyên nghiệp
st.subheader("📋 Bảng tổng hợp dữ liệu thẩm định")
df_report = pd.DataFrame({
    "Chỉ tiêu": ["Số tiền vay", "Thời hạn", "DTI", "LAV", "CIC"],
    "Giá trị": [f"{amount} Tr", f"{term} tháng", f"{dti:.1f}%", f"{lav:.1f}%", cic_score]
})
st.table(df_report)

if st.download_button("📥 Xuất báo cáo thẩm định (CSV)", df_report.to_csv(index=False), "tham_dinh.csv"):
    st.balloons()
