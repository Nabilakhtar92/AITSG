import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
from openai import OpenAI
from io import BytesIO
#from streamlit_drawable_canvas import st_canvas
#from PIL import Image
#import io
# Updated precise CSS to keep the 3-dot menu but hide Deploy and GitHub buttons
st.markdown(
    """
    <style>
    /* 1. Hide the "Deploy" button */
    .stDeployButton {
        display: none !important;
    }
    
    /* 2. Hide the GitHub link/icon block specifically without touching the menu */
    header [data-testid="stConnectionStatus"],
    header a[href*="github.com"],
    header button:has(svg path[d*="M12 2C6.477 2 2 6.484 2 12.017"]) {
        display: none !important;
    }

    /* 3. Alternative block to strip any extra Cloud host icons next to the menu */
    </style>
    """,
    unsafe_allow_html=True
)
# ==================================================
# APP PASSWORD
# ==================================================

APP_PASSWORD = "Scripto2026"

st.set_page_config(
    page_title="Scripto",
    page_icon="🧠",
    layout="wide"
)
# ==================================================
# Global CSS
# ==================================================
st.markdown("""
<style>

.hero-card {

    background: var(--secondary-background-color);

    border: 1px solid rgba(120,120,120,0.15);

    border-left: 5px solid #667eea;

    border-radius: 14px;

    padding: 8px 16px;

    margin-top: 10px;

    margin-bottom: 10px;

    box-shadow:
        0 3px 8px rgba(0,0,0,0.06);
}

.hero-card h1{

    margin: 0;

    font-size: 26px;

    line-height: 1.1;
}

.hero-card p{

    opacity: 0.85;

    margin-top: 2px;

    margin-bottom: 0;

    font-size: 13px;

    line-height: 1.2;
}

</style>
""", unsafe_allow_html=True)

#====================================================


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.markdown(
        """
        <div style="text-align:center;padding-top:100px;">
            <h1>🧠 Scripto</h1>
            <p>AI Test Script Generator</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    password = st.text_input(
        "Enter Team Password",
        type="password"
    )

    if st.button("Login"):

        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Password")

    st.stop()
# ==================================================
# CONFIGURATION
# ==================================================

TEMPLATE_FILE = "templates.json"

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump(
            templates,
            file,
            indent=4
        )


def load_templates():

    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as file:
            return json.load(file)

    default_templates = {
        "SAP Standard": [
            "Test Case ID",
            "Scenario",
            "Preconditions",
            "Test Steps",
            "Test Data",
            "Expected Result",
            "Actual Result",
            "Status"
        ]
    }

    save_templates(default_templates)

    return default_templates
#mdttemplates-------------------------------------

MDT_TEMPLATE_FILE = "mdt_templates.json"


def load_mdt_templates():

    if os.path.exists(MDT_TEMPLATE_FILE):
        with open(MDT_TEMPLATE_FILE,"r") as file:
            return json.load(file)

    return {}
#---------------------------------------------------
def build_prompt(columns, notes):

    fields = "\n".join(columns)

    prompt = f"""
You are a Senior SAP Techno-Functional QA Consultant with expertise in SIT, UAT, Regression Testing, Integration Testing, and SAP business process validation.

Your task is to convert the user's testing notes into a professional SAP test script.

Return ONLY valid JSON.


Fields:
{fields}

Instructions:
- Use professional and concise language.
- Use SAP terminology wherever applicable.
- Populate only the requested fields.
- Do not add fields that are not listed.
- Generate a Test Case ID in the format TC001, TC002, TC003, etc.
- Convert informal notes into clear testing documentation.
- Test Steps should be written as sequential user actions.
- Expected Results should describe the expected SAP system behavior.
- Actual Results should reflect the outcome described in the notes.
- Status should be one of: Pass, Fail, Blocked, Not Executed.
- Ensure all values are business-friendly and suitable for SIT/UAT evidence.
-If the testing notes contain multiple testing activities,create a separate test script row for each activity.

Output Requirements:
- Return valid JSON only.
- No markdown.
- No code blocks.
- No explanations.
- No introductory text.
- No trailing comments.


User Notes:
{notes}
"""

    return prompt


def clean_json_response(response_text):

    response_text = response_text.replace(
        "```json",
        ""
    )

    response_text = response_text.replace(
        "```",
        ""
    )

    return response_text.strip()


# ==================================================
# LOAD DATA
# ==================================================

templates = load_templates()
mdt_templates = load_mdt_templates()
#===================================================
#FLOATER
#===================================================
st.markdown(
    """
    <div style="
        background-color:#f0f2f6;
        color:#000000;
        padding:8px;
        border-radius:5px;
        font-weight:bold;
    ">
        <marquee>
        📢 🚀 Welcome to Scripto | SAP Consultant Productivity Suite | MDT Generator Available | Diagram Copy Feature Available | CREATED BY : NABIL AKHTAR
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <h1>🧠 Scripto</h1>
        <p>SAP Consultant's Productivity Suite</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "AI Test Script Generator",
        "Template Manager",
        "Diagram Playground",
        "MDT Generator",
        "Migration Validator"
    ]
)


