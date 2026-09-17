import streamlit as st

st.header("Calculations - الحسابات والتشخيص")

tab1, tab2 = st.tabs(["Solar Panel - فحص اللوح الشمسي", "Battery - فحص البطارية"])

# =========================================================
# قاعدة بيانات مرجعية مبسطة
# =========================================================

SOLAR_PANELS = {
    "Generic 100W (default example)": {
        "voc_rated": 22.0, "isc_rated": 6.0, "pmax_rated": 100.0,
        "alpha": 0.05, "beta": -0.29,
    },
    "Jinko Solar 450W": {
        "voc_rated": 49.5, "isc_rated": 11.62, "pmax_rated": 450.0,
        "alpha": 0.05, "beta": -0.29,
    },
    "Longi 445W": {
        "voc_rated": 49.9, "isc_rated": 11.36, "pmax_rated": 445.0,
        "alpha": 0.045, "beta": -0.28,
    },
    "Canadian Solar 340W": {
        "voc_rated": 46.3, "isc_rated": 9.46, "pmax_rated": 340.0,
        "alpha": 0.04, "beta": -0.30,
    },
    "غير ذلك / إدخال يدوي": None,
}

BATTERIES = {
    "Lithium-ion 100Ah (default example)": {
        "r_new": 10.0, "cycles_rated": 2000,
    },
    "Lead-acid 100Ah": {
        "r_new": 6.0, "cycles_rated": 500,
    },
    "غير ذلك / إدخال يدوي": None,
}

WEATHER_TO_IRRADIANCE = {
    "Sunny and clear - شمس صافية": 1000,
    "Partly cloudy - غائم جزئياً": 600,
    "Mostly cloudy - غائم كتير": 300,
}


# =========================================================
# دوال الحساب - اللوح الشمسي
# =========================================================

def correct_to_stc(v_oc, i_sc, temp_meas, irradiance_meas,
                    alpha, beta, temp_ref=25, irradiance_ref=1000):
    delta_t = temp_meas - temp_ref
    voc_stc = v_oc / (1 + (beta / 100) * delta_t)
    isc_stc = i_sc * (irradiance_ref / irradiance_meas) / (1 + (alpha / 100) * delta_t)
    return voc_stc, isc_stc


def get_solar_probable_causes(voc_ratio, isc_ratio, fill_factor):
    scores = {
        "Shading or dirt on the panel surface - تظليل جزئي أو اتساخ على السطح": 0,
        "Micro-cracks in the cells - تشققات دقيقة في الخلايا": 0,
        "Bypass diode fault / open connection - عطل دايود التمرير أو انقطاع": 0,
        "High series resistance / bad soldering - مقاومة توالي عالية": 0,
        "Normal aging - تدهور طبيعي مرتبط بالعمر": 0,
    }

    if isc_ratio < 0.90 and voc_ratio >= 0.95:
        scores["Shading or dirt on the panel surface - تظليل جزئي أو اتساخ على السطح"] += 3
        scores["Micro-cracks in the cells - تشققات دقيقة في الخلايا"] += 1

    if voc_ratio < 0.85 and isc_ratio >= 0.90:
        scores["Bypass diode fault / open connection - عطل دايود التمرير أو انقطاع"] += 3

    if voc_ratio >= 0.90 and isc_ratio >= 0.90 and fill_factor < 0.65:
        scores["High series resistance / bad soldering - مقاومة توالي عالية"] += 3

    if isc_ratio < 0.90 and fill_factor < 0.70:
        scores["Micro-cracks in the cells - تشققات دقيقة في الخلايا"] += 2

    if 0.85 <= voc_ratio < 0.95 and 0.85 <= isc_ratio < 0.95:
        scores["Normal aging - تدهور طبيعي مرتبط بالعمر"] += 2

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = [item for item in ranked if item[1] > 0]

    if not ranked:
        ranked = [("Unclear cause - يُنصح بفحص بصري شامل", 1)]

    return ranked


