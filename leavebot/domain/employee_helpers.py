from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class EmployeeHelpers:
    """
    Utility class to provide standardized access to employee information.
    Expects a pre-mapped employee dictionary (all keys normalized).
    """

    def __init__(self, employee: Dict[str, Any]):
        self.emp = employee

    def get_full_name(self) -> str:
        """Return the standardized full name of the employee."""
        return self.emp.get("name", "").strip() or (
            f"{self.emp.get('first_name', '')} {self.emp.get('last_name', '')}".strip()
        )

    def get_job_title(self) -> str:
        return self.emp.get("job_title", "") or "Not specified"

    def get_department(self) -> str:
        return self.emp.get("department", "") or "Not specified"

    def get_sponsor(self) -> str:
        return self.emp.get("sponsor", "") or "Not specified"

    def get_joining_date(self) -> str:
        return self.emp.get("doj", "") or "Not specified"

    def get_years_of_service(self) -> Optional[int]:
        doj = self.emp.get("doj", "")
        try:
            join_date = datetime.strptime(doj, "%d-%b-%Y")
            return (datetime.now() - join_date).days // 365
        except Exception:
            return None

    def get_contract_type(self) -> str:
        return self.emp.get("contract_type", "") or "Not specified"

    def get_family_status(self) -> str:
        return self.emp.get("family_status", "") or "Not specified"

    def get_mobile(self) -> str:
        return self.emp.get("mobile", "") or "Not specified"

    def get_email(self) -> str:
        return self.emp.get("email", "") or "Not specified"

    def get_leave_policy(self) -> str:
        return self.emp.get("leave_policy", "") or "Not specified"

    def get_shift(self) -> str:
        # Accepts both shift and shift_name as mapped field
        return self.emp.get("shift", "") or self.emp.get("shift_name", "") or "Not specified"

    def get_rp_number(self) -> str:
        return self.emp.get("rp_number", "") or "Not specified"

    def get_manager(self) -> str:
        # Accepts manager_name, reporting_to, or raw field
        return self.emp.get("manager_name") or self.emp.get("reporting_to") or self.emp.get("manager") or "Not specified"

    def is_on_probation(self) -> Tuple[Optional[bool], str]:
        """
        Returns (bool, message) if probation status can be determined.
        None if date format or fields missing.
        """
        probation_end = self.emp.get("probation_end")
        if not probation_end:
            return None, "Probation information not available."
        try:
            today = datetime.now().date()
            end_date = datetime.strptime(probation_end, "%d-%b-%Y").date()
            if today < end_date:
                return True, f"You are on probation until {probation_end}."
            else:
                return False, f"You are not on probation. Probation ended on {probation_end}."
        except Exception:
            return None, "Probation date format invalid."

    def is_eligible_for_accommodation(self) -> Tuple[bool, str]:
        eligible = self.emp.get("accommodation_eligible", False)
        return (
            eligible,
            "You are eligible for company accommodation."
            if eligible
            else "You are not eligible for company accommodation."
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns a summary dictionary of all standard employee details,
        suitable for chat output or as a profile card.
        """
        return {
            "name": self.get_full_name(),
            "job_title": self.get_job_title(),
            "department": self.get_department(),
            "sponsor": self.get_sponsor(),
            "joining_date": self.get_joining_date(),
            "years_of_service": self.get_years_of_service(),
            "contract_type": self.get_contract_type(),
            "family_status": self.get_family_status(),
            "mobile": self.get_mobile(),
            "email": self.get_email(),
            "leave_policy": self.get_leave_policy(),
            "shift": self.get_shift(),
            "rp_number": self.get_rp_number(),
            "manager": self.get_manager(),
        }

if __name__ == "__main__":
    import json
    with open("leavebot/data/mapped_context.json", "r", encoding="utf-8") as f:
        ctx = json.load(f)
    emp_helper = EmployeeHelpers(ctx["employee"])

    print(emp_helper.get_full_name())
    print(emp_helper.get_job_title())
    print(emp_helper.get_sponsor())
    print(emp_helper.get_years_of_service())
    print(emp_helper.get_leave_policy())
    print(emp_helper.get_shift())
    print(emp_helper.get_rp_number())
    print(emp_helper.get_manager())
    print(emp_helper.is_on_probation())
    print(emp_helper.is_eligible_for_accommodation())
    print(emp_helper.get_summary())
