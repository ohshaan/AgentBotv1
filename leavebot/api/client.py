import os
import requests
import logging
from typing import Dict, Any, List, Optional

# Auto-load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass  # python-dotenv not installed; skip

# Set up basic logging. In production, configure this at the app entry point.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

API_BASE = os.getenv("ERP_API_BASE", "http://117.247.187.131:8085/api")
TIMEOUT = 30  # seconds

class ERPApiClient:
    """
    Client for interacting with the ERP API for employee and leave data.
    """

    def __init__(self, token: Optional[str] = None, cgm_id: int = 1):
        """
        :param token: Bearer token for API authorization (may be blank for dev/test)
        :param cgm_id: Company group/master ID, default is 1
        """
        self.token = token or os.getenv("API_BEARER_TOKEN")
        # DO NOT enforce non-empty token if API allows blank
        self.headers = {
            "Authorization": f"Bearer {self.token or ''}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.cgm_id = cgm_id

    def get_employee_details(self, emp_id: int) -> List[Dict[str, Any]]:
        url = f"{API_BASE}/EmployeeMasterApi/HrmGetEmployeeDetails/"
        params = {"strEmp_ID_N": emp_id}
        try:
            resp = requests.post(url, headers=self.headers, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            logging.debug(f"Employee details for {emp_id}: {data}")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch employee details for {emp_id}: {e}")
            return []

    def get_leave_types(self, emp_id: int) -> List[Dict[str, Any]]:
        url = f"{API_BASE}/LeaveApplicationApi/FillLeaveType"
        params = {"Emp_ID_N": emp_id, "Cgm_ID_N": self.cgm_id}
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            logging.debug(f"Leave types for {emp_id}: {data}")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch leave types for {emp_id}: {e}")
            return []

    def get_leave_balance(self, emp_id: int, lpd_id: int, start: str = "2025-01-01", end: str = "2025-12-31") -> List[Dict[str, Any]]:
        url = f"{API_BASE}/LeaveApplicationApi"
        str_sql = f"{emp_id},{lpd_id},'{start}','{end}',0,0,1,0"
        params = {"StrSql": str_sql}
        try:
            resp = requests.post(url, headers=self.headers, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            logging.debug(f"Leave balance for emp_id={emp_id} lpd_id={lpd_id}: {data}")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch leave balance for emp_id={emp_id}, lpd_id={lpd_id}: {e}")
            return []

    def fetch_all_data(self, emp_id: int) -> Dict[str, Any]:
        """
        Fetches and returns all relevant data for an employee.
        """
        result = {"employee": [], "leave_types": [], "leave_balances": {}}
        result["employee"] = self.get_employee_details(emp_id)
        result["leave_types"] = self.get_leave_types(emp_id)
        leave_balances = {}
        for lt in result["leave_types"]:
            lpd_id = lt.get("Lpd_ID_N")
            if lpd_id is not None:
                leave_balances[lpd_id] = self.get_leave_balance(emp_id, lpd_id)
        result["leave_balances"] = leave_balances
        return result

# For direct script usage/testing:
if __name__ == "__main__":
    import json

    emp_id = 682
    client = ERPApiClient()  # Reads token from env by default

    data = client.fetch_all_data(emp_id)
    # Save raw output
    os.makedirs("leavebot/data", exist_ok=True)
    out_path = os.path.join("leavebot", "data", "api_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"API output saved to {out_path}")
    print(json.dumps(data, indent=2))