st.sidebar.divider()

api_key = st.sidebar.text_input(
    "API Key",
    type="password"
)

# ==================================================
# PAGE 1 - AI TEST SCRIPT GENERATOR
# ==================================================
 
if page == "AI Test Script Generator":
 
    st.markdown("""
<div class="hero-card">

<h1>🚀 AI Test Script Generator</h1>

<p>
Generate professional SAP SIT, UAT and
Regression test scripts using AI in seconds.
</p>

</div>
""", unsafe_allow_html=True)
 
    col1, col2 = st.columns([2, 1])
 
    with col1:
 
        selected_template = st.selectbox(
            "Select Template",
            list(templates.keys())
        )
 
    with col2:
 
        selected_model = st.selectbox(
            "Select Model",
            [
                # Gemini
                "gemini-3.5-flash",
                "gemini-2.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.5-flash",
 
                # OpenAI
                "gpt-5",
                "gpt-5-mini",
                "gpt-4o",
                "gpt-4o-mini"
            ]
        )
 
    test_notes = st.text_area(
        "Describe what you tested",
        height=250
    )
 
    selected_columns = templates[selected_template]
 
    st.subheader("Template Preview")
 
    empty_df = pd.DataFrame(
        {
            col: [""]
            for col in selected_columns
        }
    )
 
    st.data_editor(
        empty_df,
        use_container_width=True,
        num_rows="dynamic",
        key="template_preview_editor"
    )
 
    if st.button("Generate Test Script"):
 
        if not api_key:
 
            st.error("Please enter an API Key.")
 
        elif not test_notes.strip():
 
            st.error("Please enter testing notes.")
 
        else:
 
            ai_response = None
 
            try:
 
                prompt = build_prompt(
                    selected_columns,
                    test_notes
                )
 
                with st.spinner(f"Generating using {selected_model}..."):
 
                    # ==========================
                    # GEMINI
                    # ==========================
 
                    if selected_model.startswith("gemini"):
 
                        genai.configure(api_key=api_key)
 
                        model = genai.GenerativeModel(selected_model)
 
                        response = model.generate_content(prompt)
 
                        ai_response = response.text
 
                    # ==========================
                    # OPENAI
                    # ==========================
 
                    else:
 
                        client = OpenAI(api_key=api_key)
 
                        response = client.chat.completions.create(
                            model=selected_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )
 
                        ai_response = response.choices[0].message.content
 
                    cleaned_response = clean_json_response(ai_response)
 
                    json_data = json.loads(cleaned_response)
 
                    # ==========================
                    # SINGLE OBJECT RESPONSE
                    # ==========================
 
                    if isinstance(json_data, dict):
 
                        generated_row = {}
 
                        for column in selected_columns:
 
                            generated_row[column] = json_data.get(column, "")
 
                        generated_df = pd.DataFrame([generated_row])
 
                    # ==========================
                    # MULTIPLE ROW RESPONSE
                    # ==========================
 
                    elif isinstance(json_data, list):
 
                        generated_df = pd.DataFrame(json_data)
 
                    else:
 
                        st.error("Unsupported JSON format returned by model.")
 
                        st.stop()
 
                    # Ensure column order
                    generated_df = generated_df.reindex(
                        columns=selected_columns,
                        fill_value=""
                    )
 
                    # Prevent dtype drift (None/NaN -> mixed-type columns)
                    generated_df = generated_df.fillna("").astype(str)
 
                    # Give it a clean, stable index before it touches the editor
                    generated_df = generated_df.reset_index(drop=True)
 
                    # Save in session
                    st.session_state.generated_df = generated_df
 
                st.success(f"Generation completed using {selected_model}")
 
            except json.JSONDecodeError:
 
                st.error("The model did not return valid JSON.")
 
                if ai_response is not None:
 
                    with st.expander("Raw Model Response"):
 
                        st.code(ai_response)
 
            except Exception as e:
 
                st.error(f"Error: {str(e)}")
 
    # ==========================================
    # GENERATED TEST SCRIPT
    # ==========================================
 
    if "generated_df" in st.session_state:
 
        st.subheader("Generated Test Script")
 
        # IMPORTANT: pass session_state.generated_df in as `data` ONLY.
        # Do NOT reassign the widget's return value back into
        # st.session_state.generated_df on every rerun — that feedback
        # loop is what caused edits/new rows to reset after 1-2 cells.
        # st.data_editor already tracks and persists its own state
        # internally via key="generated_editor".
        st.data_editor(
            st.session_state.generated_df,
            use_container_width=True,
            num_rows="dynamic",
            key="generated_editor"
        )
# ==================================================
# PAGE 2 - TEMPLATE MANAGER
# ==================================================

