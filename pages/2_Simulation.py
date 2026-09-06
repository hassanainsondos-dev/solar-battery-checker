import streamlit as st

st.header("📈 ثانياً: محاكاة أداء اللوح والظروف البيئية")

st.subheader("إعدادات سيناريو المحاكاة")

col_a, col_b = st.columns(2)
with col_a:
    irradiance = st.slider("مستوى الإشعاع الشمسي (W/m²)", 100, 1000, 800, 50)
    temp = st.slider("درجة الحرارة (°C)", 10, 60, 25, 1)
with col_b:
    shading = st.checkbox("تفعيل محاكاة التظليل الجزئي")
    fault = st.checkbox("محاكاة عطل في أحد الدايودات (Bypass Diode Fault)")

# حسابات القدرة المحاكاة
base_power = 150.0
power = base_power * (irradiance / 1000.0) * (1 - 0.004 * (temp - 25))

if shading:
    power *= 0.5
if fault:
    power *= 0.6

st.markdown("---")
st.subheader("نتائج المحاكاة الحالية")
st.metric(label="القدرة المخرجة المحاكاة", value=f"{power:.2f} Watt")

if fault:
    st.error("⚠️ تنبيه: تم اكتشاف انخفاض حاد في الجهد بسبب عطل الدايود!")
elif shading:
    st.warning("⚠️ تنبيه: التظليل يقلل كفاءة اللوح بشكل ملحوظ.")
else:
    st.success("✅ النظام يعمل بشكل طبيعي ضمن الظروف المحددة.")