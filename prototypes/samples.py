"""One-click demo inputs.

Typing on stage is a risk: typos, slow pace, dead air. Every prototype gets a
button that fills realistic input instantly. All content here is fictional.
"""

GUIDE_QUESTIONS = [
    "What is the treatment regimen for drug-sensitive TB?",
    "When is the measles-rubella second dose given?",
    "What blood pressure reading needs referral to a higher facility?",
    "Who counts as a presumptive TB case?",
    # The refusal demo. Nothing in the loaded guidelines covers this.
    "What is the dose of adrenaline in cardiac arrest?",
]

WARD_NOTES = """\
D1: 54/M adm c/o fever x4d, cough w sputum, breathlessness x2d. K/c/o DM2 on OHA, irregular.
O/E febrile 101F, RR 28, SpO2 91% RA, creps R infrascapular. CXR - RLZ consolidation.
TLC raised. RBS 268. Started IV abx + O2 nasal prongs 3L, neb, PCM SOS. Insulin sliding scale.

D2: fever persists 100.4F. SpO2 94% on 2L. cont same. HbA1c sent - 8.2.

D3: afebrile. O2 weaned to RA, SpO2 95%. appetite improving. cont abx.

D4: afebrile, SpO2 97% RA, chest clearer. amb independently. TLC normalising.
Shift to oral abx. Start metformin. Plan discharge tomorrow.

D5: stable. for d/c. adv OPD review 1wk w rpt CXR, DM clinic 2wks. home glucose monitoring.\
"""

# Deliberately contains identifiers so the de-identification check fires on stage.
WARD_NOTES_WITH_IDENTIFIERS = WARD_NOTES + """

Contact: Ramesh Kumar, mob 9845012345, ramesh.k@example.com
UHID: 884213   DOB: 14/07/1971\
"""

SCREEN_CRITERIA = """\
INCLUDE if ALL of:
  - Primary study (RCT, quasi-experimental, or cohort)
  - Adult participants aged 30 years and above
  - Conducted in a primary care or community setting
  - Reports blood pressure as an outcome

EXCLUDE if ANY of:
  - Review, editorial, commentary, or protocol only
  - Paediatric or adolescent population only
  - Hospital inpatient setting only\
"""

SCREEN_ABSTRACTS = """\
A1: A cluster-randomised trial across 24 primary health centres in Karnataka evaluated a
nurse-led hypertension management package among 3,140 adults aged 30 and above. Mean systolic
blood pressure at 12 months was 6.4 mmHg lower in intervention clusters.

A2: This randomised trial assessed a school-based salt-reduction education programme among
1,200 children aged 9 to 14 years in urban Chennai, measuring 24-hour urinary sodium and
blood pressure at 6 months.

A3: We describe blood pressure control among 480 adults attending a community clinic over
two years. Mean systolic pressure fell from 152 to 138 mmHg. Participants were recruited
consecutively from the outpatient register.

A4: Hypertension in low- and middle-income countries: a narrative review of task-shifting
models, summarising evidence from 42 published studies across 18 countries.

A5: In a randomised controlled trial of 620 adults aged 35 to 70 in rural Maharashtra,
participants received either standard care or a community health worker follow-up model.
Systolic blood pressure at 6 months was the primary outcome.

A6: A protocol for a stepped-wedge trial of digital blood pressure monitoring in
primary care. Recruitment has not yet commenced.\
"""

TRIAGE_COMPLAINTS = [
    "45 year old man, chest pain since 2 hours, sweating",
    "28 year old woman, fever and headache since 3 days",
    "6 month old infant, not feeding well since yesterday, fever",
    "60 year old, sudden weakness of one side of body, slurred speech",
]

# 5. PharmGuard Samples
PHARM_MEDICATIONS = [
    "Warfarin 5mg daily",
    "Ibuprofen 400mg TID",
    "Metformin 1000mg BID",
    "Amoxicillin 500mg TID",
    "Amlodipine 5mg daily",
]
PHARM_ALLERGIES = ["Penicillin (Anaphylaxis)"]
PHARM_EGFR = 28.0
PHARM_DIAGNOSIS = "Type 2 Diabetes Mellitus with Stage 4 Chronic Kidney Disease and Atrial Fibrillation"