# =========================================================
# دوال الحساب - البطارية
# =========================================================

def calculate_soh(r_int, r_new):
    return max(0, 100 - ((r_int - r_new) / r_new) * 50)


def get_battery_probable_causes(r_ratio, cycle_ratio):
    scores = {
        "Sulfation from repeated partial charging - التملح": 0,
        "Normal end of life - نهاية العمر الافتراضي الطبيعي": 0,
        "Weak cell or internal connection issue - خلية ضعيفة": 0,
    }

    if r_ratio > 1.5 and cycle_ratio < 0.8:
        scores["Sulfation from repeated partial charging - التملح"] += 3
        scores["Weak cell or internal connection issue - خلية ضعيفة"] += 1

    if cycle_ratio >= 0.8:
        scores["Normal end of life - نهاية العمر الافتراضي الطبيعي"] += 3

    if r_ratio > 2.0 and cycle_ratio < 0.4:
        scores["Weak cell or internal connection issue - خلية ضعيفة"] += 2

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = [item for item in ranked if item[1] > 0]

    if not ranked:
        ranked = [("Unclear cause - يُنصح بفحص إضافي", 1)]

    return ranked


# =========================================================
# تبويب اللوح الشمسي
# =========================================================

with tab1:
    st.subheader("Step 1 - اختر موديل اللوح")
    panel_choice = st.selectbox("Panel model - موديل اللوح", list(SOLAR_PANELS.keys()))

    if SOLAR_PANELS[panel_choice] is None:
        st.info("أدخل القيم يدوياً من ملصق اللوح (خلف اللوح) أو من الداتاشيت")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            pmax_rated = st.number_input("Rated Pmax (Watt) - القدرة الاسمية", value=100.0)
            voc_rated = st.number_input("Rated Voc (Volt) - من الملصق", value=22.0)
        with col_r2:
            isc_rated = st.number_input("Rated Isc (Ampere) - من الملصق", value=6.0)
            has_coeffs = st.checkbox("عندي معاملات الحرارة من الداتاشيت الكامل")
        if has_coeffs:
            alpha = st.number_input("Alpha - معامل حرارة التيار (%/C)", value=0.05, format="%.3f")
            beta = st.number_input("Beta - معامل حرارة الجهد (%/C)", value=-0.29, format="%.3f")
        else:
            alpha, beta = 0.05, -0.29
            st.caption("تم استخدام قيم افتراضية شائعة للألواح السيليكونية (Alpha=0.05, Beta=-0.29)")
    else:
        ref = SOLAR_PANELS[panel_choice]
        pmax_rated = ref["pmax_rated"]
        voc_rated = ref["voc_rated"]
        isc_rated = ref["isc_rated"]
        alpha = ref["alpha"]
        beta = ref["beta"]
        st.caption(f"Rated values - القيم المرجعية: Pmax={pmax_rated}W, Voc={voc_rated}V, Isc={isc_rated}A")

    st.markdown("---")
    st.subheader("Step 2 - أدخل القراءات اللي قسّتها بنفسك")

    col1, col2 = st.columns(2)
    with col1:
        v_oc = st.number_input("Measured Voc (Volt) - فولتية الدارة المفتوحة", value=21.0)
        i_sc = st.number_input("Measured Isc (Ampere) - تيار القصر", value=5.5)
        v_mp = st.number_input("Measured Vmp (Volt) - فولتية أقصى قدرة", value=17.5)
        i_mp = st.number_input("Measured Imp (Ampere) - تيار أقصى قدرة", value=5.1)
    with col2:
        weather = st.selectbox("Weather condition while measuring - حالة الطقس أثناء القياس",
                                list(WEATHER_TO_IRRADIANCE.keys()))
        irradiance_meas = WEATHER_TO_IRRADIANCE[weather]
        temp_meas = st.number_input("Air temperature (C) - درجة حرارة الجو", value=30.0)
        st.caption("درجة حرارة الجو تقدر تاخذها من أي تطبيق طقس بالموبايل")

    if st.button("Diagnose Panel - تشخيص حالة اللوح", type="primary"):
        voc_stc, isc_stc = correct_to_stc(v_oc, i_sc, temp_meas, irradiance_meas, alpha, beta)

        p_measured = v_mp * i_mp
        eff = (p_measured / pmax_rated) * 100 if pmax_rated > 0 else 0
        fill_factor = p_measured / (voc_stc * isc_stc) if (voc_stc * isc_stc) > 0 else 0

        voc_ratio = voc_stc / voc_rated if voc_rated > 0 else 0
        isc_ratio = isc_stc / isc_rated if isc_rated > 0 else 0

        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Measured power - القدرة الفعلية", f"{p_measured:.2f} W")
        col_b.metric("Efficiency - الكفاءة", f"{eff:.1f}%")
        col_c.metric("Fill Factor - معامل الملء", f"{fill_factor:.3f}")

        if eff >= 80:
            st.success("Excellent condition - حالة ممتازة / جيدة جداً")
        elif 65 <= eff < 80:
            st.warning("Early warning - تحذير مبكر: بداية تراجع بسيط بالأداء")
        else:
            st.error("Significant efficiency drop - انخفاض واضح في الكفاءة")
            causes = get_solar_probable_causes(voc_ratio, isc_ratio, fill_factor)
            st.write("**Most likely causes - الاحتمالات المرجّحة:**")
            for i, (cause, score) in enumerate(causes, start=1):
                st.write(f"{i}. {cause}")