elif page == "Template Manager":

    st.markdown("""
<div class="hero-card">

<h1>📋 Template Manager</h1>

<p>
Create, customize and manage reusable testing
templates tailored to your SAP project needs.
</p>

</div>
""", unsafe_allow_html=True)

    if "working_columns" not in st.session_state:
        st.session_state.working_columns = []

    st.subheader("Create / Edit Template")

    template_name = st.text_input(
        "Template Name",
        placeholder="Example: Demand Planning SIT"
    )

    new_column = st.text_input(
        "New Column Name"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Add Column"):

            if new_column.strip():

                st.session_state.working_columns.append(
                    new_column.strip()
                )

    with col2:

        if st.button("Clear All Columns"):

            st.session_state.working_columns = []

            st.rerun()

    st.divider()

    st.subheader("Template Preview")

    if st.session_state.working_columns:

        preview_df = pd.DataFrame(
            {
                col: [""]
                for col in st.session_state.working_columns
            }
        )

        st.data_editor(
            preview_df,
            use_container_width=True,
            num_rows="dynamic"
        )

    else:

        st.info(
            "Add columns to preview your template."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Save Template"):

            if not template_name.strip():

                st.error(
                    "Please enter a template name."
                )

            elif not st.session_state.working_columns:

                st.error(
                    "Please add at least one column."
                )

            else:

                templates[
                    template_name.strip()
                ] = st.session_state.working_columns.copy()

                save_templates(
                    templates
                )

                st.success(
                    "Template saved successfully."
                )

                st.rerun()

    with col2:

        if st.button(
            "Load Existing Template"
        ):

            if template_name in templates:

                st.session_state.working_columns = (
                    templates[
                        template_name
                    ].copy()
                )

                st.success(
                    "Template loaded."
                )

                st.rerun()

            else:

                st.error(
                    "Template not found."
                )

    st.divider()

    st.subheader("Existing Templates")

    selected_delete_template = st.selectbox(
        "Templates",
        list(templates.keys())
    )

    if st.button(
        "Delete Selected Template"
    ):

        if selected_delete_template == "SAP Standard":

            st.warning(
                "SAP Standard template cannot be deleted."
            )

        else:

            del templates[
                selected_delete_template
            ]

            save_templates(
                templates
            )

            st.success(
                "Template deleted."
            )

            st.rerun()
# ==================================================
# PAGE 3 - DIAGRAM PLAYGROUND
# ==================================================

elif page == "Diagram Playground":

    import textwrap
    import streamlit as st
    import streamlit.components.v1 as components

    st.markdown("""
<div class="hero-card">

<h1>📊 Diagram Playground</h1>

<p>
Build SAP process flows, data flows and solution
diagrams visually with Mermaid based diagramming.
</p>

</div>
""", unsafe_allow_html=True)

    flow_text = st.text_area(
        "Flow Steps",
        height=250,
        placeholder="""Start
Put values in ACTUALS QTY
COPY OPERATOR: ACTUALS QTY TO ACTUALS QTY ADJ
Run Forecast
Review Results
End"""
    )

    if st.button("Generate Diagram"):

        if not flow_text.strip():

            st.error(
                "Please enter at least one step."
            )

        else:

            steps = [
                step.strip()
                for step in flow_text.split("\n")
                if step.strip()
            ]

            row_size = 6

            mermaid_code = """
%%{init: {
    "theme":"default",
    "flowchart":{
        "htmlLabels":true,
        "nodeSpacing":20,
        "rankSpacing":40
    }
}}%%
flowchart TB
"""

            # Create Nodes
            for i, step in enumerate(steps):

                wrapped_step = "<br/>".join(
                    textwrap.wrap(
                        step,
                        width=18,
                        break_long_words=False
                    )
                )

                mermaid_code += (
                    f'N{i}["{wrapped_step}"]\n'
                )

            # Create Rows (6 Nodes Per Row)
            for row_start in range(
                0,
                len(steps),
                row_size
            ):

                row_end = min(
                    row_start + row_size,
                    len(steps)
                )

                mermaid_code += (
                    f'\nsubgraph R{row_start}[" "]\n'
                )

                mermaid_code += (
                    "direction LR\n"
                )

                for i in range(
                    row_start,
                    row_end - 1
                ):

                    mermaid_code += (
                        f"N{i} --> N{i+1}\n"
                    )

                mermaid_code += "end\n"

                mermaid_code += (
                    f"style R{row_start} fill:none,stroke:none\n"
                )

                # Connect row to next row
                if row_end < len(steps):

                    mermaid_code += (
                        f"N{row_end-1} --> N{row_end}\n"
                    )

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import mermaid from
        'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

        mermaid.initialize({{
            startOnLoad: true,
            theme: "default"
        }});

        window.copyDiagram = async function() {{

            const svg = document.querySelector("svg");

            if (!svg) {{
                alert("Diagram not ready.");
                return;
            }}

            const svgData =
                new XMLSerializer()
                .serializeToString(svg);

            const canvas =
                document.createElement("canvas");

            const bbox =
                svg.getBBox();

            canvas.width =
                bbox.width + 50;

            canvas.height =
                bbox.height + 50;

            const ctx =
                canvas.getContext("2d");

            const img =
                new Image();

            img.onload = async function() {{

                ctx.fillStyle = "white";

                ctx.fillRect(
                    0,
                    0,
                    canvas.width,
                    canvas.height
                );

                ctx.drawImage(
                    img,
                    25,
                    25
                );

                canvas.toBlob(
                    async (blob) => {{

                        try {{

                            await navigator.clipboard.write([
                                new ClipboardItem({{
                                    "image/png": blob
                                }})
                            ]);

                            alert(
                                "Diagram copied. Paste into PowerPoint or Word."
                            );

                        }} catch (err) {{

                            alert(
                                "Clipboard copy failed in this browser."
                            );
                        }}
                    }},
                    "image/png"
                );
            }};

            img.src =
                "data:image/svg+xml;base64," +
                btoa(
                    unescape(
                        encodeURIComponent(
                            svgData
                        )
                    )
                );
        }};
    </script>
</head>

<body>

    <div style="margin-bottom:15px;">

        <button
            onclick="copyDiagram()"
            style="
                padding:8px 12px;
                cursor:pointer;
            "
        >
            Copy Diagram
        </button>

    </div>

    <div class="mermaid">
{mermaid_code}
    </div>

</body>
</html>
"""

            components.html(
                html,
                height=800,
                scrolling=True
            )

            st.caption(
                f"Steps: {len(steps)}"
            )

            with st.expander(
                "Show Mermaid Code"
            ):

                st.code(
                    mermaid_code,
                    language="text"
                )
# ==================================================
# PAGE 4 - MDT GENERATOR
# ==================================================

elif page == "MDT Generator":

    st.markdown("""
<div class="hero-card">

<h1>🏗 MDT Generator</h1>

<p>
Generate SAP master data templates and automatically
populate mandatory fields using AI driven business
requirements.
</p>

</div>
""", unsafe_allow_html=True)

    selected_model = st.selectbox(
        "Select Model",
        [
            "gemini-3.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.5-flash",
            "gpt-5",
            "gpt-5-mini",
            "gpt-4o",
            "gpt-4o-mini"
        ],
        key="mdt_model"
    )

    selected_mdts = st.multiselect(
        "Select MDTs",
        list(mdt_templates.keys())
    )

    requirement = st.text_area(
        "Business Requirement",
        height=250,
        placeholder="""
Create:

Finished Product:
CHOCOLATE_BAR

Raw Materials:
COCOA
SUGAR

Locations:
PLANT1000
DC1000

Country:
India
"""
    )

    if st.button(
        "Generate MDT Values"
    ):

        if not api_key:

            st.error(
                "Please enter API Key."
            )

        elif not selected_mdts:

            st.error(
                "Select at least one MDT."
            )

        elif not requirement.strip():

            st.error(
                "Enter business requirement."
            )

        else:

            try:

                template_text = ""

                for mdt in selected_mdts:

                    template_text += (
                        f"\n{mdt}\n"
                    )

                    for attribute in (
                        mdt_templates[mdt]
                    ):

                        template_text += (
                            f"- {attribute}\n"
                        )

                prompt = f"""
You are an SAP IBP Master Data Consultant and SAP Data Migration Expert.

Your task is to generate SAP Master Data values based on the user's business requirement.

Return ONLY valid JSON.

Generate values ONLY for the selected Master Data Types (MDTs).

{template_text}

Rules

- Use EXACT attribute names from the provided MDT templates.
- Do NOT create, remove, rename, or modify any attributes.
- Every attribute from the MDT template must appear in the output JSON in the exact order provided.
- Populate ALL attributes marked with "*" (mandatory attributes).
- For attributes without "*", leave the value blank ("") unless the user explicitly provides a value for that attribute.
- If the user explicitly provides a value for a non-mandatory attribute, populate it.
- Never omit an attribute from the output.
- Do NOT guess values for optional attributes.
- Generate multiple records when appropriate.
- Generate realistic SAP business values.
- Do NOT populate audit fields such as Changed By, Changed On, Created By, Created On unless explicitly requested.
- Ensure IDs and cross-references are consistent across MDTs.
- Return ONLY valid JSON.
- No markdown.
- No code blocks.
- No explanations.
- No comments.


Business Requirement

{requirement}
"""

                if selected_model.startswith(
                    "gemini"
                ):

                    genai.configure(
                        api_key=api_key
                    )

                    model = genai.GenerativeModel(
                        selected_model
                    )

                    response = (
                        model.generate_content(
                            prompt
                        )
                    )

                    ai_response = (
                        response.text
                    )

                else:

                    client = OpenAI(
                        api_key=api_key
                    )

                    response = (
                        client.chat.completions.create(
                            model=selected_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )
                    )

                    ai_response = (
                        response
                        .choices[0]
                        .message
                        .content
                    )

                cleaned_response = (
                    clean_json_response(
                        ai_response
                    )
                )

                md_data = json.loads(
                    cleaned_response
                )

                rows = []

                max_cols = 200

                for mdt_name, records in (
                    md_data.items()
                ):

                    if not records:
                        continue

                    # MDT NAME ROW

                    mdt_row = (
                        [""] * max_cols
                    )

                    mdt_row[0] = mdt_name

                    rows.append(
                        mdt_row
                    )

                    # ATTRIBUTE ROW

                    attributes = list(
                        records[0].keys()
                    )

                    attr_row = (
                        [""] * max_cols
                    )

                    for i, attr in enumerate(
                        attributes
                    ):

                        attr_row[
                            i + 1
                        ] = attr

                    rows.append(
                        attr_row
                    )

                    # VALUE ROWS

                    for record in records:

                        value_row = (
                            [""] * max_cols
                        )

                        for i, attr in enumerate(
                            attributes
                        ):

                            value_row[
                                i + 1
                            ] = str(
                                record.get(
                                    attr,
                                    ""
                                )
                            )

                        rows.append(
                            value_row
                        )

                    rows.append(
                        [""] * max_cols
                    )

                st.session_state[
                    "mdt_output"
                ] = pd.DataFrame(
                    rows,
                    columns=[
                        f"Column {i}"
                        for i in range(
                            1,
                            max_cols + 1
                        )
                    ]
                )

                st.success(
                    "MDT Values Generated"
                )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

    if "mdt_output" in st.session_state:

        st.subheader(
            "Generated MDT Sheet"
        )

        st.data_editor(
            st.session_state[
                "mdt_output"
            ],
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
# ==================================================
# PAGE 5 - MIGRATION VALIDATOR
# ==================================================

elif page == "Migration Validator":

    # A page is like a room in this app. Everything below belongs to Page 5.
    # base64 safely packs table text for the browser's Copy button.
    import hashlib
    import base64
    import streamlit.components.v1 as components



    st.markdown("""
    <div class="hero-card">
        <h1>Migration Validator</h1>
        <p>Validate SAP data migration by comparing preload and postload Excel files,
        identifying missing records, reviewing column differences, and exporting a clear audit report.</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("UPLOAD FILES  →  CHOOSE SHEETS  →  MAP HEADERS  →  SELECT KEYS  →  REVIEW & EXPORT")
    st.markdown("### 1. Upload migration files")
    upload_left, upload_right = st.columns(2, gap="large")
    with upload_left:
        preload_file = st.file_uploader(
            "Preload / source Excel file", type=["xlsx"], key="validator_preload",
            help="Upload the source data before migration."
        )
    with upload_right:
        postload_file = st.file_uploader(
            "Postload / target Excel file", type=["xlsx"], key="validator_postload",
            help="Upload the target data after migration."
        )

    def render_copyable_preview(title, dataframe, copy_key, help_text=None, height=320,show_table=True):
        """Render a table preview with a button to copy the full table as tab-separated text."""
        st.markdown(f"#### {title}")
        if help_text:
            st.caption(help_text)
        st.caption(f"{len(dataframe):,} rows · {len(dataframe.columns):,} columns")
        st.caption(f"{len(dataframe):,} rows · {len(dataframe.columns):,} columns")

        if show_table:
            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True,
                height=height
            )

        # Base64 keeps arbitrary cell values from breaking the HTML/JavaScript payload.
        tabular_text = dataframe.to_csv(index=False, sep="\t", lineterminator="\n")
        encoded_text = base64.b64encode(tabular_text.encode("utf-8")).decode("ascii")
        html = f"""
        <div style="font-family: sans-serif; display:flex; align-items:center; gap:10px;">
          <button id="copy-{copy_key}" style="
            background:#1f6feb; color:white; border:0; border-radius:8px;
            padding:9px 14px; font-size:13px; font-weight:600; cursor:pointer;">
            Copy table to clipboard
          </button>
          <span id="status-{copy_key}" style="font-size:12px;color:#64748b;">
            Paste directly into Excel or Google Sheets
          </span>
        </div>
        <script>
          const encoded = "{encoded_text}";
          const decodeTable = () => decodeURIComponent(escape(atob(encoded)));
          const button = document.getElementById("copy-{copy_key}");
          const status = document.getElementById("status-{copy_key}");
          button.addEventListener("click", async () => {{
            const text = decodeTable();
            try {{
              if (navigator.clipboard && window.isSecureContext) {{
                await navigator.clipboard.writeText(text);
              }} else {{
                const area = document.createElement("textarea");
                area.value = text;
                area.style.position = "fixed";
                area.style.left = "-9999px";
                document.body.appendChild(area);
                area.focus(); area.select();
                const ok = document.execCommand("copy");
                area.remove();
                if (!ok) throw new Error("Clipboard copy was blocked");
              }}
              status.textContent = "Copied — paste into Excel with Ctrl+V";
              status.style.color = "#15803d";
            }} catch (error) {{
              status.textContent = "Clipboard access was blocked by the browser";
              status.style.color = "#b91c1c";
            }}
          }});
        </script>
        """
        components.html(html, height=48, scrolling=False)

    if preload_file and postload_file:
        try:
            preload_excel = pd.ExcelFile(preload_file)
            postload_excel = pd.ExcelFile(postload_file)
        except Exception as exc:
            st.error(f"Unable to read the uploaded Excel file: {exc}")
            st.stop()

        st.markdown("### 2. Choose worksheets")
        sheet_left, sheet_right = st.columns(2, gap="large")
        with sheet_left:
            preload_sheet = st.selectbox(
                "Preload worksheet", preload_excel.sheet_names,
                key="validator_preload_sheet"
            )
        with sheet_right:
            postload_sheet = st.selectbox(
                "Postload worksheet", postload_excel.sheet_names,
                key="validator_postload_sheet"
            )

        try:
            preload_df = pd.read_excel(preload_file, sheet_name=preload_sheet)
            postload_df = pd.read_excel(postload_file, sheet_name=postload_sheet)
        except Exception as exc:
            st.error(f"Unable to load the selected worksheets: {exc}")
            st.stop()

        preload_df.columns = preload_df.columns.astype(str).str.strip()
        postload_df.columns = postload_df.columns.astype(str).str.strip()

        # Duplicate column names make field-level matching ambiguous, so stop with a clear message.
        if preload_df.columns.duplicated().any() or postload_df.columns.duplicated().any():
            st.error("One of the selected worksheets contains duplicate column names. Rename duplicate columns in Excel and upload again.")
            st.stop()
        if preload_df.empty and postload_df.empty:
            st.warning("Both selected worksheets are empty. Choose worksheets containing data to compare.")
            st.stop()

        # Keep the original tables, like keeping the original pages of a book.
        # We give columns temporary nicknames for matching, never change cells.
        original_preload_df = preload_df.copy()
        original_postload_df = postload_df.copy()

        st.markdown("### 3. Map column headers")
        st.caption("Choose which target column means the same thing as each source column. Exact names are paired automatically. Cell values are never changed.")

        # This fingerprint gives each pair of files its own saved dropdown choices.
        # Switching files or sheets cannot accidentally reuse an old mapping.
        mapping_scope = hashlib.sha256(
            preload_file.getvalue() + postload_file.getvalue()
            + repr((preload_sheet, postload_sheet, list(preload_df.columns),
                    list(postload_df.columns))).encode()
        ).hexdigest()[:20]
        header_mapping = {}
        mapping_rows = []
        with st.expander("Match source columns to target columns", expanded=True):
            for position, source_header in enumerate(preload_df.columns):
                # None means this source column has no partner in the target file.
                options = [None] + list(postload_df.columns)
                default = options.index(source_header) if source_header in postload_df.columns else 0
                target_header = st.selectbox(
                    f"Source: {source_header}", options, index=default,
                    format_func=lambda value: "Unmapped" if value is None else str(value),
                    key=f"validator_mapping_{mapping_scope}_{position}"
                )
                if target_header is not None:
                    header_mapping[source_header] = target_header
                mapping_rows.append({"Preload header": source_header,
                                     "Postload header": target_header if target_header is not None else "",
                                     "Mapping": "Mapped" if target_header is not None else "Unmapped"})
        mapping_df = pd.DataFrame(mapping_rows)
        if len(set(header_mapping.values())) != len(header_mapping):
            st.error("Each target column can have only one source partner. Remove the duplicate mapping to continue.")
            st.stop()
        st.caption(f"{len(header_mapping)} mapped pairs · {len(preload_df.columns) - len(header_mapping)} unmapped source columns")

        # Give every mapped pair one unique internal name. Unmapped columns get
        # different names so they cannot be matched just because names look alike.
        # Unique names also make swaps (A → B and B → A) safe.
        source_names = {column: f"field_{i}" for i, column in enumerate(preload_df.columns)}
        target_names = {column: f"target_{i}" for i, column in enumerate(postload_df.columns)}
        for source_header, target_header in header_mapping.items():
            target_names[target_header] = source_names[source_header]
        preload_df = preload_df.rename(columns=source_names)
        postload_df = postload_df.rename(columns=target_names)
        source_labels = {name: column for column, name in source_names.items()}
        target_labels = {name: column for column, name in target_names.items()}

        preload_headers = set(preload_df.columns)
        postload_headers = set(postload_df.columns)
        common_headers = sorted(preload_headers & postload_headers)
        preload_only = sorted(preload_headers - postload_headers)
        postload_only = sorted(postload_headers - preload_headers)

        st.markdown("### 4. Source and target overview")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Preload rows", f"{len(preload_df):,}")
        metric_cols[1].metric("Postload rows", f"{len(postload_df):,}")
        metric_cols[2].metric("Shared columns", f"{len(common_headers):,}")
        metric_cols[3].metric("Different column names", f"{len(preload_only) + len(postload_only):,}")

        header_analysis_df = pd.DataFrame({
            "Shared columns": pd.Series([f"{source_labels[c]} ↔ {target_labels[c]}" for c in common_headers], dtype="object"),
            "Only in Preload": pd.Series([source_labels[c] for c in preload_only], dtype="object"),
            "Only in Postload": pd.Series([target_labels[c] for c in postload_only], dtype="object"),
        })
        with st.expander("Review column / header analysis", expanded=False):
            render_copyable_preview(
                "Column analysis preview", header_analysis_df, "header-analysis",
                "Copy this preview to share the column-level differences. ", height=240
            )

        st.markdown("### 5. Select record keys")
        st.caption("Choose the column or combination of columns that uniquely identifies a record in both files.")
        primary_keys = st.multiselect(
            "Primary key column(s)", common_headers,
            format_func=lambda c: f"{source_labels[c]} ↔ {target_labels[c]}",
            key=f"validator_primary_keys_{mapping_scope}_{hashlib.sha256(repr(sorted(header_mapping.items())).encode()).hexdigest()[:12]}",
            placeholder="Select one or more shared columns"
        )
        if not primary_keys:
            st.info("Select at least one primary key column to run the record comparison.")
            st.stop()

        # Compare on stable composite keys without adding helper columns to the user-facing data.
        preload_compare = preload_df.copy()
        postload_compare = postload_df.copy()
        preload_compare["_VALIDATOR_KEY"] = preload_compare[primary_keys].astype("string").fillna("<NULL>").agg("\x1f".join, axis=1)
        postload_compare["_VALIDATOR_KEY"] = postload_compare[primary_keys].astype("string").fillna("<NULL>").agg("\x1f".join, axis=1)

        preload_key_set = set(preload_compare["_VALIDATOR_KEY"])
        postload_key_set = set(postload_compare["_VALIDATOR_KEY"])
        missing_postload_keys = preload_key_set - postload_key_set
        missing_preload_keys = postload_key_set - preload_key_set
        matched_keys = preload_key_set & postload_key_set

        missing_in_postload = preload_compare.loc[
            preload_compare["_VALIDATOR_KEY"].isin(missing_postload_keys)
        ].drop(columns=["_VALIDATOR_KEY"])
        missing_in_preload = postload_compare.loc[
            postload_compare["_VALIDATOR_KEY"].isin(missing_preload_keys)
        ].drop(columns=["_VALIDATOR_KEY"])

        # Consolidated view: align source and target fields by the selected primary key(s).
        consolidated_df = pd.merge(
            preload_df, postload_df, on=primary_keys, how="outer",
            suffixes=("_Preload", "_Postload"), indicator="_Record_Status"
        )
        consolidated_df["_Record_Status"] = consolidated_df["_Record_Status"].map({
            "both": "Present in both", "left_only": "Missing in Postload",
            "right_only": "Missing in Preload"
        })

        # Count duplicate composite keys to help users assess whether their selected keys are unique.
        preload_duplicate_rows = int(preload_compare["_VALIDATOR_KEY"].duplicated(keep=False).sum())
        postload_duplicate_rows = int(postload_compare["_VALIDATOR_KEY"].duplicated(keep=False).sum())
        if preload_duplicate_rows or postload_duplicate_rows:
            st.warning(
                f"Duplicate key rows detected — Preload: {preload_duplicate_rows:,}; "
                f"Postload: {postload_duplicate_rows:,}. Check that the selected columns uniquely identify records."
            )

        # Put the real headers back on missing-record tables before showing them.
        missing_in_postload = missing_in_postload.rename(columns=source_labels)
        missing_in_preload = missing_in_preload.rename(columns=target_labels)

        st.markdown("### 6. Validation results")
        result_cols = st.columns(4)
        result_cols[0].metric("Matched key values", f"{len(matched_keys):,}")
        result_cols[1].metric("Missing in Postload", f"{len(missing_in_postload):,}")
        result_cols[2].metric("Missing in Preload", f"{len(missing_in_preload):,}")
        result_cols[3].metric("Consolidated rows", f"{len(consolidated_df):,}")

        tab_postload, tab_preload, tab_consolidated = st.tabs([
            "Missing in Postload", "Missing in Preload", "Consolidated View"
        ])
        with tab_postload:
            st.caption("Source records whose selected primary key was not found in the target file.")
            render_copyable_preview(
                "Missing in Postload preview", missing_in_postload, "missing-postload",
                "Every displayed row can be copied as tab-separated values.", height=360
            )
        with tab_preload:
            st.caption("Target records whose selected primary key was not found in the source file.")
            render_copyable_preview(
                "Missing in Preload preview", missing_in_preload, "missing-preload",
                "Every displayed row can be copied as tab-separated values.", height=360
            )
        with tab_consolidated:
            st.caption(
                "Blue = Preload (File 1) · Green = Postload (File 2) · "
                "Grey = common primary key. Column labels also identify each source."
            )

            # Build an easy-to-read preview with explicit source labels.
            # The original consolidated_df remains unchanged for comparison logic.
            consolidated_display_df = consolidated_df.copy()
            preload_display_columns = []
            postload_display_columns = []
            key_display_columns = []
            display_rename_map = {}

            for column in preload_df.columns:
                if column in primary_keys:
                    display_rename_map[column] = f"🔑 {source_labels[column]} ↔ {target_labels[column]} | Common Key"
                    key_display_columns.append(display_rename_map[column])
                elif column in postload_df.columns:
                    display_rename_map[f"{column}_Preload"] = f"{source_labels[column]} | Preload"
                    preload_display_columns.append(display_rename_map[f"{column}_Preload"])
                else:
                    display_rename_map[column] = f"{source_labels[column]} | Preload"
                    preload_display_columns.append(display_rename_map[column])

            for column in postload_df.columns:
                if column in primary_keys:
                    continue
                if column in preload_df.columns:
                    display_rename_map[f"{column}_Postload"] = f"{target_labels[column]} | Postload"
                    postload_display_columns.append(display_rename_map[f"{column}_Postload"])
                else:
                    display_rename_map[column] = f"{target_labels[column]} | Postload"
                    postload_display_columns.append(display_rename_map[column])

            consolidated_display_df = consolidated_display_df.rename(columns=display_rename_map)

            def shade_consolidated_columns(data):
                styles = pd.DataFrame("", index=data.index, columns=data.columns)
                for column in preload_display_columns:
                    if column in styles.columns:
                        styles[column] = "background-color: #E8F2FF; color: #17365D;"
                for column in postload_display_columns:
                    if column in styles.columns:
                        styles[column] = "background-color: #E8F5E9; color: #1B5E20;"
                for column in key_display_columns:
                    if column in styles.columns:
                        styles[column] = "background-color: #E5E7EB; color: #111827; font-weight: bold;"
                return styles

            st.markdown("**Consolidated comparison preview**")
            st.caption(
                f"{len(consolidated_display_df):,} rows · "
                f"{len(consolidated_display_df.columns):,} columns"
            )
            # Colour shows which file each column came from; it does not change data.
            # Some installations do not include the optional table-colouring package.
            # In that case, show the same table without colours so work can continue.
            try:
                total_cells = (
                    len(consolidated_display_df)
                    * len(consolidated_display_df.columns)
                )

                if total_cells < 250000:

                    comparison_preview = (
                        consolidated_display_df.style.apply(
                            shade_consolidated_columns,
                            axis=None
                        )
                    )

                else:

                    comparison_preview = consolidated_display_df

                    st.warning(
                        f"Large dataset detected "
                        f"({total_cells:,} cells). "
                        f"Styling disabled for performance."
                    )

            except ImportError:
                comparison_preview = consolidated_display_df
            st.dataframe(
                comparison_preview,
                use_container_width=True,
                height=420
            )
            render_copyable_preview(
                "",
                consolidated_display_df,
                "consolidated-view",
                "The copied table includes the source labels in its column headers.",
                height=420,
                show_table=False
            )

        st.markdown("### 7. Export validation report")
        st.caption("The Excel report contains a summary, header mapping, column analysis, both missing-record lists, and the consolidated view. Common-records output is intentionally omitted.")

        # Build an Excel workbook in memory, like assembling pages in a folder.
        # Each worksheet holds a different part of the same validation report.
        def create_validation_report():
            output = BytesIO()
            summary_df = pd.DataFrame({
                "Metric": [
                    "Preload rows", "Postload rows", "Shared columns",
                    "Only in Preload columns", "Only in Postload columns",
                    "Matched key values", "Missing in Postload rows",
                    "Missing in Preload rows", "Preload duplicate-key rows",
                    "Postload duplicate-key rows"
                ],
                "Value": [
                    len(preload_df), len(postload_df), len(common_headers),
                    len(preload_only), len(postload_only), len(matched_keys),
                    len(missing_in_postload), len(missing_in_preload),
                    preload_duplicate_rows, postload_duplicate_rows
                ]
            })
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                header_analysis_df.to_excel(writer, sheet_name="Header Analysis", index=False)
                missing_in_postload.to_excel(writer, sheet_name="Missing in Postload", index=False)
                missing_in_preload.to_excel(writer, sheet_name="Missing in Preload", index=False)
                # The exported table uses readable original headers, not temporary names.
                consolidated_display_df.to_excel(writer, sheet_name="Consolidated View", index=False)
                mapping_df.to_excel(writer, sheet_name="Header Mapping", index=False)
                # Make report sheets easier to review in Excel.
                for worksheet in writer.sheets.values():
                    worksheet.freeze_panes = "A2"
                    worksheet.auto_filter.ref = worksheet.dimensions
                    for column_cells in worksheet.columns:
                        max_length = max(
                            (len(str(cell.value)) if cell.value is not None else 0)
                            for cell in column_cells
                        )
                        worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 42)
            output.seek(0)
            return output

        report_file = create_validation_report()
        st.download_button(
            label="Download Excel validation report",
            data=report_file,
            file_name="Migration_Validation_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
            key="validator_download_report"
        )
    else:
        st.info("Upload both the preload and postload Excel files to begin validation.")