# 6. LabAlert Samples
LAB_PANEL_CRITICAL = """\
Hemoglobin: 11.2 g/dL
WBC: 12,400 /µL
Platelets: 185,000 /µL
Potassium: 6.4 mEq/L
Sodium: 136 mEq/L
Serum Creatinine: 2.8 mg/dL
Troponin I: 0.12 ng/mL
Blood Glucose: 210 mg/dL\
"""

# 7. TrialMatch Samples
TRIAL_PATIENT_PROFILE = """\
Patient: 58-year-old male
Diagnosis: Type 2 Diabetes Mellitus (12 years duration)
Recent HbA1c: 8.6%
Renal Function: eGFR 24 mL/min/1.73m2, Serum Creatinine 2.4 mg/dL
Prior Medications: Metformin (discontinued), Glimepiride 2mg, Insulatard 20U at bedtime
Cardiac History: No history of myocardial infarction, stroke, or heart failure.
Ophthalmic Exam: Mild non-proliferative diabetic retinopathy.\
"""

TRIAL_CRITERIA = """\
INCLUSION CRITERIA:
1. Adults aged 18 to 75 years at time of screening.
2. Diagnosed with Type 2 Diabetes Mellitus with baseline HbA1c between 7.5% and 10.5%.
3. Stable regimen of glucose-lowering therapy for at least 8 weeks prior to screening.

EXCLUSION CRITERIA:
1. eGFR < 30 mL/min/1.73m2 or active end-stage renal disease.
2. History of acute coronary syndrome, stroke, or TIA within the previous 6 months.
3. Severe proliferative diabetic retinopathy or macular edema requiring urgent laser therapy.\
"""

# 8. DiffCheck Samples
DIFF_SYMPTOMS = "42-year-old female presents with sudden onset sharp right-sided chest pain worsening on deep inspiration (pleuritic). HR 104 bpm, BP 122/78 mmHg, SpO2 97% on room air. Taking oral contraceptive pills."
DIFF_WORKING_DIAGNOSIS = "Musculoskeletal chest wall pain / muscle strain"

# 9. RadVision (Multimodal Vision) Samples
# Valid 1x1 transparent PNG base64 string for zero-network testing & preview
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

MULTIMODAL_SAMPLES = [
    {
        "label": "🫁 Chest X-Ray: Fever & Consolidation",
        "modality": "Chest X-Ray",
        "file_name": "cxr_right_lower_lobe_consolidation.jpg",
        "context": "54-year-old male presenting with 4 days of high fever, productive cough with purulent sputum, and right-sided pleuritic chest pain. SpO2 92% on room air.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🩺 Dermatology: Asymmetric Skin Lesion",
        "modality": "Dermatology",
        "file_name": "skin_lesion_irregular_melanoma.jpg",
        "context": "48-year-old female noticed a changing pigmented lesion on her upper back. Asymmetric borders, color variation (dark brown/black), diameter 8mm.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "⚡ ECG: Acute Chest Pain (ST Elevation)",
        "modality": "ECG",
        "file_name": "ecg_acute_st_elevation_stemi.jpg",
        "context": "62-year-old diabetic male with sudden crushing retrosternal chest pain radiating to left jaw and arm for 1 hour. Diaphoretic and pale.",
        "image_b64": TINY_PNG_B64,
    },
]

# 10. PathoScan Samples
PATHOLOGY_SAMPLES = [
    {
        "label": "🔬 Breast Biopsy: Invasive Ductal Carcinoma",
        "tissue_type": "Breast Tissue Biopsy",
        "file_name": "breast_biopsy_he_stain.jpg",
        "context": "Core needle biopsy of 2.5cm firm breast mass in a 52-year-old female. H&E stain, high power field. High mitotic count and lymphovascular invasion noted.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🧫 Lymph Node: Granulomatous Lymphadenitis",
        "tissue_type": "Lymph Node Biopsy",
        "file_name": "lymph_node_granuloma_tb.jpg",
        "context": "Excisional cervical lymph node biopsy in a 34-year-old male with chronic fever and night sweats. Caseating necrotizing granulomas with Langhans giant cells.",
        "image_b64": TINY_PNG_B64,
    },
]

