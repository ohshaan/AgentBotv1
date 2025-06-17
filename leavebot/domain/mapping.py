import json
from typing import Any, Dict, List
def map_employee(employee_raw):
    if not employee_raw or not isinstance(employee_raw, list):
        return {}
    emp = employee_raw[0]
    return {
        "emp_id": emp.get("Emp_ID_N"),
        "name": emp.get("Emp_EFullName_V", "") or emp.get("Emp_EDisplayName_V", ""),
        "code": emp.get("Emp_Code_V", ""),
        "nationality": emp.get("Cnt_Nationality_V"),
        "gender": emp.get("Emp_Gender_V"),
        "marital_status": emp.get("Emp_MaritalStatusDesc_V"),
        "visa_type": emp.get("EmpVisatype_Desc_V") or emp.get("Emp_VisaType_V"),
        "visa_number": emp.get("Emp_VisaNumber_V"),
        "doj": emp.get("Emp_DOJ_D"),
        "job_title": emp.get("Emp_RpProfessionDesc_V"),
        "department": emp.get("Dpm_Desc_V"),
        "sponsor": emp.get("Emp_SponsorDesc_V"),
        "contract_type": emp.get("Ctm_Description_V"),
        "pay_type": emp.get("Emp_PayTypeDesc_V"),
        "nationality_code": emp.get("Cnt_ID_N"),
        "employee_type": emp.get("Emp_EmployeeTypeDesc_V"),
        "family_status": emp.get("Emp_FamilyStatus_V"),
        "mobile": emp.get("Emp_Mobile_V"),
        "email": emp.get("Emp_EmailID_V"),
        # --- Additional fields ---
        "rp_number": emp.get("Emp_RPNumber_V"),
        "rp_expiry": emp.get("Emp_RPExpiryDate_D"),
        "manager_id": emp.get("Emp_ReportingToID_N"),
        "manager_name": emp.get("Emp_EmployeeReportsDesc_V"),
        "leave_policy": emp.get("Lph_Desc_V"),
        "shift_name": emp.get("Sfh_ShiftName_V"),
        "shift_code": emp.get("Sfh_ShiftCode_V"),
        "probation_end": emp.get("Emp_ProbationEndDate_D"),
        "confirmed_date": emp.get("Emp_DateOfConfirmation_D"),
        "accommodation_eligible": any(
            el.get("Eligibility_Desc_V", "").strip().lower() == "accommodation"
            for el in emp.get("Eligibility", [])
        ),
        "reporting_to": emp.get("Emp_EmployeeReportsDesc_V"),
    }


def map_leave_types(leave_types_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Map raw leave types list to a clean list of dicts with relevant fields.
    """
    mapped = []
    for lt in leave_types_raw:
        mapped.append({
            "id": lt.get("Lpd_ID_N"),
            "code": lt.get("Lvm_Code_V"),
            "desc": lt.get("Lvm_Description_V"),
            "attach_required": str(lt.get("Lvm_AttachRequired_N", "0")) == "1",
            "self_service": str(lt.get("Lvm_ShwSelfService_N", "0")) == "1",
            "anniv_date": lt.get("Emp_AnnivDate_D"),
            "atm_id": lt.get("Atm_ID_N"),
            "eligibility_on_workdays": str(lt.get("Lpd_EligibilityOnWrkdays_N", "0")) == "1",
        })
    return mapped

def map_leave_balances(
    leave_balances_raw: Dict[str, Any],
    leave_types_raw: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Map raw leave balances dict to normalized dict keyed by leave code.
    Uses leave_types_raw to link code and description to balances.
    """
    id_to_code = {str(lt.get("Lpd_ID_N")): lt.get("Lvm_Code_V") for lt in leave_types_raw}
    mapped = {}
    for lpd_id, vals in leave_balances_raw.items():
        if not vals or not isinstance(vals, list):
            continue
        item = vals[0]
        code = id_to_code.get(str(lpd_id), str(lpd_id))
        mapped[code] = {
            "id": int(lpd_id),
            "balance": float(item.get("Balance", 0)),
            "eligible": float(item.get("Eligible", 0)),
            "paid": float(item.get("Paid", 0)),
            "unpaid": float(item.get("UnPaid", 0)),
            "days_allowed": int(item.get("DAYS", 0)),
            "air_ticket": bool(int(item.get("Airticket", 0))),
            "max_days": int(item.get("Maxdays", 0)),
            "allow_half_day": bool(int(item.get("Lpd_AllowHalfDay_N", 0))),
            "anniv_date": item.get("Emp_AnnivDate_D"),
            "air_ticket_percent": float(item.get("AirTicketPercent", 0)),
            # Add more fields if required for business rules.
        }
    return mapped

def build_full_context(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Take raw API output and map it to the full clean context for downstream use.
    """
    employee = map_employee(api_data["employee"])
    leave_types = map_leave_types(api_data["leave_types"])
    leave_balances = map_leave_balances(api_data["leave_balances"], api_data["leave_types"])
    return {
        "employee": employee,
        "leave_types": leave_types,
        "leave_balances": leave_balances,  # Keyed by leave code, e.g. 'AL'
    }

# Script usage example: reads API output and writes mapped context for further processing
if __name__ == "__main__":
    with open("leavebot/data/api_output.json", "r", encoding="utf-8") as f:
        api_data = json.load(f)
    mapped = build_full_context(api_data)
    # Save mapped output for downstream helpers
    with open("leavebot/data/mapped_context.json", "w", encoding="utf-8") as out_f:
        json.dump(mapped, out_f, indent=2, ensure_ascii=False)
    print("Saved mapped context to leavebot/data/mapped_context.json")
    print(json.dumps(mapped, indent=2))
