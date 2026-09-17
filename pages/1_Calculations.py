import streamlit as st

st.header("📊 أولاً: الحسابات والتشخيص اليدوي")

tab1, tab2 = st.tabs(["⚡ فحص اللوح الشمسي", "🔋 فحص البطارية"])

# =========================================================
# دوال الحساب - اللوح الشمسي
# =========================================================

def correct_to_stc(v_oc, i_sc, temp_meas, irradiance_meas,
                    alpha, beta, temp_ref=25, irradiance_ref=1000):
    """تصحيح Voc و Isc المقاسين ليصبحا مكافئين لظروف STC (25°C, 1000 W/m2)"""
    delta_t = temp_meas - temp_ref
    voc_stc = v_oc / (1 + (beta / 100) * delta_t)
    isc_stc = i_sc * (irradiance_ref / irradiance_meas) / (1 + (alpha / 100) * delta_t)
    return voc_stc, isc_stc


def get_solar_probable_causes(voc_ratio, isc_ratio, fill_factor):
    """ترجيح الاحتمالات حسب نمط انحراف Voc و Isc و FF عن القيم المرجعية"""
    scores = {
        "تظليل جزئي أو اتساخ على سطح اللوح": 0,
        "تشققات دقيقة في الخلايا (Micro-cracks)": 0,
        "عطل في دايود التمرير أو انقطاع بالتوصيل": 0,
        "مقاومة توالي عالية (لحام / وصلات ضعيفة)": 0,
        "تدهور طبيعي مرتبط بعمر اللوح": 0,
    }

    if isc_ratio < 0.90 and voc_ratio >= 0.95:
        scores["تظليل جزئي أو اتساخ على سطح اللوح"] += 3
        scores["تشققات دقيقة في الخلايا (Micro-cracks)"] += 1

    if voc_ratio < 0.85 and isc_ratio >= 0.90:
        scores["عطل في دايود التمرير أو انقطاع بالتوصيل"] += 3

    if voc_ratio >= 0.90 and isc_ratio >= 0.90 and fill_factor < 0.65:
        scores["مقاومة توالي عالية (لحام / وصلات ضعيفة)"] += 3

    if isc_ratio < 0.90 and fill_factor < 0.70:
        scores["تشققات دقيقة في الخلايا (Micro-cracks)"] += 2

    if 0.85 <= voc_ratio < 0.95 and 0.85 <= isc_ratio < 0.95:
        scores["تدهور طبيعي مرتبط بعمر اللوح"] += 2

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = [item for item in ranked if item[1] > 0]

    if not ranked:
        ranked = [("سبب غير محدد بوضوح - يُنصح بفحص بصري شامل", 1)]

    return ranked


# =========================================================
# دوال الحساب - البطارية
# =========================================================

def calculate_soh(r_int, r_new):
    return max(0, 100 - ((r_int - r_new) / r_new) * 50)


def get_battery_probable_causes(r_ratio, cycle_ratio):
    scores = {
        "التملح (Sulfation) بسبب الشحن الجزئي المتكرر": 0,
        "نهاية العمر الافتراضي الطبيعي (تجاوز عدد الدورات)": 0,
        "خلية ضعيفة أو مشكلة في الوصلات الداخلية": 0,
    }

    if r_ratio > 1.5 and cycle_ratio < 0.8:
        scores["التملح (Sulfation) بسبب الشحن الجزئي المتكرر"] += 3
        scores["خلية ضعيفة أو مشكلة في الوصلات الداخلية"] += 1

    if cycle_ratio >= 0.8:
        scores["نهاية العمر الافتراضي الطبيعي (تجاوز عدد الدورات)"] += 3

    if r_ratio > 2.0 and cycle_ratio < 0.4:
        scores["خلية ضعيفة أو مشكلة في الوصلات الداخلية"] += 2

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = [item for item in ranked if item[1] > 0]

    if not ranked:
        ranked = [("سبب غير محدد بوضوح - يُنصح بفحص إضافي", 1)]

    return ranked


# =========================================================
# تبويب اللوح الشمسي
# =========================================================

