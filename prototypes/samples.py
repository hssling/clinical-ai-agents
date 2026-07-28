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
