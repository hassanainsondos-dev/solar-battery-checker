import streamlit as st

st.header("📊 أولاً: الحسابات والتشخيص اليدوي")

tab1, tab2 = st.tabs(["⚡ فحص اللوح الشمسي", "🔋 فحص البطارية"])

with tab1:
    st.subheader("إدخال القراءات المقاسة للوح الشمسي")
    col1, col2 = st.columns(2)
    
    with col1:
        v_oc = st.number_input("فولتية الدارة المفتوحة Voc (Volt)", value=21.0)
        i_sc = st.number_input("تيار القصر Isc (Ampere)", value=5.5)
    with col2:
        p_rated = st.number_input("القدرة الاسمية المدونة على اللوح (Watt)", value=100.0)
        v_mp = st.number_input("فولتية أقصى قدرة Vmp (Volt)", value=17.5)
        i_mp = st.number_input("تيار أقصى قدرة Imp (Ampere)", value=5.1)

    if st.button("تشخيص حالة اللوح"):
        p_measured = v_mp * i_mp
        eff = (p_measured / p_rated) * 100 if p_rated > 0 else 0
        
        st.metric(label="القدرة المقاسة الفعلية", value=f"{p_measured:.2f} W")
        st.metric(label="نسبة الكفاءة الحالية", value=f"{eff:.1f}%")
        
        if eff >= 80:
            st.success("حالة اللوح: ممتازة / جيدة جداً")
        elif 50 <= eff < 80:
            st.warning("حالة اللوح: متوسطة - يوجد تراجع في الأداء")
        else:
            st.error("حالة اللوح: متهالك أو يوجد عطل في الخلايا/الدايود")

with tab2:
    st.subheader("إدخال قراءات البطارية المقاسة")
    col1_b, col2_b = st.columns(2)
    
    with col1_b:
        r_int = st.number_input("المقاومة الداخلية المقاسة (mΩ)", value=25.0)
    with col2_b:
        r_new = st.number_input("المقاومة الداخلية للبطارية وهي جديدة (mΩ)", value=10.0)

    if st.button("حساب صحة البطارية (SoH)"):
        soh = max(0, 100 - ((r_int - r_new) / r_new) * 50)
        
        st.metric(label="حالة صحة البطارية (SoH)", value=f"{soh:.1f}%")
        
        if soh >= 80:
            st.success("البطارية بحالة ممتازة")
        elif 50 <= soh < 80:
            st.warning("البطارية متوسطة الكفاءة")
        else:
            st.error("البطارية متهالكة وتحتاج إلى استبدال")