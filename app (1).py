import streamlit as st
import json
import datetime
import io
import re
from groq import Groq

st.set_page_config(
    page_title="AI Exam Question Generator",
    page_icon="🎓",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap');
  html, body, [class*="css"] { background:#0f1117!important; color:#e2e8f0!important; font-family:'Inter',sans-serif!important; }
  .stApp { background:#0f1117!important; }
  .block-container { padding-top:1.5rem!important; }
  h1,h2,h3 { color:#6ee7f7!important; }
  [data-testid="stSidebar"] { background:#080c14!important; border-right:1px solid #1e2d45!important; }
  .stButton>button { background:#0d1f3c!important; color:#6ee7f7!important; border:1px solid #6ee7f744!important; border-radius:6px!important; font-size:13px!important; transition:all 0.2s; }
  .stButton>button:hover { background:#6ee7f722!important; border-color:#6ee7f7!important; }
  .stButton>button[kind="primary"] { background:linear-gradient(135deg,#6ee7f722,#a78bfa22)!important; border:1px solid #6ee7f7!important; font-weight:bold!important; color:#6ee7f7!important; }
  [data-testid="stMetric"] { background:#0d1526!important; border:1px solid #1e2d45!important; border-radius:8px!important; padding:10px!important; }
  [data-testid="stMetricValue"] { color:#6ee7f7!important; }
  [data-testid="stMetricLabel"] { color:#4a6a8a!important; font-size:0.65rem!important; }
  .q-card { background:#0d1526; border:1px solid #1e2d45; border-radius:10px; padding:16px 20px; margin:10px 0; }
  .q-card.mcq    { border-left:4px solid #6ee7f7; }
  .q-card.short  { border-left:4px solid #a78bfa; }
  .q-card.long   { border-left:4px solid #34d399; }
  .q-card.case   { border-left:4px solid #f59e0b; }
  .q-num  { font-size:11px; color:#4a6a8a; font-family:monospace; margin-bottom:6px; }
  .q-text { font-size:14px; color:#e2e8f0; margin-bottom:8px; line-height:1.6; }
  .q-opt  { font-size:13px; color:#94a3b8; margin:3px 0 3px 16px; }
  .q-ans  { font-size:12px; color:#34d399; margin-top:8px; padding:6px 10px; background:#0a1f14; border-radius:4px; font-family:monospace; }
  .q-diff { font-size:10px; padding:2px 8px; border-radius:10px; float:right; font-weight:600; }
  .diff-easy   { background:#0a1f14; color:#34d399; }
  .diff-medium { background:#1a1500; color:#f59e0b; }
  .diff-hard   { background:#1f0a0a; color:#ef4444; }
  .section-header { background:#0d1526; border:1px solid #1e2d45; border-radius:8px; padding:10px 16px; margin:16px 0 8px 0; font-weight:700; font-size:14px; letter-spacing:1px; }
  .upload-zone { background:#0d1526; border:2px dashed #1e2d45; border-radius:10px; padding:20px; text-align:center; color:#4a6a8a; font-size:13px; }
  .stTextArea textarea { background:#0d1526!important; border:1px solid #1e2d45!important; color:#e2e8f0!important; font-family:'JetBrains Mono',monospace!important; font-size:12px!important; }
  .stSelectbox>div>div,.stMultiSelect>div>div { background:#0d1526!important; border:1px solid #1e2d45!important; color:#e2e8f0!important; }
  .stSelectbox label,.stSlider label,.stCheckbox label,.stNumberInput label { color:#4a6a8a!important; font-size:12px!important; }
  .stTabs [data-baseweb="tab"] { color:#4a6a8a!important; font-size:13px!important; }
  .stTabs [aria-selected="true"] { color:#6ee7f7!important; border-bottom:2px solid #6ee7f7!important; }
  .stProgress>div>div { background:#6ee7f7!important; }
  hr { border-color:#1e2d45!important; }
  [data-testid="stExpander"] { border:1px solid #1e2d45!important; background:#0d1526!important; }
  .streamlit-expanderHeader { color:#6ee7f7!important; }
  .stSuccess { background:#0a1f14!important; border:1px solid #34d399!important; color:#34d399!important; }
  .stWarning { background:#1a1500!important; border:1px solid #f59e0b!important; }
  .stInfo    { background:#0a1526!important; border:1px solid #6ee7f744!important; }
</style>
""", unsafe_allow_html=True)

# ── Secrets ───────────────────────────────────────────────────────────────────
default_key = st.secrets.get("GROQ_API_KEY", "")

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("questions", {}), ("raw_text", ""), ("generated", False), ("course_info", {})]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ CONFIGURATION")
    api_key = st.text_input("Groq API Key", value=default_key, type="password", placeholder="gsk_...")
    model   = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.divider()

    st.markdown("### 📊 QUESTION SETTINGS")
    n_mcq   = st.slider("MCQs per difficulty",    1, 15, 5)
    n_short = st.slider("Short Qs per difficulty", 1, 10, 3)
    n_long  = st.slider("Long Qs per difficulty",  1, 5,  2)
    n_case  = st.slider("Case Studies",            1, 5,  1)
    st.divider()

    st.markdown("### 🎯 DIFFICULTY LEVELS")
    diff_easy   = st.checkbox("Easy",   value=True)
    diff_medium = st.checkbox("Medium", value=True)
    diff_hard   = st.checkbox("Hard",   value=True)
    st.divider()

    st.markdown("### 📋 QUESTION TYPES")
    gen_mcq   = st.checkbox("MCQs (4 options)", value=True)
    gen_short = st.checkbox("Short Questions",  value=True)
    gen_long  = st.checkbox("Long Questions",   value=True)
    gen_case  = st.checkbox("Case Studies",     value=True)

    difficulties = []
    if diff_easy:   difficulties.append("easy")
    if diff_medium: difficulties.append("medium")
    if diff_hard:   difficulties.append("hard")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🎓 AI EXAM QUESTION GENERATOR")
st.caption("Upload course material · AI generates full exam paper · Download instantly · Powered by Groq + Llama 3")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📥 INPUT MATERIAL", "❓ GENERATED QUESTIONS", "📄 EXPORT"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Input
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🏫 COURSE INFORMATION")
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        course_name  = st.text_input("Course Name",    placeholder="e.g. Artificial Intelligence", key="course_name")
        course_code  = st.text_input("Course Code",    placeholder="e.g. CS-401", key="course_code")
    with ci2:
        instructor   = st.text_input("Instructor",     placeholder="Your name", key="instructor")
        university   = st.text_input("University",     placeholder="e.g. Superior University", key="university")
    with ci3:
        semester     = st.text_input("Semester",       placeholder="e.g. Fall 2024", key="semester")
        exam_type    = st.selectbox("Exam Type", ["Mid-Term","Final","Quiz","Assignment","Practice"], key="exam_type")

    st.markdown("### 📄 COURSE MATERIAL")
    input_tab1, input_tab2 = st.tabs(["📎 Upload PDF", "📝 Paste Text"])

    with input_tab1:
        uploaded_file = st.file_uploader(
            "Upload lecture notes, slides, or textbook chapter (PDF)",
            type=["pdf"],
            help="Max 10MB. Text will be extracted automatically."
        )
        if uploaded_file:
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                st.session_state.raw_text = text
                st.success(f"✅ PDF loaded — {len(pdf.pages)} pages, {len(text.split())} words extracted")
                with st.expander("👁 Preview extracted text"):
                    st.text(text[:2000] + ("…" if len(text) > 2000 else ""))
            except ImportError:
                # Fallback without pdfplumber
                st.warning("⚠️ pdfplumber not installed. Using PyPDF2 fallback.")
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(uploaded_file)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    st.session_state.raw_text = text
                    st.success(f"✅ PDF loaded — {len(reader.pages)} pages extracted")
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
            except Exception as e:
                st.error(f"PDF error: {e}")

    with input_tab2:
        pasted = st.text_area(
            "Paste your lecture notes, topic summary, or any course content here",
            height=300,
            placeholder="""Example:
Chapter 5: Neural Networks

A neural network is a computational model inspired by the human brain.
It consists of layers of interconnected nodes (neurons).

Key concepts:
- Input layer: receives raw data
- Hidden layers: perform transformations
- Output layer: produces predictions
- Activation functions: ReLU, Sigmoid, Tanh
- Backpropagation: algorithm for training
- Gradient descent: optimization method
...""",
            key="pasted_text"
        )
        if pasted.strip():
            st.session_state.raw_text = pasted
            st.success(f"✅ Text ready — {len(pasted.split())} words")

    # Topic focus
    st.markdown("### 🎯 FOCUS TOPICS (optional)")
    focus_topics = st.text_input(
        "Specific topics to focus on (comma-separated)",
        placeholder="e.g. backpropagation, activation functions, gradient descent",
        key="focus_topics"
    )

    st.markdown("### 📝 ADDITIONAL INSTRUCTIONS (optional)")
    extra_inst = st.text_area(
        "Any special instructions for the AI",
        height=70,
        placeholder="e.g. Focus on practical applications, include Pakistani healthcare context, avoid memorization questions…",
        key="extra_inst"
    )

    st.divider()

    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        gen_btn = st.button(
            "🧠 GENERATE EXAM PAPER",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.raw_text or not api_key
        )
    with col_clear:
        if st.button("🗑 CLEAR", use_container_width=True):
            st.session_state.raw_text = ""
            st.session_state.questions = {}
            st.session_state.generated = False
            st.rerun()

    if not api_key:
        st.warning("⚠️ Add your Groq API key in the sidebar")
    if not st.session_state.raw_text:
        st.info("📄 Upload a PDF or paste text above to begin")


# ══════════════════════════════════════════════════════════════════════════════
# AI Generation
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are an expert academic exam question generator for university-level courses.
Generate exam questions from the provided course material.
Return ONLY valid JSON. No markdown fences. No explanation.

JSON format:
{{
  "mcqs": [
    {{"q": "question text", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "answer": "A", "explanation": "brief explanation", "difficulty": "easy|medium|hard"}}
  ],
  "short_questions": [
    {{"q": "question text", "answer": "model answer (2-3 sentences)", "marks": 5, "difficulty": "easy|medium|hard"}}
  ],
  "long_questions": [
    {{"q": "question text", "answer": "detailed model answer", "marks": 10, "difficulty": "medium|hard"}}
  ],
  "case_studies": [
    {{"title": "case title", "scenario": "detailed scenario paragraph", "questions": ["q1", "q2", "q3"], "answers": ["a1", "a2", "a3"], "marks": 20}}
  ]
}}"""

def generate_questions(api_key, material, course_info, difficulties, n_mcq, n_short, n_long, n_case,
                       gen_mcq, gen_short, gen_long, gen_case, focus_topics, extra_inst):
    client = Groq(api_key=api_key)

    # Truncate material to fit context
    material_excerpt = material[:6000] if len(material) > 6000 else material

    types_requested = []
    if gen_mcq:   types_requested.append(f"{n_mcq} MCQs per difficulty level ({', '.join(difficulties)})")
    if gen_short: types_requested.append(f"{n_short} short questions per difficulty level")
    if gen_long:  types_requested.append(f"{n_long} long questions (medium and hard)")
    if gen_case:  types_requested.append(f"{n_case} case stud{'y' if n_case==1 else 'ies'}")

    user_prompt = f"""Course: {course_info.get('name','General')} ({course_info.get('code','')})
Exam Type: {course_info.get('exam_type','Mid-Term')}
Difficulty levels needed: {', '.join(difficulties)}
Generate: {'; '.join(types_requested)}
{f'Focus topics: {focus_topics}' if focus_topics else ''}
{f'Special instructions: {extra_inst}' if extra_inst else ''}

COURSE MATERIAL:
{material_excerpt}

Generate the questions now. Return ONLY the JSON object."""

    resp = client.chat.completions.create(
        model=model,
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
    )

    raw = resp.choices[0].message.content.strip()
    # Clean JSON
    raw = raw.replace("```json","").replace("```","").strip()
    s = raw.find("{"); e = raw.rfind("}") + 1
    return json.loads(raw[s:e])


if gen_btn and st.session_state.raw_text and api_key:
    course_info = {
        "name": course_name, "code": course_code,
        "instructor": instructor, "university": university,
        "semester": semester, "exam_type": exam_type,
    }
    st.session_state.course_info = course_info

    with st.spinner("🧠 ARIA is reading your material and generating questions…"):
        prog = st.progress(0, text="Analyzing course material…")
        try:
            prog.progress(30, text="Generating MCQs…")
            questions = generate_questions(
                api_key, st.session_state.raw_text, course_info,
                difficulties, n_mcq, n_short, n_long, n_case,
                gen_mcq, gen_short, gen_long, gen_case,
                focus_topics, extra_inst
            )
            prog.progress(100, text="Done ✅")
            st.session_state.questions = questions
            st.session_state.generated = True
            st.success(f"✅ Exam paper generated! Switch to GENERATED QUESTIONS tab.")
        except Exception as e:
            st.error(f"Generation error: {e}")
            import traceback
            st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Questions Display
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.generated:
        st.info("📄 Generate questions from the INPUT MATERIAL tab first.")
    else:
        q = st.session_state.questions
        ci = st.session_state.course_info

        # Header
        st.markdown(f"## 📋 {ci.get('exam_type','Exam').upper()} — {ci.get('name','Course').upper()}")
        st.markdown(f'<span style="color:#4a6a8a;font-size:12px">{ci.get("university","")} | {ci.get("semester","")} | Instructor: {ci.get("instructor","")}</span>', unsafe_allow_html=True)
        st.divider()

        # Stats
        mcqs   = q.get("mcqs", [])
        shorts = q.get("short_questions", [])
        longs  = q.get("long_questions", [])
        cases  = q.get("case_studies", [])
        total_marks = (
            len(mcqs) * 1 +
            sum(s.get("marks", 5) for s in shorts) +
            sum(l.get("marks", 10) for l in longs) +
            sum(c.get("marks", 20) for c in cases)
        )

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("MCQs",            len(mcqs))
        s2.metric("Short Questions", len(shorts))
        s3.metric("Long Questions",  len(longs))
        s4.metric("Case Studies",    len(cases))
        s5.metric("Total Marks",     total_marks)
        st.divider()

        show_answers = st.toggle("👁 Show Answer Keys", value=False)

        # ── MCQs ──────────────────────────────────────────────────────────────
        if mcqs:
            st.markdown('<div class="section-header">📝 SECTION A — MULTIPLE CHOICE QUESTIONS (1 mark each)</div>', unsafe_allow_html=True)
            for i, item in enumerate(mcqs):
                diff  = item.get("difficulty","medium")
                diff_css = f'<span class="q-diff diff-{diff}">{diff.upper()}</span>'
                opts_html = "".join([f'<div class="q-opt">({k}) {v}</div>' for k, v in item.get("options",{}).items()])
                ans_html  = f'<div class="q-ans">✅ Answer: {item.get("answer","")} — {item.get("explanation","")}</div>' if show_answers else ""
                st.markdown(
                    f'<div class="q-card mcq">'
                    f'{diff_css}'
                    f'<div class="q-num">Q{i+1} | MCQ | 1 Mark</div>'
                    f'<div class="q-text">{item.get("q","")}</div>'
                    f'{opts_html}{ans_html}</div>',
                    unsafe_allow_html=True
                )

        # ── Short Questions ───────────────────────────────────────────────────
        if shorts:
            st.markdown('<div class="section-header">✏️ SECTION B — SHORT QUESTIONS</div>', unsafe_allow_html=True)
            for i, item in enumerate(shorts):
                diff = item.get("difficulty","medium")
                marks = item.get("marks", 5)
                ans_html = f'<div class="q-ans">✅ Model Answer: {item.get("answer","")}</div>' if show_answers else ""
                st.markdown(
                    f'<div class="q-card short">'
                    f'<span class="q-diff diff-{diff}">{diff.upper()}</span>'
                    f'<div class="q-num">Q{i+1} | Short Question | {marks} Marks</div>'
                    f'<div class="q-text">{item.get("q","")}</div>'
                    f'{ans_html}</div>',
                    unsafe_allow_html=True
                )

        # ── Long Questions ────────────────────────────────────────────────────
        if longs:
            st.markdown('<div class="section-header">📖 SECTION C — LONG QUESTIONS</div>', unsafe_allow_html=True)
            for i, item in enumerate(longs):
                diff = item.get("difficulty","hard")
                marks = item.get("marks", 10)
                ans_html = f'<div class="q-ans">✅ Model Answer: {item.get("answer","")}</div>' if show_answers else ""
                st.markdown(
                    f'<div class="q-card long">'
                    f'<span class="q-diff diff-{diff}">{diff.upper()}</span>'
                    f'<div class="q-num">Q{i+1} | Long Question | {marks} Marks</div>'
                    f'<div class="q-text">{item.get("q","")}</div>'
                    f'{ans_html}</div>',
                    unsafe_allow_html=True
                )

        # ── Case Studies ──────────────────────────────────────────────────────
        if cases:
            st.markdown('<div class="section-header">🔬 SECTION D — CASE STUDIES</div>', unsafe_allow_html=True)
            for i, item in enumerate(cases):
                marks = item.get("marks", 20)
                qs_html = "".join([f'<div class="q-opt">({chr(97+j)}) {cq}</div>' for j, cq in enumerate(item.get("questions",[]))])
                ans_html = ""
                if show_answers:
                    ans_html = "<br>".join([f'✅ ({chr(97+j)}) {ca}' for j, ca in enumerate(item.get("answers",[]))])
                    ans_html = f'<div class="q-ans">{ans_html}</div>'
                st.markdown(
                    f'<div class="q-card case">'
                    f'<div class="q-num">CASE STUDY {i+1} | {marks} Marks</div>'
                    f'<div class="q-text"><b>{item.get("title","")}</b></div>'
                    f'<div class="q-text" style="color:#94a3b8">{item.get("scenario","")}</div>'
                    f'<div style="margin-top:8px;font-size:12px;color:#f59e0b">Questions:</div>'
                    f'{qs_html}{ans_html}</div>',
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Export
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.generated:
        st.info("📄 Generate questions first.")
    else:
        q  = st.session_state.questions
        ci = st.session_state.course_info
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        mcqs   = q.get("mcqs", [])
        shorts = q.get("short_questions", [])
        longs  = q.get("long_questions", [])
        cases  = q.get("case_studies", [])
        total_marks = (
            len(mcqs) +
            sum(s.get("marks",5) for s in shorts) +
            sum(l.get("marks",10) for l in longs) +
            sum(c.get("marks",20) for c in cases)
        )

        st.markdown("### 📊 PAPER SUMMARY")
        sc1,sc2,sc3,sc4,sc5 = st.columns(5)
        sc1.metric("MCQs",            len(mcqs))
        sc2.metric("Short Questions", len(shorts))
        sc3.metric("Long Questions",  len(longs))
        sc4.metric("Case Studies",    len(cases))
        sc5.metric("Total Marks",     total_marks)

        st.divider()

        # ── Build report text ─────────────────────────────────────────────────
        def build_report(include_answers):
            lines = []
            lines.append("=" * 70)
            lines.append(f"  {ci.get('university','').upper()}")
            lines.append(f"  {ci.get('exam_type','EXAMINATION').upper()} PAPER")
            lines.append("=" * 70)
            lines.append(f"  Course    : {ci.get('name','')} ({ci.get('code','')})")
            lines.append(f"  Semester  : {ci.get('semester','')}")
            lines.append(f"  Instructor: {ci.get('instructor','')}")
            lines.append(f"  Date      : {now}")
            lines.append(f"  Total Marks: {total_marks}")
            lines.append(f"  {'*** ANSWER KEY INCLUDED ***' if include_answers else 'Student Copy'}")
            lines.append("=" * 70)
            lines.append("")
            lines.append("  Instructions:")
            lines.append("  - Attempt all sections.")
            lines.append("  - Mobile phones are not allowed.")
            lines.append("  - Write your name and roll number clearly.")
            lines.append("")

            # MCQs
            if mcqs:
                lines.append("-" * 70)
                lines.append(f"  SECTION A: MULTIPLE CHOICE QUESTIONS  [{len(mcqs)} Marks]")
                lines.append("  (Circle the correct option)")
                lines.append("-" * 70)
                for i, item in enumerate(mcqs):
                    lines.append(f"\n  Q{i+1}. [{item.get('difficulty','').upper()}] {item.get('q','')}")
                    for k, v in item.get("options", {}).items():
                        lines.append(f"       ({k}) {v}")
                    if include_answers:
                        lines.append(f"       >> Answer: {item.get('answer','')} — {item.get('explanation','')}")
                lines.append("")

            # Short
            if shorts:
                lines.append("-" * 70)
                lines.append(f"  SECTION B: SHORT QUESTIONS")
                lines.append("-" * 70)
                for i, item in enumerate(shorts):
                    lines.append(f"\n  Q{i+1}. [{item.get('difficulty','').upper()}] [{item.get('marks',5)} Marks] {item.get('q','')}")
                    if include_answers:
                        lines.append(f"       Model Answer: {item.get('answer','')}")
                lines.append("")

            # Long
            if longs:
                lines.append("-" * 70)
                lines.append(f"  SECTION C: LONG QUESTIONS")
                lines.append("-" * 70)
                for i, item in enumerate(longs):
                    lines.append(f"\n  Q{i+1}. [{item.get('difficulty','').upper()}] [{item.get('marks',10)} Marks]")
                    lines.append(f"       {item.get('q','')}")
                    if include_answers:
                        lines.append(f"\n       Model Answer: {item.get('answer','')}")
                lines.append("")

            # Case studies
            if cases:
                lines.append("-" * 70)
                lines.append(f"  SECTION D: CASE STUDIES")
                lines.append("-" * 70)
                for i, item in enumerate(cases):
                    lines.append(f"\n  CASE STUDY {i+1}: {item.get('title','')}  [{item.get('marks',20)} Marks]")
                    lines.append(f"\n  Scenario:\n  {item.get('scenario','')}")
                    lines.append(f"\n  Questions:")
                    for j, cq in enumerate(item.get("questions",[])):
                        lines.append(f"  ({chr(97+j)}) {cq}")
                    if include_answers:
                        lines.append(f"\n  Answers:")
                        for j, ca in enumerate(item.get("answers",[])):
                            lines.append(f"  ({chr(97+j)}) {ca}")
                lines.append("")

            lines.append("=" * 70)
            lines.append(f"  Generated by AI Exam Generator — {now}")
            lines.append("=" * 70)
            return "\n".join(lines)

        st.markdown("### 💾 DOWNLOAD OPTIONS")
        dl1, dl2 = st.columns(2)
        fname_base = f"{ci.get('code','EXAM')}_{ci.get('exam_type','Paper')}_{datetime.datetime.now().strftime('%Y%m%d')}"

        with dl1:
            st.markdown("#### 📄 Student Copy")
            st.markdown('<span style="color:#4a6a8a;font-size:12px">Questions only — no answers</span>', unsafe_allow_html=True)
            student_report = build_report(include_answers=False)
            st.download_button(
                "📥 DOWNLOAD STUDENT COPY",
                data=student_report,
                file_name=f"{fname_base}_Student.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with dl2:
            st.markdown("#### 🔑 Answer Key")
            st.markdown('<span style="color:#4a6a8a;font-size:12px">Full paper with model answers</span>', unsafe_allow_html=True)
            answer_report = build_report(include_answers=True)
            st.download_button(
                "📥 DOWNLOAD ANSWER KEY",
                data=answer_report,
                file_name=f"{fname_base}_AnswerKey.txt",
                mime="text/plain",
                use_container_width=True,
            )

        st.divider()
        with st.expander("👁 Preview — Student Copy"):
            st.code(build_report(include_answers=False), language=None)
        with st.expander("👁 Preview — Answer Key"):
            st.code(build_report(include_answers=True), language=None)