# 11. WoundTrack Samples
WOUND_SAMPLES = [
    {
        "label": "🦶 Diabetic Foot Ulcer: Plantar Surface (Wagner Grade 3)",
        "location": "Plantar Surface 1st MTP Joint",
        "file_name": "diabetic_foot_ulcer_exposed_bone.jpg",
        "context": "64-year-old diabetic male with deep chronic ulcer on plantar aspect of right foot. Probe-to-bone positive, purulent discharge, spreading erythema 3cm.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🏥 Post-Op Surgical Wound: Sacral Pressure Injury",
        "location": "Sacral Area",
        "file_name": "sacral_pressure_ulcer_stage3.jpg",
        "context": "78-year-old bedbound female post-hip fracture repair. Sacral Stage 3 pressure injury with 40% slough and 60% red granulation tissue. No osteomyelitis.",
        "image_b64": TINY_PNG_B64,
    },
]

# 12. ChartVision Samples
CHART_SAMPLES = [
    {
        "label": "✍️ Prescription: Ciprofloxacin & Insulin Order",
        "document_type": "Handwritten Prescription",
        "file_name": "handwritten_prescription_insulin.jpg",
        "context": "Rx: Ciprofloxacin 500mg BID x7d. Regular Insulin 10U SC AC TID. Metformin 1000mg BID. Dr. R. Sharma, MD.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "📋 ICU Flowsheet: Inotrope & Heparin Infusion",
        "document_type": "ICU Flowsheet Note",
        "file_name": "icu_flowsheet_heparin_dopamine.jpg",
        "context": "ICU Day 2: Noradrenaline 0.1 mcg/kg/min IV. Heparin IV infusion 1000 units/hr. Check APTT q6h.",
        "image_b64": TINY_PNG_B64,
    },
]

# 13. FundusVision Samples
FUNDUS_SAMPLES = [
    {
        "label": "👁️ Retinal Fundus: Severe NPDR (Diabetic Retinopathy)",
        "eye_side": "Right Eye (OD)",
        "file_name": "fundus_diabetic_retinopathy_npdr.jpg",
        "context": "56-year-old male with 14-year history of Type 2 DM (HbA1c 9.2%). Multiple hard exudates, microaneurysms, and macular edema.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🚨 Optic Disc: Bilateral Papilledema (Elevated ICP)",
        "eye_side": "Bilateral Fundus (OU)",
        "file_name": "fundus_papilledema_elevated_icp.jpg",
        "context": "28-year-old female presenting with severe morning headaches, pulsatile tinnitus, and transient visual obscurations. Optic disc margin blurring and hyperemia.",
        "image_b64": TINY_PNG_B64,
    },
]

# 14. OtoscopeAI Samples
OTOSCOPE_SAMPLES = [
    {
        "label": "👂 Otoscopy: Acute Otitis Media (Bulging TM)",
        "ear_side": "Right Ear (AD)",
        "file_name": "otoscopy_acute_otitis_media.jpg",
        "context": "3-year-old child with 2 days of high fever (102°F), severe ear otalgia, and irritability. Bulging erythematous tympanic membrane with loss of cone of light.",
        "image_b64": TINY_PNG_B64,
    },
    {
        "label": "🚨 Otoscopy: Acute Mastoiditis (Retroauricular Swelling)",
        "ear_side": "Left Ear (AS)",
        "file_name": "otoscopy_acute_mastoiditis.jpg",
        "context": "6-year-old child with persistent untreated otitis media presenting with post-auricular tenderness, erythema, and outward displacement of the pinna.",
        "image_b64": TINY_PNG_B64,
    },
]



