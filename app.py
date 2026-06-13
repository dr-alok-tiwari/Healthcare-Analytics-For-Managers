import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from textwrap import dedent
from datetime import datetime
import math

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Healthcare Analytics for Managers",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        :root{
            --saffron:#F59E0B;
            --saffron-dark:#B45309;
            --cream:#FFF7ED;
            --ink:#111827;
            --muted:#6B7280;
            --teal:#0F766E;
            --blue:#2563EB;
            --rose:#E11D48;
            --green:#15803D;
            --card:#FFFFFF;
            --border:#F3D6A4;
        }
        .main .block-container{padding-top:1.2rem; padding-bottom:3rem; max-width:1360px;}
        h1,h2,h3{letter-spacing:-0.035em; color:var(--ink);} 
        p, li, label, div{font-size:1.0rem;}
        [data-testid="stSidebar"]{background:linear-gradient(180deg,#FFF7ED 0%,#FFFBEB 55%,#FFFFFF 100%);} 
        [data-testid="stSidebar"] *{font-size:.98rem;}
        .hero{
            background: radial-gradient(circle at 7% 18%, rgba(245,158,11,.28), transparent 30%),
                        radial-gradient(circle at 90% 5%, rgba(15,118,110,.12), transparent 26%),
                        linear-gradient(135deg,#FFF7ED 0%,#FFFFFF 44%,#ECFEFF 100%);
            border:1px solid var(--border);
            border-radius:30px;
            padding:34px 36px;
            box-shadow:0 20px 55px rgba(120,53,15,.09);
            margin-bottom:18px;
        }
        .hero h1{font-size:3.05rem; line-height:1.02; margin-bottom:.28rem;}
        .hero p{font-size:1.12rem; color:#4B5563; max-width:1050px;}
        .pill{display:inline-block; padding:7px 12px; border-radius:999px; background:#FFEDD5; color:#9A3412; border:1px solid #FED7AA; font-weight:750; font-size:.85rem; margin:4px 5px 4px 0;}
        .tag{display:inline-block; padding:4px 9px; border-radius:8px; background:#F8FAFC; border:1px solid #E5E7EB; margin:2px 4px 2px 0; font-size:.84rem; color:#374151;}
        .card{background:var(--card); border:1px solid #F3E8D1; border-radius:22px; padding:20px 22px; box-shadow:0 10px 28px rgba(31,41,55,.05); margin-bottom:14px;}
        .mini-card{background:#FFFFFF; border:1px solid #F4DDB7; border-radius:18px; padding:16px 18px; height:100%; box-shadow:0 8px 22px rgba(31,41,55,.045);}
        .callout{border-left:6px solid var(--saffron); background:#FFF7ED; padding:16px 18px; border-radius:16px; margin:12px 0;}
        .green-callout{border-left:6px solid #0F766E; background:#F0FDFA; padding:16px 18px; border-radius:16px; margin:12px 0;}
        .blue-callout{border-left:6px solid #2563EB; background:#EFF6FF; padding:16px 18px; border-radius:16px; margin:12px 0;}
        .rose-callout{border-left:6px solid #E11D48; background:#FFF1F2; padding:16px 18px; border-radius:16px; margin:12px 0;}
        .metric-card{background:#FFFFFF; border:1px solid #F3E8D1; padding:16px; border-radius:18px; box-shadow:0 6px 16px rgba(31,41,55,.05);}
        .small-muted{color:#6B7280; font-size:.91rem;}
        .diagram-box{background:#FFFFFF; border:1px dashed #F59E0B; padding:13px; border-radius:15px; text-align:center; font-weight:750; color:#7C2D12; min-height:58px;}
        .arrow{text-align:center; color:#B45309; font-size:1.55rem; font-weight:900; padding-top:19px;}
        .footer-note{font-size:.9rem; color:#6B7280; border-top:1px solid #F3E8D1; margin-top:24px; padding-top:14px;}
        .stButton>button{border-radius:13px; border:1px solid #FCD34D; background:#FFFBEB; color:#78350F; font-weight:750;}
        .stButton>button:hover{border-color:#F59E0B; background:#FEF3C7; color:#78350F;}
        .codebox{background:#111827; color:#E5E7EB; padding:14px; border-radius:14px; font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; overflow:auto;}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ============================================================
# HELPER UI
# ============================================================
def hero(title, subtitle, pills=None):
    pills = pills or []
    pill_html = "".join([f"<span class='pill'>{p}</span>" for p in pills])
    st.markdown(f"""
    <div class='hero'>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <div>{pill_html}</div>
    </div>
    """, unsafe_allow_html=True)

def callout(text, color="orange"):
    cls = {"orange":"callout", "green":"green-callout", "blue":"blue-callout", "rose":"rose-callout"}.get(color, "callout")
    st.markdown(f"<div class='{cls}'>{text}</div>", unsafe_allow_html=True)

def card(title, body, icon="📌"):
    st.markdown(f"""
    <div class='card'>
      <h3>{icon} {title}</h3>
      <p>{body}</p>
    </div>
    """, unsafe_allow_html=True)

def flow_diagram(items):
    cols = st.columns(len(items) * 2 - 1)
    for i, item in enumerate(items):
        cols[i*2].markdown(f"<div class='diagram-box'>{item}</div>", unsafe_allow_html=True)
        if i < len(items) - 1:
            cols[i*2+1].markdown("<div class='arrow'>→</div>", unsafe_allow_html=True)

def download_df(df, label, filename):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, csv, filename, "text/csv")

# ============================================================
# MASTER DATA GENERATORS
# ============================================================
DECISION_LEVELS = ["Strategic", "Tactical", "Operational", "Clinical-operational", "Financial", "Ethical-governance"]
DECISION_DOMAINS = [
    "Patient Flow", "Bed & Capacity", "Quality & Safety", "Finance & Revenue Cycle", "Insurance & Claims",
    "Pharmacy & Supply Chain", "Workforce & Staffing", "Patient Experience", "Population Health", "Digital Health & AI"
]
KPI_BANK = {
    "Patient Flow": ["Average waiting time", "queue length", "no-show rate", "consultation turnaround time"],
    "Bed & Capacity": ["bed occupancy", "average length of stay", "discharge-before-noon rate", "ICU utilization"],
    "Quality & Safety": ["infection rate", "readmission rate", "adverse events", "mortality review flags"],
    "Finance & Revenue Cycle": ["net revenue", "collection rate", "cost per case", "AR days"],
    "Insurance & Claims": ["claim denial rate", "preauthorization delay", "claim turnaround time", "approval rate"],
    "Pharmacy & Supply Chain": ["stockout risk", "inventory days", "expiry value", "reorder point"],
    "Workforce & Staffing": ["staff utilization", "overtime hours", "patient-to-nurse ratio", "schedule adherence"],
    "Patient Experience": ["NPS", "complaint rate", "satisfaction score", "service recovery time"],
    "Population Health": ["screening coverage", "risk stratification", "follow-up adherence", "preventive visit rate"],
    "Digital Health & AI": ["model drift", "AI override rate", "teleconsult adoption", "alert precision"]
}

DECISION_URGENCIES = ["low", "moderate", "high", "critical"]


def generate_decision_situations(min_per_combination=5):
    """Generate a complete decision-room bank.

    Design rule: every Level x Domain x Urgency combination must have at
    least `min_per_combination` situations. With 6 levels, 10 domains,
    4 urgency values, and 5 variants, the bank contains 1,200 situations.
    This prevents empty screens when a learner applies multiple filters.
    """
    rows = []
    situation_templates = [
        "A dashboard warning has appeared and the leadership team needs a clear decision before the next review.",
        "A department head reports repeated friction between patient demand, available capacity, and staff workload.",
        "Patient complaints and operational KPIs are telling different stories, so the manager must reconcile evidence before acting.",
        "A monthly review shows an unusual pattern that may be temporary noise or a real system-level risk.",
        "A new policy or process change is being considered, but the manager must weigh cost, safety, experience, and feasibility."
    ]
    option_templates = [
        "A) Wait one more cycle, B) Run a focused diagnostic, C) Launch a rapid intervention with daily review",
        "A) Add capacity immediately, B) Segment the issue first, C) Escalate to executive committee",
        "A) Use one hospital-wide average, B) Compare by unit/shift/patient group, C) Ignore outliers as exceptions",
        "A) Reduce service scope, B) Redesign the process, C) Create a pilot intervention with control metrics",
        "A) Prioritise financial savings, B) Prioritise patient safety, C) Balance both using a transparent decision scorecard"
    ]
    action_templates = [
        "Run a focused diagnostic for 7 days, identify the highest-impact segment, and assign a visible KPI owner before changing the full process.",
        "Do not respond only to the average. Break the metric by department, shift, patient type, payer type, and severity before deciding.",
        "Create a short pilot with a baseline, target, owner, review frequency, and stop/go rule so the decision stays evidence-based.",
        "Use a Pareto view to identify the top two drivers, solve those first, and review the effect weekly with frontline managers.",
        "Document the ethical, financial, clinical, and operational trade-offs before implementation so the recommendation is defensible."
    ]
    tradeoff_templates = [
        "Speed versus evidence quality; short-term relief versus long-term redesign.",
        "Patient experience versus staff workload; local optimisation versus system-wide flow.",
        "Financial discipline versus clinical risk; access improvement versus resource limits.",
        "Standardisation versus departmental flexibility; automation efficiency versus human oversight.",
        "Equity, safety, privacy, and cost must be balanced instead of optimising one metric blindly."
    ]
    first_7_day_templates = [
        "Day 1 define the KPI, Day 2 validate data, Day 3 segment the trend, Day 4 identify bottlenecks, Day 5 meet owners, Day 6 launch pilot, Day 7 review dashboard.",
        "Freeze the definition, pull six weeks of data, compare segments, shortlist root causes, create an action owner list, and schedule two review huddles.",
        "Map the patient journey, locate delay points, compare weekday/weekend patterns, quantify impact, and publish one-page decision note.",
        "Create baseline, target, risk flag, stakeholder owner, escalation rule, and a simple before-after tracking view.",
        "Speak to frontline users, verify data against source systems, estimate cost of inaction, and prepare a phased recommendation."
    ]
    stakeholders = ["COO", "CMO", "CFO", "Nursing Head", "Quality Head", "Operations Manager", "Hospital CEO", "Insurance Manager", "Pharmacy Head", "Digital Health Lead"]
    managerial_skills = ["prioritization", "root-cause thinking", "data storytelling", "ethical judgement", "resource allocation", "stakeholder alignment", "dashboard interpretation", "risk communication"]

    situation_id = 1
    for level_idx, level in enumerate(DECISION_LEVELS):
        for domain_idx, domain in enumerate(DECISION_DOMAINS):
            kpis = KPI_BANK[domain]
            for urgency_idx, urgency in enumerate(DECISION_URGENCIES):
                for variant in range(1, min_per_combination + 1):
                    kpi = kpis[(variant - 1) % len(kpis)]
                    stakeholder = stakeholders[(level_idx + domain_idx + urgency_idx + variant - 1) % len(stakeholders)]
                    template_idx = (variant - 1) % len(situation_templates)
                    risk_word = {"low":"watchlist", "moderate":"emerging risk", "high":"active management issue", "critical":"executive escalation"}[urgency]
                    rows.append({
                        "ID": situation_id,
                        "Combination Key": f"{level} | {domain} | {urgency}",
                        "Variant": variant,
                        "Level": level,
                        "Domain": domain,
                        "Urgency": urgency,
                        "Stakeholder": stakeholder,
                        "Situation": f"{domain} {level.lower()} decision {variant}: {kpi.title()} needs attention",
                        "Business Story": f"{situation_templates[template_idx]} The {stakeholder} sees {kpi} moving unfavourably in the {domain.lower()} area. Because urgency is {urgency}, the issue is treated as a {risk_word}. Managers must decide whether to monitor, diagnose, intervene, or escalate.",
                        "Decision Question": f"For this {level.lower()} decision, what action should management take on {kpi} in {domain.lower()} without overreacting to incomplete data?",
                        "Data to Check": ", ".join(kpis),
                        "Options": option_templates[template_idx],
                        "Recommended Action": action_templates[template_idx],
                        "Trade-off": tradeoff_templates[template_idx],
                        "First 7 Days": first_7_day_templates[template_idx],
                        "Follow-up KPI": f"Weekly movement in {kpi}, segmented by department, shift, patient group, and payer type.",
                        "Managerial Skill": managerial_skills[(level_idx + domain_idx + urgency_idx + variant - 1) % len(managerial_skills)],
                        "Discussion Prompt": f"Ask students: What would go wrong if the manager used only the overall average of {kpi}? What extra segmentation would make the decision safer?"
                    })
                    situation_id += 1
    return pd.DataFrame(rows)

CASE_CATEGORIES = [
    "Patient Flow & Waiting Time", "Bed Occupancy & Capacity Planning", "Readmission & Quality Improvement",
    "Revenue Cycle & Billing", "Insurance Claims & Denials", "Pharmacy & Inventory",
    "Staffing & Workforce", "Patient Experience & NPS", "Population Health & Outreach", "AI Governance & Ethics"
]

def generate_business_cases():
    cases = []
    for cat_idx, category in enumerate(CASE_CATEGORIES):
        for j in range(1, 21):
            case_id = cat_idx * 20 + j
            dept = ["Emergency", "OPD", "ICU", "Surgery", "Radiology", "Pharmacy", "Billing", "Oncology", "Cardiology", "Pediatrics"][(case_id-1) % 10]
            metric = ["waiting time", "occupancy", "readmission", "collection rate", "claim denial", "stockout", "staff overtime", "NPS", "screening coverage", "AI override rate"][cat_idx]
            cases.append({
                "Case ID": case_id,
                "Category": category,
                "Difficulty": ["Beginner", "Intermediate", "Advanced"][(j-1) % 3],
                "Department": dept,
                "Title": f"Case {case_id}: {category} in {dept}",
                "Business Story": f"The {dept} unit is facing pressure from patients, clinicians, and administrators. The visible symptom is a change in {metric}. The manager must decide whether the issue is a demand problem, process problem, capacity problem, data-quality problem, or governance problem.",
                "Dataset Design": f"Create a table with columns: date, department, patient_type, volume, staff_available, {metric.replace(' ', '_')}, cost, satisfaction_score, outcome_flag.",
                "Analytics Question": f"Which segment, time period, or operational driver explains the change in {metric}, and what should the manager do next?",
                "Step 1 - Frame": "Convert the complaint into a measurable KPI. Decide numerator, denominator, time period, and owner.",
                "Step 2 - Diagnose": "Compare by department, weekday, patient type, severity, payer type, and shift. Do not rely on one average only.",
                "Step 3 - Analyse": "Use descriptive statistics, trend line, segment comparison, Pareto ranking, and exception list.",
                "Step 4 - Interpret": f"If a small segment contributes most of the {metric} problem, fix that segment first. If every segment is worsening, redesign the full process.",
                "Step 5 - Action": "Pilot one intervention for 2–4 weeks, track before/after KPI, and record unintended consequences.",
                "Python Starter": "df.groupby(['department','patient_type']).agg({'volume':'sum','satisfaction_score':'mean'}).sort_values('volume', ascending=False)",
                "Managerial Recommendation": f"Create a weekly dashboard for {metric}, assign one accountable owner, and combine data review with staff feedback before scaling the solution.",
                "Risk / Pitfall": "Avoid punishing teams based only on raw numbers. Adjust for case mix, severity, seasonality, and data completeness.",
                "Expected Learning": "Managers learn to convert messy healthcare situations into measurable decisions without ignoring empathy, ethics, and clinical context."
            })
    return pd.DataFrame(cases)

DATASET_NAMES = [
    "OPD Waiting Time", "Emergency Triage", "Bed Census", "Surgery OT Utilization", "Readmission Tracker",
    "Length of Stay", "Mortality Review", "Patient Experience Survey", "Telemedicine Usage", "Pharmacy Stock",
    "Drug Stockout", "Lab Turnaround Time", "Radiology Turnaround Time", "Claims Denials", "AR Aging",
    "Billing Errors", "Insurance Preauthorization", "ICU Occupancy", "Infection Control", "Sepsis Bundle Compliance",
    "Diabetes Chronic Care", "Hypertension Follow-up", "Maternal Health", "Vaccination Outreach", "HR Attendance",
    "Nurse Rostering", "Doctor Utilization", "Equipment Downtime", "Ambulance Response", "Home Health Visits",
    "Appointment No-shows", "Referral Network", "Cost per Case", "Procurement Prices", "Clinical Pathway Compliance",
    "Employee Wellness", "Mental Health Outreach", "Cancer Screening", "Dialysis Operations", "Blood Bank Inventory",
    "Emergency Supplies", "Digital App Usage", "Wearable Alerts", "Remote Monitoring", "Complaint Tickets",
    "Nutrition Services", "Biomedical Waste", "Energy Usage", "Training Compliance", "Medical Records Quality"
]

DATASET_DOMAINS = [
    "Operations", "Operations", "Capacity", "Operations", "Quality", "Quality", "Quality", "Experience", "Digital Health", "Supply Chain",
    "Supply Chain", "Diagnostics", "Diagnostics", "Claims", "Finance", "Finance", "Claims", "Capacity", "Quality", "Quality",
    "Population Health", "Population Health", "Population Health", "Population Health", "Workforce", "Workforce", "Workforce", "Assets", "Operations", "Home Care",
    "Operations", "Strategy", "Finance", "Supply Chain", "Quality", "Workforce", "Population Health", "Population Health", "Operations", "Supply Chain",
    "Supply Chain", "Digital Health", "Digital Health", "Digital Health", "Experience", "Support Services", "Sustainability", "Sustainability", "Workforce", "Data Governance"
]

def dataset_catalog():
    rows = []
    for i, name in enumerate(DATASET_NAMES, start=1):
        domain = DATASET_DOMAINS[i-1]
        rows.append({
            "Dataset ID": i,
            "Dataset": name,
            "Domain": domain,
            "Rows available": "Custom generated",
            "Manager Question": f"What decision should a manager make using the {name.lower()} data?",
            "Suggested Charts": "Bar, line, histogram, box plot, scatter, heatmap, Pareto",
            "Suggested Stats": "Mean, median, SD, IQR, percentiles, correlation, outliers, group comparison"
        })
    return pd.DataFrame(rows)

def make_sandbox_dataset(name, rows=250, seed=42, missing_pct=0.0, outlier_pct=0.0):
    rng = np.random.default_rng(seed + len(name))
    departments = np.array(["OPD", "Emergency", "ICU", "Surgery", "Radiology", "Pharmacy", "Billing", "Cardiology"])
    months = np.array(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    patient_types = np.array(["New", "Follow-up", "Emergency", "Chronic", "Elective"])
    payer_types = np.array(["Cash", "Private Insurance", "Government Scheme", "Corporate"])
    df = pd.DataFrame({
        "Month": rng.choice(months, rows),
        "Department": rng.choice(departments, rows),
        "Patient_Type": rng.choice(patient_types, rows),
        "Payer_Type": rng.choice(payer_types, rows),
        "Age": np.clip(rng.normal(48, 17, rows).round(), 1, 95).astype(int),
        "Volume": rng.poisson(35, rows) + 1,
        "Wait_Min": np.clip(rng.normal(45, 18, rows), 5, 180).round(1),
        "LOS_Days": np.clip(rng.gamma(2.2, 1.4, rows), 0.2, 18).round(1),
        "Cost": np.clip(rng.normal(18000, 6500, rows), 1000, 80000).round(0),
        "Revenue": np.clip(rng.normal(24000, 8500, rows), 2000, 120000).round(0),
        "Satisfaction": np.clip(rng.normal(78, 12, rows), 10, 100).round(1),
        "Risk_Score": np.clip(rng.beta(2, 5, rows)*100, 0, 100).round(1),
        "Staff_Count": rng.integers(3, 25, rows),
        "Inventory_Units": rng.integers(20, 500, rows),
        "Claims_Denied": rng.binomial(1, 0.13, rows),
        "Readmitted": rng.binomial(1, 0.11, rows),
        "Outcome": rng.choice(["Improved", "Stable", "Escalated", "Delayed"], rows, p=[.45,.30,.15,.10])
    })
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Dataset"] = name
    # dataset-specific nudges
    if "Readmission" in name or "Chronic" in name:
        df["Readmitted"] = rng.binomial(1, np.clip(df["Risk_Score"] / 250 + .05, .03, .42))
    if "Claims" in name or "Insurance" in name:
        df["Claims_Denied"] = rng.binomial(1, np.clip(df["Risk_Score"] / 300 + .08, .04, .45))
    if missing_pct > 0:
        numeric_cols = ["Wait_Min", "LOS_Days", "Cost", "Revenue", "Satisfaction", "Risk_Score"]
        for col in numeric_cols:
            idx = rng.choice(df.index, int(rows * missing_pct / 100), replace=False)
            df.loc[idx, col] = np.nan
    if outlier_pct > 0:
        idx = rng.choice(df.index, max(1, int(rows * outlier_pct / 100)), replace=False)
        df.loc[idx, "Wait_Min"] = df.loc[idx, "Wait_Min"].fillna(45) * rng.uniform(2.5, 4.5, len(idx))
        df.loc[idx, "Cost"] = df.loc[idx, "Cost"].fillna(18000) * rng.uniform(2.0, 4.0, len(idx))
    return df

# ============================================================
# QUESTION BANKS
# ============================================================
MCQ_TOPICS = [
    "Healthcare KPI", "Patient Flow", "Quality & Safety", "Finance", "Claims", "Pharmacy",
    "Workforce", "Patient Experience", "Population Health", "AI & Ethics", "Visualization", "Statistics", "Data Governance"
]
QUESTION_TYPES = ["Concept", "Scenario", "Calculation", "Interpretation", "Ethics", "Chart Choice", "Data Quality", "Managerial Action"]
DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

def generate_mcqs(n=500):
    questions = []
    for i in range(1, n+1):
        topic = MCQ_TOPICS[(i-1) % len(MCQ_TOPICS)]
        qtype = QUESTION_TYPES[(i-1) % len(QUESTION_TYPES)]
        diff = DIFFICULTIES[(i-1) % len(DIFFICULTIES)]
        metric = ["waiting time", "bed occupancy", "readmission rate", "claim denial rate", "stockout risk", "NPS", "cost per case", "screening coverage"][(i-1) % 8]
        question = f"Q{i}. In a {topic.lower()} dashboard, a manager sees that {metric} is worsening for two consecutive weeks. What is the best first analytics action?"
        options = {
            "A": "Immediately blame the frontline team and close the review.",
            "B": "Check trend, segment, denominator, data quality, and operational context before deciding.",
            "C": "Ignore it because healthcare data is always noisy.",
            "D": "Replace the dashboard with a more colourful chart."
        }
        explanation = f"The correct approach is to understand whether {metric} changed due to real process deterioration, patient mix, missing data, seasonality, or measurement error. Managers should diagnose before acting."
        example = f"Example: If {metric} worsens only in Emergency during night shifts, the solution may be staffing or triage redesign, not a hospital-wide policy change."
        questions.append({
            "ID": i, "Topic": topic, "Type": qtype, "Difficulty": diff, "Question": question,
            "A": options["A"], "B": options["B"], "C": options["C"], "D": options["D"],
            "Answer": "B", "Explanation": explanation, "Example": example
        })
    return pd.DataFrame(questions)

INTERVIEW_CATEGORIES = [
    "Healthcare Analytics Basics", "Hospital Operations", "Healthcare KPIs", "SQL & Data Handling",
    "Python/Pandas", "Dashboarding & Visualization", "Statistics", "Machine Learning", "AI Governance",
    "Finance & Claims", "Population Health", "Product & Digital Health", "Consulting Cases", "Leadership"
]
TARGET_JOBS = [
    "Healthcare Data Analyst", "Healthcare Business Analyst", "Hospital Operations Analyst", "Quality Improvement Analyst",
    "Revenue Cycle Analyst", "Population Health Analyst", "Healthcare AI/Product Manager", "Healthcare Consultant"
]

def generate_interview_questions(n=500):
    rows = []
    for i in range(1, n+1):
        cat = INTERVIEW_CATEGORIES[(i-1) % len(INTERVIEW_CATEGORIES)]
        job = TARGET_JOBS[(i-1) % len(TARGET_JOBS)]
        diff = DIFFICULTIES[(i-1) % len(DIFFICULTIES)]
        topic_metric = ["readmission", "waiting time", "claim denial", "stockout", "NPS", "LOS", "bed occupancy", "AI model bias"][(i-1) % 8]
        rows.append({
            "ID": i,
            "Category": cat,
            "Target Job": job,
            "Difficulty": diff,
            "Question": f"How would you analyse and explain a sudden change in {topic_metric} to a hospital leadership team?",
            "Answer": f"I would first define the KPI clearly, verify data quality, compare trends before and after the change, segment by department and patient group, identify the strongest driver, and translate the finding into a decision. For {topic_metric}, I would avoid giving only one average because healthcare operations often vary by shift, severity, payer type, and department.",
            "Simple Example": f"If {topic_metric} worsens mainly for one department or payer group, I would focus the intervention there before recommending a hospital-wide change.",
            "Interview-ready Spoken Answer": f"I would frame it as a decision problem, not only a data problem. My answer would include the metric definition, trend, segmentation, root cause, recommendation, risk, and follow-up KPI.",
            "Common Mistake": "Jumping directly to a solution without checking denominator, seasonality, data completeness, or operational context.",
            "Managerial Angle": "The interviewer wants to see whether you can convert analysis into action while respecting clinical and operational realities."
        })
    return pd.DataFrame(rows)

# ============================================================
# ROADMAP GENERATOR
# ============================================================
CAREER_OPTIONS = pd.DataFrame([
    {"Role":"Healthcare Data Analyst", "Core Skills":"Excel, SQL, Python, dashboards, KPI analysis", "Portfolio Project":"Hospital KPI dashboard with patient-flow insights", "Interview Focus":"Data cleaning, dashboard interpretation, stakeholder communication"},
    {"Role":"Healthcare Business Analyst", "Core Skills":"Process mapping, requirements, analytics translation, documentation", "Portfolio Project":"OPD improvement business case", "Interview Focus":"Problem framing, stakeholder management, solution design"},
    {"Role":"Hospital Operations Analyst", "Core Skills":"Patient flow, bed capacity, staffing, process improvement", "Portfolio Project":"Bed occupancy simulator and waiting-time reduction plan", "Interview Focus":"Operational KPIs, bottleneck analysis, trade-offs"},
    {"Role":"Quality Improvement Analyst", "Core Skills":"Readmission, infection, safety, PDSA, root-cause analysis", "Portfolio Project":"Readmission risk dashboard with intervention plan", "Interview Focus":"Quality metrics, ethics, patient safety"},
    {"Role":"Revenue Cycle Analyst", "Core Skills":"Claims, denials, AR days, billing, payer analytics", "Portfolio Project":"Claims denial Pareto and recovery plan", "Interview Focus":"Financial KPIs, claims data, business impact"},
    {"Role":"Population Health Analyst", "Core Skills":"Risk stratification, outreach, screening, preventive analytics", "Portfolio Project":"Diabetes follow-up and screening coverage dashboard", "Interview Focus":"Population segmentation, equity, outcome tracking"},
    {"Role":"Healthcare AI/Product Manager", "Core Skills":"AI use cases, product thinking, model monitoring, governance", "Portfolio Project":"AI triage assistant governance canvas", "Interview Focus":"Responsible AI, risk, adoption, user workflow"},
    {"Role":"Healthcare Consultant", "Core Skills":"Case solving, analytics storytelling, change management", "Portfolio Project":"Hospital transformation case deck", "Interview Focus":"Structured problem solving, impact estimation, recommendations"},
])

def generate_roadmap(days, target_role, level, hours_per_week):
    focus_map = {
        "Healthcare Data Analyst": ["SQL/Python", "KPI dashboard", "data cleaning", "portfolio analytics"],
        "Healthcare Business Analyst": ["process mapping", "requirements", "stakeholder stories", "business case"],
        "Hospital Operations Analyst": ["patient flow", "capacity", "staffing", "operations dashboard"],
        "Quality Improvement Analyst": ["quality metrics", "root cause", "PDSA", "readmission case"],
        "Revenue Cycle Analyst": ["claims", "AR days", "denials", "finance dashboard"],
        "Population Health Analyst": ["risk segments", "outreach", "screening", "equity metrics"],
        "Healthcare AI/Product Manager": ["AI use case", "model risk", "product requirements", "governance"],
        "Healthcare Consultant": ["case solving", "storyline", "diagnostic tree", "executive recommendation"]
    }
    focuses = focus_map.get(target_role, ["analytics", "dashboard", "case", "career"])
    rows = []
    for d in range(1, days+1):
        week = math.ceil(d/7)
        focus = focuses[(d-1) % len(focuses)]
        rows.append({
            "Day": d,
            "Week": week,
            "Target Role": target_role,
            "Learning Focus": focus,
            "Learning Task": f"Study one healthcare analytics concept related to {focus} and write a 5-line summary.",
            "Practice Task": f"Analyse or simulate a small dataset for {focus}. Create one chart and one managerial insight.",
            "Career Task": ["Improve LinkedIn headline", "Add one portfolio bullet", "Prepare one interview answer", "Write one STAR story", "Review one job description", "Create one dashboard screenshot", "Practice a 60-second explanation"][(d-1) % 7],
            "Evidence to Save": ["notebook", "dashboard screenshot", "case note", "GitHub commit", "interview answer", "resume bullet", "reflection note"][(d-1) % 7],
            "Time Box": f"{max(30, int(hours_per_week*60/7))} minutes"
        })
    return pd.DataFrame(rows)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
PAGES = [
    "Home", "Healthcare Analytics Map", "Executive KPI Dictionary", "Manager Decision Room 1200+",
    "Detailed Business Cases", "Analytics Sandbox 50+ Datasets", "Visual Analytics Studio",
    "MCQ Bank 500", "Interview Bank 500", "Custom Career Roadmap", "About the Developer", "Faculty Notes"
]

st.sidebar.markdown("# 🏥 Healthcare Analytics")
st.sidebar.markdown("**For Managers**  \nStory → Data → Insight → Action")
page = st.sidebar.radio("Navigate", PAGES)
st.sidebar.markdown("---")
st.sidebar.markdown("**Built for PGDM-HCM / Managers**")
st.sidebar.markdown("Copyright © Dr Alok Tiwari")

# ============================================================
# PAGE: HOME
# ============================================================
if page == "Home":
    hero(
        "Healthcare Analytics for Managers",
        "A one-stop interactive learning studio that teaches managers how to turn hospital problems, patient stories, operational data, and AI outputs into responsible decisions.",
        ["1200+ decision situations", "200+ business cases", "50+ datasets", "500 MCQs", "500 interviews", "custom career roadmap"]
    )
    callout("<b>Core idea:</b> Healthcare analytics is not just about charts. It is about improving patient outcomes, operational flow, financial sustainability, workforce planning, and ethical decision-making.")
    flow_diagram(["Business story", "Data question", "KPI", "Analysis", "Decision", "Action review"])
    c1, c2, c3 = st.columns(3)
    with c1:
        card("For managers", "No coding background is assumed. Every concept is explained through hospital decisions and managerial trade-offs.", "👩‍💼")
    with c2:
        card("For classrooms", "Use the cases, MCQs, decision rooms, and sandbox as live activities during a 75-minute session or a full course.", "🎓")
    with c3:
        card("For careers", "The app includes interview preparation, role-based roadmap creation, and portfolio-building tasks.", "🚀")

    st.subheader("What makes this app different?")
    st.markdown("""
    - It starts from **healthcare decisions**, not formulas.
    - It explains each answer using **simple language and examples**.
    - It includes **large practice banks** for revision, interviews, and case discussions.
    - It provides an **analytics sandbox** where learners can generate datasets and test charts/statistics.
    - It connects learning with **career readiness** for healthcare analytics roles.
    """)

# ============================================================
# PAGE: ANALYTICS MAP
# ============================================================
elif page == "Healthcare Analytics Map":
    hero("Healthcare Analytics Map", "Understand the full decision landscape before learning tools.", ["Clinical", "Operations", "Finance", "Experience", "AI governance"])
    domains = pd.DataFrame([
        ["Clinical quality", "Readmission, infection, adverse events", "Which patients need attention?", "Quality head / CMO"],
        ["Operations", "Waiting time, LOS, OT utilization", "Where is the bottleneck?", "COO / Operations manager"],
        ["Finance", "AR days, cost per case, net revenue", "Where is money leaking?", "CFO / finance manager"],
        ["Claims", "Denial rate, approval time", "Why are claims getting rejected?", "Insurance manager"],
        ["Workforce", "Utilization, overtime, staffing gaps", "Do we have the right staff at the right time?", "HR / Nursing head"],
        ["Population health", "Screening, adherence, risk groups", "Which population needs outreach?", "Public health manager"],
        ["AI governance", "Model drift, fairness, override rate", "Can we trust this model in practice?", "AI product manager"],
    ], columns=["Area", "Common KPIs", "Managerial question", "Primary owner"])
    st.dataframe(domains, use_container_width=True, hide_index=True)
    callout("<b>Managerial rule:</b> Do not ask 'What chart can I make?' first. Ask 'What decision must be made, by whom, and with what risk?'", "green")

# ============================================================
# PAGE: KPI DICTIONARY
# ============================================================
elif page == "Executive KPI Dictionary":
    hero("Executive KPI Dictionary", "A practical glossary of healthcare metrics for managers.", ["definitions", "formulas", "interpretation", "mistakes"])
    kpis = []
    for domain, metrics in KPI_BANK.items():
        for m in metrics:
            kpis.append({
                "Domain": domain,
                "KPI": m.title(),
                "Simple Meaning": f"A measure that helps managers understand {m} in the {domain.lower()} area.",
                "Basic Formula / Logic": "Clearly define numerator, denominator, time period, inclusion rules, and exclusions.",
                "Managerial Use": "Use it to detect variation, compare units, prioritize action, and monitor improvement.",
                "Common Mistake": "Using a raw average without checking case mix, data quality, trend, and segment differences."
            })
    kpi_df = pd.DataFrame(kpis)
    domain_filter = st.multiselect("Filter by domain", sorted(kpi_df["Domain"].unique()), default=[])
    if domain_filter:
        kpi_df = kpi_df[kpi_df["Domain"].isin(domain_filter)]
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
    download_df(kpi_df, "Download KPI dictionary", "healthcare_kpi_dictionary.csv")

# ============================================================
# PAGE: MANAGER DECISION ROOM
# ============================================================
elif page == "Manager Decision Room 1200+":
    hero(
        "Manager Decision Room 1200+",
        "Practice healthcare decisions at strategic, tactical, operational, clinical-operational, financial, and ethical-governance levels. Every selected Level × Domain × Urgency combination has at least 5 situations.",
        ["1200 situations", "5 per combination", "filters", "recommendations", "trade-offs"]
    )
    df = generate_decision_situations(min_per_combination=5)
    full_coverage = df.groupby(["Level", "Domain", "Urgency"]).size().reset_index(name="Cases")

    cA, cB, cC = st.columns(3)
    cA.metric("Total decision situations", len(df))
    cB.metric("Level × Domain × Urgency combinations", len(full_coverage))
    cC.metric("Minimum cases per combination", int(full_coverage["Cases"].min()))
    callout("<b>Coverage fixed:</b> The decision bank is now generated using a full-grid design. That means every valid filter combination, such as Strategic + Bed & Capacity + high, returns at least 5 cases.", "green")

    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            levels = st.multiselect("Decision level", DECISION_LEVELS, default=[])
        with c2:
            domains = st.multiselect("Domain", DECISION_DOMAINS, default=[])
        with c3:
            urgency = st.multiselect("Urgency", DECISION_URGENCIES, default=[])
        with c4:
            count = st.slider("Situations to display", 5, 50, 10)

    filtered = df.copy()
    if levels:
        filtered = filtered[filtered["Level"].isin(levels)]
    if domains:
        filtered = filtered[filtered["Domain"].isin(domains)]
    if urgency:
        filtered = filtered[filtered["Urgency"].isin(urgency)]

    selected_coverage = filtered.groupby(["Level", "Domain", "Urgency"]).size().reset_index(name="Cases") if len(filtered) else pd.DataFrame(columns=["Level", "Domain", "Urgency", "Cases"])
    min_selected = int(selected_coverage["Cases"].min()) if len(selected_coverage) else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Matching decision situations", len(filtered))
    m2.metric("Selected combinations covered", len(selected_coverage))
    m3.metric("Minimum cases in selected combinations", min_selected)

    if len(filtered) == 0:
        callout("No situations matched. This should not happen for normal filter choices. Clear filters or select valid values from the dropdowns.", "rose")
    else:
        st.markdown("### Filtered situation bank")
        st.dataframe(filtered.head(count), use_container_width=True, hide_index=True)
        with st.expander("Check coverage for selected filters"):
            st.dataframe(selected_coverage, use_container_width=True, hide_index=True)
        download_df(filtered, "Download filtered decision room bank", "manager_decision_room_1200_plus.csv")

        st.subheader("Practice mode")
        selected_id = st.selectbox("Choose a situation ID for detailed discussion", filtered["ID"].tolist())
        row = filtered[filtered["ID"] == selected_id].iloc[0]
        card(row["Situation"], row["Business Story"], "🧭")
        c1, c2 = st.columns(2)
        with c1:
            callout(f"<b>Decision question:</b><br>{row['Decision Question']}<br><br><b>Data to check:</b><br>{row['Data to Check']}<br><br><b>Follow-up KPI:</b><br>{row['Follow-up KPI']}", "blue")
            st.markdown(f"**Options:** {row['Options']}")
            callout(f"<b>Classroom discussion prompt:</b><br>{row['Discussion Prompt']}", "orange")
        with c2:
            if st.button("Click to reveal recommended action", key=f"decision_reveal_{selected_id}"):
                callout(f"<b>Recommended action:</b><br>{row['Recommended Action']}<br><br><b>Trade-off:</b><br>{row['Trade-off']}<br><br><b>First 7 days:</b><br>{row['First 7 Days']}<br><br><b>Managerial skill:</b><br>{row['Managerial Skill']}", "green")

# ============================================================
# PAGE: BUSINESS CASES
# ============================================================
elif page == "Detailed Business Cases":
    hero("Detailed Business Cases", "At least 20 cases per category with story, dataset design, solution steps, code logic, and managerial recommendation.", ["10 categories", "200 cases", "simple explanations", "actionable"])
    cases = generate_business_cases()
    st.markdown("### Case category coverage")
    coverage = cases.groupby("Category").size().reset_index(name="Number of cases")
    st.dataframe(coverage, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        cat = st.selectbox("Case category", ["All"] + CASE_CATEGORIES)
    with c2:
        diff = st.selectbox("Difficulty", ["All"] + DIFFICULTIES)
    with c3:
        show_n = st.slider("Cases to display", 5, 40, 10)
    filtered = cases.copy()
    if cat != "All": filtered = filtered[filtered["Category"] == cat]
    if diff != "All": filtered = filtered[filtered["Difficulty"] == diff]
    st.dataframe(filtered[["Case ID", "Category", "Difficulty", "Department", "Title"]].head(show_n), use_container_width=True, hide_index=True)
    download_df(filtered, "Download filtered business cases", "healthcare_business_cases.csv")

    st.subheader("Case discussion room")
    chosen = st.selectbox("Select case ID", filtered["Case ID"].tolist())
    case = filtered[filtered["Case ID"] == chosen].iloc[0]
    card(case["Title"], case["Business Story"], "📚")
    tabs = st.tabs(["Problem", "Dataset", "Solution", "Python logic", "Managerial answer"])
    with tabs[0]:
        callout(f"<b>Analytics question:</b><br>{case['Analytics Question']}", "blue")
        st.markdown(f"**Difficulty:** {case['Difficulty']}  ")
        st.markdown(f"**Department:** {case['Department']}")
    with tabs[1]:
        st.markdown(case["Dataset Design"])
        sample = make_sandbox_dataset(case["Department"], rows=20, seed=int(chosen))
        st.dataframe(sample.head(10), use_container_width=True)
    with tabs[2]:
        st.markdown(f"1. **Frame:** {case['Step 1 - Frame']}")
        st.markdown(f"2. **Diagnose:** {case['Step 2 - Diagnose']}")
        st.markdown(f"3. **Analyse:** {case['Step 3 - Analyse']}")
        st.markdown(f"4. **Interpret:** {case['Step 4 - Interpret']}")
        st.markdown(f"5. **Act:** {case['Step 5 - Action']}")
    with tabs[3]:
        st.code(case["Python Starter"], language="python")
        callout("This code groups the data by important segments and calculates summary values. Managers should then inspect which segment has the highest volume, worst outcome, or biggest financial impact.", "orange")
    with tabs[4]:
        if st.button("Click to reveal detailed managerial answer", key=f"case_reveal_{chosen}"):
            callout(f"<b>Recommendation:</b> {case['Managerial Recommendation']}<br><br><b>Risk / pitfall:</b> {case['Risk / Pitfall']}<br><br><b>Expected learning:</b> {case['Expected Learning']}", "green")

# ============================================================
# PAGE: SANDBOX
# ============================================================
elif page == "Analytics Sandbox 50+ Datasets":
    hero("Analytics Sandbox 50+ Datasets", "Generate healthcare datasets, select statistics, build charts, and practice managerial interpretation.", ["50 datasets", "custom rows", "missing values", "outliers", "statistics", "charts"])
    catalog = dataset_catalog()
    st.subheader("Dataset catalog")
    with st.expander("View all 50 datasets", expanded=False):
        st.dataframe(catalog, use_container_width=True, hide_index=True)
        download_df(catalog, "Download dataset catalog", "healthcare_dataset_catalog_50.csv")

    c1, c2, c3 = st.columns(3)
    with c1:
        dataset = st.selectbox("Choose dataset", DATASET_NAMES)
        rows = st.slider("Number of rows", 50, 5000, 500, step=50)
    with c2:
        seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42)
        missing_pct = st.slider("Missing values %", 0, 30, 2)
    with c3:
        outlier_pct = st.slider("Outlier %", 0, 15, 1)
        show_rows = st.slider("Preview rows", 5, 100, 15)

    df = make_sandbox_dataset(dataset, rows=rows, seed=int(seed), missing_pct=missing_pct, outlier_pct=outlier_pct)
    st.dataframe(df.head(show_rows), use_container_width=True)
    download_df(df, "Download generated dataset", f"{dataset.lower().replace(' ','_')}.csv")

    st.subheader("Statistics parameters")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    c1, c2, c3 = st.columns(3)
    with c1:
        metric = st.selectbox("Numeric metric", numeric_cols, index=numeric_cols.index("Wait_Min") if "Wait_Min" in numeric_cols else 0)
    with c2:
        group_col = st.selectbox("Group by", cat_cols, index=cat_cols.index("Department") if "Department" in cat_cols else 0)
    with c3:
        stat_options = st.multiselect("Stats to compute", ["count", "mean", "median", "std", "var", "min", "max", "iqr", "cv", "skew", "kurt", "p10", "p25", "p75", "p90"], default=["count", "mean", "median", "std", "min", "max"])

    series = df[metric].dropna()
    stats = {}
    if "count" in stat_options: stats["count"] = series.count()
    if "mean" in stat_options: stats["mean"] = series.mean()
    if "median" in stat_options: stats["median"] = series.median()
    if "std" in stat_options: stats["std"] = series.std()
    if "var" in stat_options: stats["var"] = series.var()
    if "min" in stat_options: stats["min"] = series.min()
    if "max" in stat_options: stats["max"] = series.max()
    if "iqr" in stat_options: stats["iqr"] = series.quantile(.75) - series.quantile(.25)
    if "cv" in stat_options: stats["cv"] = series.std() / series.mean() if series.mean() else np.nan
    if "skew" in stat_options: stats["skew"] = series.skew()
    if "kurt" in stat_options: stats["kurt"] = series.kurt()
    if "p10" in stat_options: stats["p10"] = series.quantile(.10)
    if "p25" in stat_options: stats["p25"] = series.quantile(.25)
    if "p75" in stat_options: stats["p75"] = series.quantile(.75)
    if "p90" in stat_options: stats["p90"] = series.quantile(.90)
    stats_df = pd.DataFrame([stats]).T.reset_index()
    stats_df.columns = ["Statistic", "Value"]
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Grouped summary")
        grouped = df.groupby(group_col)[metric].agg(["count", "mean", "median", "std", "min", "max"]).reset_index()
        st.dataframe(grouped, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### Missing values")
        missing = df.isna().sum().reset_index()
        missing.columns = ["Column", "Missing Count"]
        st.dataframe(missing, use_container_width=True, hide_index=True)

    st.markdown("#### Correlation matrix")
    corr_cols = st.multiselect("Select numeric columns for correlation", numeric_cols, default=[c for c in ["Wait_Min", "LOS_Days", "Cost", "Revenue", "Satisfaction", "Risk_Score"] if c in numeric_cols])
    if len(corr_cols) >= 2:
        st.dataframe(df[corr_cols].corr().round(2), use_container_width=True)

    st.markdown("#### Outlier detector")
    q1, q3 = series.quantile(.25), series.quantile(.75)
    iqr = q3 - q1
    outliers = df[(df[metric] < q1 - 1.5*iqr) | (df[metric] > q3 + 1.5*iqr)]
    st.write(f"Detected **{len(outliers)}** possible outliers in **{metric}** using the IQR rule.")
    if len(outliers) > 0:
        st.dataframe(outliers.head(20), use_container_width=True)

    st.subheader("Chart builder")
    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Area", "Pie", "Scatter", "Histogram", "Box plot", "Heatmap", "Pareto", "Waterfall"])
    fig, ax = plt.subplots(figsize=(9, 4.8))
    try:
        if chart_type == "Bar":
            grouped.sort_values("mean", ascending=False).plot(kind="bar", x=group_col, y="mean", ax=ax, legend=False)
            ax.set_ylabel(metric)
        elif chart_type == "Line":
            temp = df.groupby("Month")[metric].mean().reindex(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
            temp.plot(kind="line", marker="o", ax=ax)
            ax.set_ylabel(metric)
        elif chart_type == "Area":
            temp = df.groupby("Month")[metric].mean().reindex(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
            ax.fill_between(range(len(temp)), temp.values)
            ax.set_xticks(range(len(temp))); ax.set_xticklabels(temp.index, rotation=45)
            ax.set_ylabel(metric)
        elif chart_type == "Pie":
            temp = df[group_col].value_counts().head(8)
            ax.pie(temp.values, labels=temp.index, autopct="%1.1f%%")
        elif chart_type == "Scatter":
            x = st.selectbox("Scatter X", numeric_cols, index=0)
            y = st.selectbox("Scatter Y", numeric_cols, index=1 if len(numeric_cols)>1 else 0)
            ax.scatter(df[x], df[y], alpha=.55)
            ax.set_xlabel(x); ax.set_ylabel(y)
        elif chart_type == "Histogram":
            ax.hist(series, bins=25)
            ax.set_xlabel(metric); ax.set_ylabel("Frequency")
        elif chart_type == "Box plot":
            df.boxplot(column=metric, by=group_col, ax=ax, rot=45)
            fig.suptitle("")
        elif chart_type == "Heatmap":
            corr = df[corr_cols].corr() if len(corr_cols)>=2 else df[numeric_cols[:6]].corr()
            im = ax.imshow(corr, aspect="auto")
            ax.set_xticks(range(len(corr.columns))); ax.set_xticklabels(corr.columns, rotation=45, ha="right")
            ax.set_yticks(range(len(corr.index))); ax.set_yticklabels(corr.index)
            fig.colorbar(im, ax=ax)
        elif chart_type == "Pareto":
            temp = df.groupby(group_col)[metric].sum().sort_values(ascending=False)
            cum = temp.cumsum() / temp.sum() * 100
            ax.bar(temp.index, temp.values)
            ax2 = ax.twinx(); ax2.plot(temp.index, cum.values, marker="o")
            ax.tick_params(axis='x', rotation=45); ax2.set_ylabel("Cumulative %")
        elif chart_type == "Waterfall":
            temp = df.groupby(group_col)["Profit"].sum().sort_values(ascending=False).head(6)
            running = temp.cumsum().shift(fill_value=0)
            ax.bar(temp.index, temp.values, bottom=running)
            ax.tick_params(axis='x', rotation=45); ax.set_ylabel("Profit contribution")
        ax.set_title(f"{chart_type}: {dataset}")
        st.pyplot(fig)
    finally:
        plt.close(fig)

    if st.button("Click to reveal managerial interpretation template"):
        callout(f"For this dataset, start by explaining what happened to <b>{metric}</b>, where it is highest or lowest by <b>{group_col}</b>, whether the pattern is stable over time, and what action a manager should take next. Avoid saying 'the chart shows...' only. Say what decision the chart supports.", "green")

# ============================================================
# PAGE: VISUAL ANALYTICS
# ============================================================
elif page == "Visual Analytics Studio":
    hero("Visual Analytics Studio", "Choose the right chart for the right healthcare decision.", ["chart selection", "interpretation", "managerial storytelling"])
    chart_guide = pd.DataFrame([
        ["Bar", "Compare departments", "Which department has the highest wait time?"],
        ["Line", "Show trend", "Is readmission improving month by month?"],
        ["Pie/Donut", "Show share of a total", "What share of claims are denied by payer?"],
        ["Scatter", "Show relationship", "Does cost increase with LOS?"],
        ["Histogram", "Show distribution", "Are waits usually short or often extreme?"],
        ["Box plot", "Compare spread", "Which unit has more variation?"],
        ["Heatmap", "Show intensity matrix", "Which shift-department combination is risky?"],
        ["Pareto", "Find vital few", "Which causes explain most denials?"],
        ["Waterfall", "Explain contribution", "Which units create or reduce profit?"],
        ["Radar", "Compare multiple dimensions", "Which hospital branch performs better across KPIs?"],
    ], columns=["Chart", "Best Use", "Healthcare Example"])
    st.dataframe(chart_guide, use_container_width=True, hide_index=True)
    callout("<b>Important:</b> A chart is useful only when it supports a decision. For managers, every chart should end with: So what should we do?", "blue")

# ============================================================
# PAGE: MCQ BANK 500
# ============================================================
elif page == "MCQ Bank 500":
    hero("MCQ Bank 500", "Practice 500 healthcare analytics questions with simple explanations and click-to-reveal answers.", ["500 MCQs", "no auto-select", "filters", "examples"])
    mcq = generate_mcqs(500)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        topic = st.multiselect("Topic", sorted(mcq["Topic"].unique()), default=[])
    with c2:
        qtype = st.multiselect("Question type", sorted(mcq["Type"].unique()), default=[])
    with c3:
        difficulty = st.multiselect("Difficulty", DIFFICULTIES, default=[])
    with c4:
        nshow = st.slider("Questions to display", 5, 50, 10)
    filtered = mcq.copy()
    if topic: filtered = filtered[filtered["Topic"].isin(topic)]
    if qtype: filtered = filtered[filtered["Type"].isin(qtype)]
    if difficulty: filtered = filtered[filtered["Difficulty"].isin(difficulty)]
    st.metric("Matching MCQs", len(filtered))
    download_df(filtered, "Download filtered MCQ bank", "healthcare_analytics_mcq_500.csv")
    st.markdown("No option is pre-selected. Read the options, think, then click the reveal button.")
    for _, row in filtered.head(nshow).iterrows():
        st.markdown(f"### {row['Question']}")
        st.markdown(f"<span class='tag'>{row['Topic']}</span><span class='tag'>{row['Type']}</span><span class='tag'>{row['Difficulty']}</span>", unsafe_allow_html=True)
        st.markdown(f"A. {row['A']}")
        st.markdown(f"B. {row['B']}")
        st.markdown(f"C. {row['C']}")
        st.markdown(f"D. {row['D']}")
        if st.button("Click to reveal answer", key=f"mcq_{int(row['ID'])}"):
            callout(f"<b>Correct answer: {row['Answer']}</b><br>{row['Explanation']}<br><br><b>Example:</b> {row['Example']}", "green")
        st.markdown("---")

# ============================================================
# PAGE: INTERVIEW BANK 500
# ============================================================
elif page == "Interview Bank 500":
    hero("Interview Bank 500", "Prepare for healthcare analytics roles using filtered interview questions, examples, mistakes, and spoken answers.", ["500 questions", "target job filter", "simple answers", "interview-ready"])
    bank = generate_interview_questions(500)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        job = st.selectbox("Target job", ["All"] + TARGET_JOBS)
    with c2:
        cat = st.selectbox("Category", ["All"] + INTERVIEW_CATEGORIES)
    with c3:
        diff = st.selectbox("Difficulty", ["All"] + DIFFICULTIES)
    with c4:
        nshow = st.slider("Questions to display", 5, 50, 10, key="interview_nshow")
    apply = st.button("Apply interview filters")
    filtered = bank.copy()
    if job != "All": filtered = filtered[filtered["Target Job"] == job]
    if cat != "All": filtered = filtered[filtered["Category"] == cat]
    if diff != "All": filtered = filtered[filtered["Difficulty"] == diff]
    st.metric("Matching interview questions", len(filtered))
    download_df(filtered, "Download filtered interview bank", "healthcare_interview_bank_500.csv")
    for _, row in filtered.head(nshow).iterrows():
        st.markdown(f"### Q{int(row['ID'])}. {row['Question']}")
        st.markdown(f"<span class='tag'>{row['Target Job']}</span><span class='tag'>{row['Category']}</span><span class='tag'>{row['Difficulty']}</span>", unsafe_allow_html=True)
        if st.button("Click to reveal detailed answer", key=f"int_{int(row['ID'])}"):
            callout(f"<b>Answer:</b> {row['Answer']}<br><br><b>Simple example:</b> {row['Simple Example']}<br><br><b>Interview-ready spoken answer:</b> {row['Interview-ready Spoken Answer']}<br><br><b>Common mistake:</b> {row['Common Mistake']}<br><br><b>Managerial angle:</b> {row['Managerial Angle']}", "green")
        st.markdown("---")

# ============================================================
# PAGE: CUSTOM ROADMAP
# ============================================================
elif page == "Custom Career Roadmap":
    hero("Custom Career Roadmap", "Create a personalised healthcare analytics learning and career-readiness roadmap for any number of days.", ["custom days", "target job", "portfolio", "interviews", "career readiness"])
    st.subheader("Career options")
    role_filter = st.multiselect("Filter career options", CAREER_OPTIONS["Role"].tolist(), default=[])
    roles_view = CAREER_OPTIONS if not role_filter else CAREER_OPTIONS[CAREER_OPTIONS["Role"].isin(role_filter)]
    st.dataframe(roles_view, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        target = st.selectbox("Target job", TARGET_JOBS)
        days = st.slider("Roadmap length in days", 7, 180, 30)
    with c2:
        level = st.selectbox("Current level", ["Beginner", "Some analytics exposure", "Intermediate", "Career switcher"])
        hours = st.slider("Hours per week", 2, 25, 7)
    with c3:
        focus = st.multiselect("Extra focus", ["Python", "SQL", "Dashboards", "Statistics", "Healthcare operations", "Finance/claims", "AI ethics", "Interview prep", "Portfolio"], default=["Dashboards", "Interview prep", "Portfolio"])
    roadmap = generate_roadmap(days, target, level, hours)
    st.subheader("Generated roadmap")
    st.dataframe(roadmap.head(min(days, 60)), use_container_width=True, hide_index=True)
    if days > 60:
        st.info("Showing first 60 days in preview. Download the full roadmap below.")
    download_df(roadmap, "Download full custom roadmap", f"{target.lower().replace(' ','_')}_roadmap_{days}_days.csv")
    if st.button("Click to reveal career-readiness checklist"):
        callout("<b>Career-ready evidence:</b> 1 strong resume headline, 2 healthcare dashboard screenshots, 2 case write-ups, 1 GitHub/project link, 10 interview answers, 5 STAR stories, 1 LinkedIn featured project, and a clear 60-second pitch for your target role.", "green")

# ============================================================
# PAGE: ABOUT DEVELOPER
# ============================================================
elif page == "About the Developer":
    hero("About the Developer", "Dr Alok Tiwari — AI, Healthcare Analytics, Educator, and applied decision-science practitioner.", ["Assistant Professor", "Big Data Analytics", "Healthcare AI", "Management Analytics"])
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("""
        ### Dr Alok Tiwari
        **Assistant Professor – Big Data Analytics, Goa Institute of Management, Goa**

        Dr Alok Tiwari works at the intersection of **machine learning, medical imaging, explainable AI, healthcare analytics, and management-focused data science**. His teaching and applied work are built around a simple belief: technical concepts become meaningful for managers only when they improve real decisions.

        His academic background includes a **PhD in Biomedical Engineering from IIT (BHU), Varanasi**, with research in transfer learning for COVID-19 classification and weakly supervised cardiac MRI segmentation. He also holds an M.Tech. in Biomedical Engineering from NIT Kurukshetra and a B.Tech. in Electronics & Communication.
        """)
        callout("<b>Teaching philosophy:</b> Every technical concept taught to a manager must arrive with a decision they can make, or it is not yet finished.", "orange")
    with c2:
        st.markdown("""
        ### Portfolio
        - Portfolio: https://dr-alok-tiwari.github.io/
        - Email: shodhkarta.alok@gmail.com
        - Areas: Healthcare AI, Medical Imaging, Explainable AI, MLOps, Data Science, Management Analytics
        """)
        st.link_button("Open portfolio", "https://dr-alok-tiwari.github.io/")

    st.subheader("Research and applied areas")
    research = pd.DataFrame([
        ["Medical Image Analysis", "MRI, chest X-ray, clinical imaging, segmentation, classification"],
        ["Explainable & Ethical AI", "LIME, SHAP, trustworthy systems, fairness, accountability"],
        ["Applied Data Science", "Healthcare, business, policy, and decision analytics"],
        ["Pedagogy & Learning Innovation", "GenAI-enabled teaching, FDPs, MDPs, executive learning"],
        ["Industry-Oriented Analytics", "Practical analytics for managers, dashboards, SQL, Power BI, Python"],
        ["Production-ready AI", "Docker, MLflow, Git, cloud workflows, deployment thinking"],
    ], columns=["Area", "Description"])
    st.dataframe(research, use_container_width=True, hide_index=True)

    st.subheader("Teaching portfolio")
    teaching = pd.DataFrame([
        ["Healthcare Analytics", "PGDM-HCM", "Clinical, operational, public-health, and healthcare decision analytics"],
        ["Sports Analytics", "PGDM-BDA", "Performance analytics, scouting, team and player metrics"],
        ["MLOps", "PGDM-BDA / professional cohorts", "Experiment tracking, deployment, reproducibility, ML lifecycle"],
        ["Data Visualization", "PGDM-BDA", "Storytelling, dashboard thinking, visual analytics"],
        ["AI for Managers / GenAI", "MDPs / FDPs", "Executive AI literacy, productivity, governance, adoption"],
        ["Python, SQL, ML, DL", "Data engineering and analytics learners", "Hands-on programming and analytics workflows"],
    ], columns=["Course / Area", "Audience", "Focus"])
    st.dataframe(teaching, use_container_width=True, hide_index=True)

    st.subheader("Selected projects and publications themes")
    st.markdown("""
    - Cardiac MRI segmentation using weakly supervised deep learning pipelines.
    - COVID-19 and chest X-ray classification using transfer learning.
    - Brain stroke detection from neuroimaging data.
    - Modified Pan-Tompkins algorithm for arrhythmia detection.
    - GenAI-enabled teaching frameworks and executive learning tools.
    - Healthcare analytics and AI tools for management education.
    """)
    st.subheader("Why this app was created")
    callout("This app is designed to help healthcare management students and working managers move from passive dashboard viewing to active decision-making. It combines business stories, synthetic datasets, case analysis, quizzes, interviews, and career planning in one place.", "green")

# ============================================================
# PAGE: FACULTY NOTES
# ============================================================
elif page == "Faculty Notes":
    hero("Faculty Notes", "Suggested classroom use for a 75-minute overview session or a full module.", ["teaching plan", "activities", "assessment"])
    plan = pd.DataFrame([
        ["0–10 min", "Healthcare analytics mindset", "Ask: What healthcare decision is difficult without data?"],
        ["10–20 min", "KPI dictionary", "Students map problems to KPIs"],
        ["20–35 min", "Decision room", "Group discussion on 2–3 situations"],
        ["35–50 min", "Business case", "One detailed case with managerial recommendation"],
        ["50–65 min", "Sandbox", "Generate dataset, make one chart, interpret"],
        ["65–75 min", "MCQ/interview/roadmap", "Reveal answers and career link"],
    ], columns=["Time", "Focus", "Activity"])
    st.dataframe(plan, use_container_width=True, hide_index=True)
    callout("For management students, avoid starting with algorithms. Start with patient journey, manager pain point, KPI definition, and decision consequence.", "blue")

st.markdown("<div class='footer-note'>Healthcare Analytics for Managers · Story → Data → Insight → Action · Copyright © Dr Alok Tiwari</div>", unsafe_allow_html=True)