with tab1:
    st.subheader("إدخال القراءات المقاسة للوح الشمسي")

    st.markdown("**القراءات الميدانية (اللي بتقيسيها بنفسك):**")
    col1, col2 = st.columns(2)
    with col1:
        v_oc = st.number_input("فولتية الدارة المفتوحة Voc (Volt)", value=21.0)
        i_sc = st.number_input("تيار القصر Isc (Ampere)", value=5.5)
        v_mp = st.number_input("فولتية أقصى قدرة Vmp (Volt)", value=17.5)
        i_mp = st.number_input("تيار أقصى قدرة Imp (Ampere)", value=5.1)
    with col2:
        temp_meas = st.number_input("درجة حرارة اللوح أثناء القياس (°C)", value=45.0)
        irradiance_meas = st.number_input("شدة الإشعاع أثناء القياس (W/m²)", value=800.0)

    st.markdown("**القيم المدونة على ملصق اللوح / الداتاشيت:**")
    col3, col4 = st.columns(2)
    with col3:
        p_rated = st.number_input("القدرة الاسمية Pmax (Watt)", value=100.0)
        voc_rated = st.number_input("Voc المدون على الداتاشيت (Volt)", value=22.0)
        isc_rated = st.number_input("Isc المدون على الداتاشيت (Ampere)", value=6.0)
    with col4:
        alpha = st.number_input("معامل حرارة التيار α (%/°C)", value=0.05, format="%.3f")
        beta = st.number_input("معامل حرارة الجهد β (%/°C)", value=-0.29, format="%.3f")

    if st.button("تشخيص حالة اللوح"):
        # الخطوة 1: تصحيح القراءات لظروف STC
        voc_stc, isc_stc = correct_to_stc(v_oc, i_sc, temp_meas, irradiance_meas, alpha, beta)

        # الخطوة 2: حساب القدرة الفعلية والكفاءة ومعامل الملء
        p_measured = v_mp * i_mp
        eff = (p_measured / p_rated) * 100 if p_rated > 0 else 0
        fill_factor = p_measured / (voc_stc * isc_stc) if (voc_stc * isc_stc) > 0 else 0

        voc_ratio = voc_stc / voc_rated if voc_rated > 0 else 0
        isc_ratio = isc_stc / isc_rated if isc_rated > 0 else 0

        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("القدرة المقاسة الفعلية", f"{p_measured:.2f} W")
        col_b.metric("نسبة الكفاءة الحالية", f"{eff:.1f}%")
        col_c.metric("معامل الملء (FF)", f"{fill_factor:.3f}")
        st.caption(f"Voc بعد تصحيح STC: {voc_stc:.2f} V  |  Isc بعد تصحيح STC: {isc_stc:.2f} A")

        # الخطوة 3: القرار - 3 مستويات
        if eff >= 80:
            st.success("✅ حالة اللوح: ممتازة / جيدة جداً - الكفاءة ضمن المدى الطبيعي")
        elif 65 <= eff < 80:
            st.warning("⚠️ تحذير مبكر: بداية تراجع بسيط في الأداء - يُنصح بالمتابعة والتنظيف")
        else:
            st.error("❌ انخفاض واضح في الكفاءة")
            causes = get_solar_probable_causes(voc_ratio, isc_ratio, fill_factor)
            st.write("**الاحتمالات المرجّحة لسبب الانخفاض:**")
            for i, (cause, score) in enumerate(causes, start=1):
                st.write(f"{i}. {cause}")


# =========================================================
# تبويب البطارية
# =========================================================

with tab2:
    st.subheader("إدخال قراءات البطارية المقاسة")

    col1_b, col2_b = st.columns(2)
    with col1_b:
        r_int = st.number_input("المقاومة الداخلية المقاسة (mΩ)", value=25.0)
        r_new = st.number_input("المقاومة الداخلية للبطارية وهي جديدة (mΩ)", value=10.0)
    with col2_b:
        cycles = st.number_input("عدد دورات الشحن حتى الآن", min_value=0, value=300)
        cycles_rated = st.number_input("عدد الدورات المتوقع من الداتاشيت", min_value=1, value=500)

    if st.button("حساب صحة البطارية (SoH)"):
        soh = calculate_soh(r_int, r_new)
        r_ratio = r_int / r_new if r_new > 0 else 1
        cycle_ratio = cycles / cycles_rated if cycles_rated > 0 else 0

        st.divider()
        st.metric(label="حالة صحة البطارية (SoH)", value=f"{soh:.1f}%")
        st.caption(f"عدد الدورات: {cycles} من أصل {cycles_rated} دورة متوقعة")

        if soh >= 80:
            st.success("✅ البطارية بحالة ممتازة")
        elif 65 <= soh < 80:
            st.warning("⚠️ تحذير مبكر: بداية تراجع بالكفاءة - يُنصح بالمتابعة الدورية")
        else:
            st.error("❌ انخفاض واضح في حالة الصحة")
            causes = get_battery_probable_causes(r_ratio, cycle_ratio)
            st.write("**الاحتمالات المرجّحة لسبب الانخفاض:**")
            for i, (cause, score) in enumerate(causes, start=1):
                st.write(f"{i}. {cause}")
