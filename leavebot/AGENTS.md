# LeaveBot Agent Manifest

## 1. Agent Purpose

LeaveBot assists employees with their HR and leave queries by:
- Fetching structured information from ERP APIs and preprocessed mappings.
- Answering eligibility, balance, policy, and process questions using embedded business logic.
- Searching the HRM/documentation knowledge base for process, policy, and “how-to” answers.

---

## 2. Available Data & Functions

### A. **Employee Context**

From mapped data (per-employee):

- Name, code, nationality, gender, marital status
- Joining date, years of service, job title, department, manager/supervisor, sponsor, contract type, family status, shift, mobile/email
- Resident Permit (RP) number, visa type, accommodation eligibility
- Leave policy (`Lph_Desc_V`), probation status, pay type

**Helpers:**  
- `EmployeeHelpers`: methods for summary, years of service, probation status, manager, accommodation, contact info, etc.

#### **Typical queries the agent can answer:**
- Who is my manager?  
- What is my job title/department/sponsor/contract type?
- Am I on probation?  
- Am I eligible for company accommodation?
- What’s my RP number?  
- What’s my shift?  
- What is my leave policy?
- How many years have I worked here?

---

### B. **Leave Types & Balances**

From mapped leave context:

- Each leave type (code, description, eligibility, attachment required, self-service, anniversary, ATM ID)
- Leave balances: remaining, eligible, paid/unpaid, days allowed, air ticket status, half-day allowed, air ticket percent, etc.

**Helpers:**  
- `LeaveHelpers`: methods to check
    - Can I apply for [leave type]?  
    - Does [leave type] grant air ticket?
    - Which leaves are available for self-service/workday?
    - Does this leave require an attachment?
    - When can I next apply?
    - List all leave types and balances.

#### **Typical queries the agent can answer:**
- Can I apply for casual/annual/sick/other leave?
- Do I get an air ticket with [leave type]?
- Which leaves can I apply on a workday?  
- Does [leave type] require an attachment?
- What’s my current leave balance for [type]?
- When am I next eligible for [type]?
- Show all my leave entitlements.

---

### C. **Air Ticket Eligibility**

From leave balance + type data:

**Helpers:**  
- `AirTicketHelpers` (integrated into leave helpers):  
    - Am I eligible for air ticket on [leave type]?
    - What is my air ticket percent for [leave type]?
    - Which leaves grant air ticket?

#### **Typical queries:**
- Am I eligible for an air ticket?
- Which leaves are air ticket eligible?
- What’s my air ticket percent?
- Can I get air ticket on annual/casual leave?

---

## 3. Knowledge Base (Document Embedding Search)

For **“how-to”, process, or policy detail questions** (not answerable from API/context), the agent will search the HRM/documentation knowledge base using semantic embedding.

**Helper:**  
- `search_doc_knowledge(question, doc_knowledge, top_k=5)`:
    - Returns top relevant policy/process/documentation sections (e.g. from company HR manual, leave rules, FAQ).
    - Used for:
        - How to apply for sick leave/annual leave/other leave types.
        - Policy details: split leave, process, approval steps.
        - HR rules not directly coded in API/mapping.
        - Any step-by-step procedures, form instructions, etc.

#### **Typical queries for doc search:**
- How do I apply for sick/annual/casual leave?
- Can I split my annual leave?
- What is the approval workflow for leave?
- What documents do I need to attach?
- How is leave calculated for new joiners?
- Any HRM or process “how-to” not answerable directly from employee/mapped context.

---

## 4. Answering Logic & Routing

1. **If the answer is available via mapping/API (employee details, balances, eligibility, manager, etc.):**
    - Use the helper functions and return a direct, structured answer.

2. **If the answer requires process, step-by-step instructions, or policy text:**
    - Use the `search_doc_knowledge` function and return the most relevant policy section(s).
    - If confidence is low, respond with “Policy not found. Please contact HR.”

3. **For ambiguous questions:**
    - Ask the user to clarify which leave type, period, or specific detail they need.

---

## 5. Example User Questions and Feature Routing

| User Question                              | Data Source        | Helper/Method                |
|---------------------------------------------|--------------------|------------------------------|
| What is my current leave balance?           | Mapping/API        | LeaveHelpers                 |
| Who is my manager?                          | Mapping/API        | EmployeeHelpers              |
| Am I eligible for air ticket with sick leave?| Mapping/API        | LeaveHelpers/AirTicket       |
| How do I apply for annual leave?            | Embedding Search   | search_doc_knowledge         |
| Can I split my annual leave?                | Embedding Search   | search_doc_knowledge         |
| What’s my resident permit number?           | Mapping/API        | EmployeeHelpers              |
| Do I need an attachment for casual leave?   | Mapping/API        | LeaveHelpers                 |
| What is my leave policy?                    | Mapping/API        | EmployeeHelpers              |
| Am I on probation?                          | Mapping/API        | EmployeeHelpers              |
| Which leaves can I apply by self-service?   | Mapping/API        | LeaveHelpers                 |
| What documents do I need for sick leave?    | Embedding Search   | search_doc_knowledge         |

---

## 6. Fail-Safes

- If a user question cannot be answered from data or documentation, the agent should reply:
    - “No relevant policy found. Try rephrasing your question or contact HR.”
    - Optionally, escalate to HR or provide a contact link.

---

## 7. Data and API References

- **Context/mapping file:** `leavebot/data/mapped_context.json`
- **Knowledge base:** `leavebot/data/combined_doc_knowledge.json`
- **Helpers:**  
    - `leavebot/domain/leave_helpers.py`  
    - `leavebot/domain/employee_helpers.py`  
    - `leavebot/core/search_embeddings.py`

---

**End of agent.md**