# =========================================================
# تبويب البطارية
# =========================================================

with tab2:
    st.subheader("Step 1 - اختر نوع البطارية")
    battery_choice = st.selectbox("Battery type - نوع البطارية", list(BATTERIES.keys()))

    if BATTERIES[battery_choice] is None:
        st.info("أدخل القيم يدوياً من ملصق البطارية أو الداتاشيت")
        r_new = st.number_input("Internal resistance when new (mOhm) - المقاومة وهي جديدة", value=10.0)
        cycles_rated = st.number_input("Rated cycle life - عدد الدورات المتوقع", min_value=1, value=500)
    else:
        ref = BATTERIES[battery_choice]
        r_new = ref["r_new"]
        cycles_rated = ref["cycles_rated"]
        st.caption(f"Rated values - القيم المرجعية: R_new={r_new} mOhm, Cycles={cycles_rated}")

    st.markdown("---")
    st.subheader("Step 2 - أدخل القراءات الحالية")

    col1_b, col2_b = st.columns(2)
    with col1_b:
        r_int = st.number_input("Measured internal resistance (mOhm) - المقاومة الحالية", value=25.0)
    with col2_b:
        cycles = st.number_input("Number of charge cycles so far - عدد دورات الشحن حتى الآن",
                                   min_value=0, value=300)

    if st.button("Calculate SoH - حساب صحة البطارية", type="primary"):
        soh = calculate_soh(r_int, r_new)
        r_ratio = r_int / r_new if r_new > 0 else 1
        cycle_ratio = cycles / cycles_rated if cycles_rated > 0 else 0

        st.divider()
        st.metric("State of Health (SoH) - حالة الصحة", f"{soh:.1f}%")
        st.caption(f"Cycles used - عدد الدورات المستخدمة: {cycles} of {cycles_rated}")

        if soh >= 80:
            st.success("Excellent condition - بحالة ممتازة")
        elif 65 <= soh < 80:
            st.warning("Early warning - تحذير مبكر: بداية تراجع بالكفاءة")
        else:
            st.error("Significant health drop - انخفاض واضح في حالة الصحة")
            causes = get_battery_probable_causes(r_ratio, cycle_ratio)
            st.write("**Most likely causes - الاحتمالات المرجّحة:**")
            for i, (cause, score) in enumerate(causes, start=1):
                st.write(f"{i}. {cause}")
