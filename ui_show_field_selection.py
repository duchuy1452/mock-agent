import streamlit as st
import os
import json
import argparse
from dotenv import load_dotenv
from schema_loader import load_schema
from orchestrator import continue_pipeline_after_hitl
from utils.log_helper import append_log

def render_field_selection_ui(slide_num):
    # Load environment variables
    load_dotenv()

    st.markdown(f"### Field Selection for Slide {slide_num}")

    # Construct paths
    output_path = os.getenv("OUTPUT_JSON_PATH")
    row_logic_path = os.path.join(output_path, f"row_logic_output_revised_{slide_num}.json")
    agg_metric_path = os.path.join(output_path, f"aggregated_totals_metric_fields_{slide_num}.json")
    schema_path = os.getenv("SCHEMA_PATH")
    slide_path = os.path.join(os.getenv("TMP_MEDIA"), f"slide_{slide_num}.png")

    # Load files
    row_logic = json.load(open(row_logic_path))
    # aggregated_totals = json.load(open(agg_metric_path))
    field_defs = load_schema(schema_path)
    field_list = list(field_defs.keys())

    # Build lookup
    # agg_dict = {entry["total_row"]: entry for entry in aggregated_totals}
    row_dict = {entry["row_label"]: entry for entry in row_logic}
    
    # Load llm_slide_reader_output
    slide_json_path = os.path.join(output_path, f"llm_slide_reader_output_{slide_num}.json")
    with open(slide_json_path, "r") as f:
        slide_json = json.load(f)

    llm_rows = slide_json["tables"][0]["rows"]
    
    # Create a lookup: row_label -> if_total_what_row_labels
    total_mapping = {
        row["cells"][0]: row.get("if_total_what_row_labels", [])
        for row in llm_rows
        if row.get("is_aggregate", False)
    }
        
    # Show the image
    # st.image(slide_path, caption=f"Slide {slide_num}", use_container_width=True)
    st.markdown("### 🛠️ Validate Field Mapping")

    results = []

    for row_label, row_data in row_dict.items():
        st.markdown(f"#### {row_label}")

        # component_rows = agg_dict.get(row_label, {}).get("component_rows", [])
        component_rows = total_mapping.get(row_label, [])
        # metric_fields = agg_dict.get(row_label, {}).get("metric_fields", row_data.get("metric_fields", []))
        metric_fields = row_data.get("metric_fields", [])

        col1, col2 = st.columns([3, 3])

        with col1:
            st.markdown("**Aggregate of rows**", unsafe_allow_html=True)
            st.caption("Logic used by the LLM to aggregate rows")
            # st.text_area("", "\n".join(component_rows), disabled=True, height=90, key=f"agg_{slide_num}_{row_label}")
            selected_component_rows = st.multiselect(
                "Select aggregate fields",
                options=list(row_dict.keys()),
                default=component_rows,
                key=f"agg_multiselect_{slide_num}_{row_label}"
            )

        with col2:
            st.markdown("**Metric field(s)**", unsafe_allow_html=True)
            st.caption("List of field(s) selected by LLM")
            # st.text_area("", ", ".join(metric_fields), disabled=True, height=90, key=f"metric_{slide_num}_{row_label}")
            selected_metric_fields = st.multiselect(
                "Select metric fields",
                options=field_list,
                default=metric_fields,
                key=f"metric_multiselect_{slide_num}_{row_label}"
            )

        # content = "\n".join(metric_fields)
        # num_lines = content.count("\n") + 1 if content.strip() else 1
        # dynamic_height = min(250, max(68, num_lines * 20))

        # with col3:
        #     st.markdown("**Override?**", unsafe_allow_html=True)
        #     # st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True) 
        #     # st.markdown(f"<div style='height: {int((dynamic_height - 20) / 2)}px'></div>", unsafe_allow_html=True)
        #     st.caption("Select this to override")
        #         # Use inner columns to centre
        #     # left_pad, cb_col, right_pad = st.columns([1, 1, 1])
        #     # with cb_col:
        #     print(f"Rendering: ok_{slide_num}_{row_label}, metric_{slide_num}_{row_label}")
        #     is_ok = st.checkbox("", key=f"ok_{slide_num}_{row_label}")

        # with col4:
        #     st.markdown("**List of fields**", unsafe_allow_html=True)
        #     st.caption("Select fields manually (if override is checked)")
        #     print(f"Rendering: select_{slide_num}_{row_label}, metric_{slide_num}_{row_label}")
        #     selected_fields = st.multiselect("", disabled=not is_ok, options= field_list, key=f"select_{slide_num}_{row_label}")


        results.append({
            "row_label": row_label,
            # "is_ok": is_ok,
            # "selected_fields": selected_fields,
            "component_rows": selected_component_rows,
            "metric_fields": selected_metric_fields
        })

    # Add vertical spacing
    st.markdown("")

    # Create three columns and centre the button
    cola, colb, colc = st.columns([1, 2, 1])
    # with cola:
    #     if st.button("All OK, let’s Proceed"):
    #         st.session_state[f"slide_{slide_num}_proceed_triggered"] = True
    #         messages = continue_pipeline_after_hitl(slide_num, agent7=True)
    #         for msg in messages:
    #             append_log(msg, inline=True)
    #             st.markdown("### Debug Logs Returned")
    #             st.code("\n".join(messages or []), language="text")

    with colb:
        save_path = os.path.join(output_path, f"row_logic_merged_{slide_num}.json")
        if st.button(f"Proceed with {slide_num} selections", key=f"proceed_btn_{slide_num}"):
            user_override_map = {
                entry["row_label"]: {
                    "metric_fields": entry["metric_fields"],
                   "component_rows": entry["component_rows"]
                }
                for entry in results
            }
            with open(save_path, "w") as f:
                json.dump(results, f, indent=2)
            
                    # Reload base logic to preserve structure
            with open(row_logic_path, "r") as f:
                base_logic = json.load(f)

            # Inject user selections where applicable
            for row in base_logic:
                row_label = row["row_label"]
                if row_label in user_override_map:
                    override = user_override_map[row_label]
                    row["metric_fields"] = override["metric_fields"]
                    row["component_rows"] = override["component_rows"]
                    row["rationale"] = "User override applied via HITL interface."

            # Save to merged path
            with open(save_path, "w") as f:
                json.dump(base_logic, f, indent=2)

            st.success(f"Field selections for Slide {slide_num} saved to {save_path}")
            st.session_state[f"slide_{slide_num}_approved"] = True

            messages = list(continue_pipeline_after_hitl(slide_num))  # 👈 force full evaluation
            for msg in messages:
                append_log(msg, inline=True)
                st.markdown("✅ Inline debug: last message")
                st.code("\n".join(st.session_state.get("log", "").splitlines()[-3:]), language="text")

