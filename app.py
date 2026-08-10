import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
from openai import OpenAI
#from streamlit_drawable_canvas import st_canvas
#from PIL import Image
#import io
# ==================================================
# APP PASSWORD
# ==================================================

APP_PASSWORD = "Scripto2026"

st.set_page_config(
    page_title="Scripto",
    page_icon="🧠",
    layout="wide"
)

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
        📢 Welcome to Scripto | Use your own API Key | New Diagram Copy Feature Available | Built for SAP Consultants | CREATED BY : NABIL AKHTAR
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "AI Test Script Generator",
        "Template Manager",
        "Diagram Playground"
    ]
)

st.sidebar.divider()

st.sidebar.header("About Scripto")

st.sidebar.write(
    """
AI Test Script Generator helps SAP
Techno-Functional Consultants create
professional test scripts using AI.
"""
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
 
    st.title("AI Test Script Generator")
 
    st.write(
        """
        Select a template, choose a model,
        enter testing notes, generate a
        professional SAP test script,
        review and edit it as required.
        """
    )
 
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

    st.title("Template Manager")

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

    st.title("Diagram Playground")

    st.write(
        """
        Create process flows and data flow diagrams manually.
        Enter one step per line and generate a flow diagram.
        """
    )

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