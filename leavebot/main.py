import streamlit as st
import json
import os
import sys
from urllib.parse import parse_qs

# Allow running this script directly by ensuring the package root is on sys.path
if __name__ == "__main__" and os.path.basename(os.getcwd()) != "leavebot":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from leavebot.domain.leave_helpers import LeaveHelpers
from leavebot.domain.employee_helpers import EmployeeHelpers
from leavebot.core.search_embeddings import search_doc_knowledge

# ---- Load employee data and doc knowledge ----
def load_context(emp_id):
    with open("leavebot/data/mapped_context.json", "r", encoding="utf-8") as f:
        ctx = json.load(f)
    if str(ctx['employee'].get('emp_id', '')) == str(emp_id):
        return ctx
    else:
        st.error("Employee not found in mapped context. Please re-run mapping for the employee.")
        st.stop()

def load_doc_knowledge():
    doc_path = "leavebot/data/combined_doc_knowledge.json"
    if not os.path.exists(doc_path):
        st.warning("Doc knowledge file not found.")
        return []
    with open(doc_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---- Main app ----
st.set_page_config(page_title="LeaveBot - HR Assistant", layout="centered")
st.title("LeaveBot - HR/ERP Assistant")

# --- Read emp id from query string ---
query_params = st.experimental_get_query_params()
emp_id = query_params.get('emp', [None])[0]

if not emp_id:
    st.info("Add ?emp=682 to your URL (e.g., http://localhost:8501/?emp=682)")
    st.stop()

ctx = load_context(emp_id)
doc_knowledge = load_doc_knowledge()

leave_helper = LeaveHelpers(ctx['leave_balances'], ctx['leave_types'])
emp_helper = EmployeeHelpers(ctx['employee'])

st.markdown(f"**Welcome, {emp_helper.get_full_name()}** (Employee ID: {emp_id})")

# ---- User Query Box ----
user_query = st.text_input("Ask your HR or leave question:")

if user_query:
    # --- Try mapped helpers ---
    lower_q = user_query.lower()

    # Leave application
    if "leave balance" in lower_q:
        leave_codes = [lt['code'] for lt in ctx['leave_types']]
        balances = [
            f"{lt['desc']}: {ctx['leave_balances'][lt['code']]['balance']} days"
            for lt in ctx['leave_types']
            if ctx['leave_balances'][lt['code']]['balance'] > 0
        ]
        st.markdown("**Your leave balances:**")
        st.write("\n".join(balances))
    elif "air ticket" in lower_q:
        results = [k for k,v in ctx['leave_balances'].items() if v.get('air_ticket')]
        if results:
            tickets = [
                f"{ctx['leave_types'][i]['desc']} ({ctx['leave_types'][i]['code']}): {ctx['leave_balances'][ctx['leave_types'][i]['code']]['air_ticket_percent']}%"
                for i in range(len(ctx['leave_types']))
                if ctx['leave_types'][i]['code'] in results
            ]
            st.markdown("**Leaves eligible for Air Ticket:**")
            st.write("\n".join(tickets))
        else:
            st.write("No leaves grant air ticket.")
    elif "manager" in lower_q or "reporting" in lower_q:
        st.write(f"Your manager: {emp_helper.get_manager()}")
    elif "probation" in lower_q:
        on_prob, msg = emp_helper.is_on_probation()
        st.write(msg)
    elif "accommodation" in lower_q:
        eligible, msg = emp_helper.is_eligible_for_accommodation()
        st.write(msg)
    elif "shift" in lower_q:
        st.write(f"Your shift: {emp_helper.get_shift()}")
    elif "rp number" in lower_q or "resident permit" in lower_q:
        st.write(f"Your RP Number: {emp_helper.get_rp_number()}")
    elif "department" in lower_q:
        st.write(f"Your department: {emp_helper.get_department()}")
    elif "joining date" in lower_q or "doj" in lower_q:
        st.write(f"Your joining date: {emp_helper.get_joining_date()}")
    else:
        # ---- Fallback: Policy Embedding Search ----
        results = search_doc_knowledge(user_query, doc_knowledge, top_k=2)
        if results:
            for result in results:
                st.markdown(f"**Matched Policy Section:** {result.get('section', 'N/A')} (Score: {result['score']:.3f})")
                st.write(result.get('text', 'No policy text found.'))
        else:
            st.warning("No relevant policy or answer found. Try rephrasing or contact HR.")

# ---- Show summary / context (optional) ----
with st.expander("Show my profile summary"):
    st.json(emp_helper.get_summary())
