from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.telecom_ja.data_model import BillStatus, LineStatus
from tau2.domains.telecom_ja.environment import TelecomEnvironment
from tau2.domains.telecom_ja.tasks.const import TOOL_CALL_GROUNDING, TOOL_CALL_INFO_CHECK
from tau2.domains.telecom_ja.tasks.manager import TaskManager
from tau2.domains.telecom_ja.tasks.utils import BaseTask, SelectionSet

OVERDUE_BILL_ID = "B1234321"


### Check solve
def get_env_assertions(expected_success: bool) -> list[EnvAssertion]:
    """
    Get the environment assertions for the service issue task.
    Service status is expected to be "接続済み" if the task is expected to be successful,
    and "サービスなし" otherwise.
    For the task to be successful, the overdue bill is either not in the database or paid.
    """
    if expected_success:
        return [
            EnvAssertion(
                env_type="user",
                func_name="assert_service_status",
                arguments={"expected_status": "接続済み"},
                message="Service status is not as expected",
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_no_overdue_bill",
                arguments={"overdue_bill_id": OVERDUE_BILL_ID},
                message="Overdue bill is not as expected",
            ),
        ]
    else:
        return [
            EnvAssertion(
                env_type="user",
                func_name="assert_service_status",
                arguments={"expected_status": "サービスなし"},
            ),
        ]


def is_fixed(env: TelecomEnvironment) -> bool:
    """
    Check if the service issue is fixed.
    """
    assertions = get_env_assertions(expected_success=True)
    success = True
    for assertion in assertions:
        success = success and env.run_env_assertion(
            assertion,
            raise_assertion_error=False,
        )
    return success


### Init Functions
def set_surrounding(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Set the user info for the service issue task.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_user_info",
            arguments={"name": "田中太郎", "phone_number": "090-1234-5678"},
        )
    ]


def airplane_mode_on(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Turn on airplane mode.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="turn_airplane_mode_on",
            arguments={},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_airplane_mode_status",
            arguments={"expected_status": True},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="Airplane mode is on but service is not broken",
        ),
    ]


def unseat_sim_card(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Unseat the SIM card.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="unseat_sim_card",
            arguments={},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="SIM card is unseated but service is not broken",
        ),
    ]


def lock_sim_card_pin(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Lock the SIM card with a PIN.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="lock_sim_card",
            arguments={"mode": "pin"},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="SIM card is locked with pin but service is not broken",
        ),
    ]


def lock_sim_card_puk(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Lock the SIM card with a PUK.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="lock_sim_card",
            arguments={"mode": "puk"},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="SIM card is locked with puk but service is not broken",
        ),
    ]


def break_apn_settings(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Break the APN settings.
    """
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="break_apn_settings",
            arguments={},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="APN settings are broken but service is not broken",
        ),
    ]


def suspend_line_for_overdue_bill(env: TelecomEnvironment) -> list[EnvFunctionCall]:
    """
    Suspend the line for an overdue bill.
    """
    user = env.tools.get_customer_by_phone(env.user_tools.db.surroundings.phone_number)
    line = env.tools._get_line_by_phone(env.user_tools.db.surroundings.phone_number)
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="suspend_line_for_overdue_bill",
            arguments={
                "customer_id": user.customer_id,
                "line_id": line.line_id,
                "new_bill_id": OVERDUE_BILL_ID,
                "contract_ended": False,
            },
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="simulate_network_search",
            arguments={},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="User is suspended for an overdue bill but service is not broken",
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_overdue_bill_exists",
            arguments={
                "customer_id": user.customer_id,
                "overdue_bill_id": OVERDUE_BILL_ID,
            },
            message="Overdue bill does not exist",
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_line_status",
            arguments={
                "customer_id": user.customer_id,
                "line_id": line.line_id,
                "expected_status": LineStatus.SUSPENDED,
            },
            message="Line is not suspended",
        ),
    ]


def suspend_line_for_overdue_bill_and_contract_end(
    env: TelecomEnvironment,
) -> list[EnvFunctionCall]:
    """
    Suspend the line for an overdue bill and a contract end.
    """
    user = env.tools.get_customer_by_phone(env.user_tools.db.surroundings.phone_number)
    line = env.tools._get_line_by_phone(env.user_tools.db.surroundings.phone_number)
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="suspend_line_for_overdue_bill",
            arguments={
                "customer_id": user.customer_id,
                "line_id": line.line_id,
                "new_bill_id": OVERDUE_BILL_ID,
                "contract_ended": True,
            },
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="simulate_network_search",
            arguments={},
        ),
        EnvAssertion(
            env_type="user",
            func_name="assert_service_status",
            arguments={"expected_status": "サービスなし"},
            message="User is suspended for an overdue bill but service is not broken",
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_overdue_bill_exists",
            arguments={
                "customer_id": user.customer_id,
                "overdue_bill_id": OVERDUE_BILL_ID,
            },
            message="Overdue bill does not exist",
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_line_status",
            arguments={
                "customer_id": user.customer_id,
                "line_id": line.line_id,
                "expected_status": LineStatus.SUSPENDED,
            },
            message="Line is not suspended",
        ),
    ]


### Fix Functions
def fix_airplane_mode_on(env: TelecomEnvironment) -> list[ToolCall]:
    """
    Fix the airplane mode on issue.
    """
    return [
        ToolCall(
            requestor="user",
            name="toggle_airplane_mode",
            arguments={},
        )
    ]


def fix_unseat_sim_card(env: TelecomEnvironment) -> list[ToolCall]:
    """
    Fix the unseat SIM card issue.
    """
    return [
        ToolCall(
            requestor="user",
            name="reseat_sim_card",
            arguments={},
        )
    ]


def fix_broken_apn_settings(env: TelecomEnvironment) -> list[ToolCall]:
    """
    Fix the broken APN settings issue.
    """
    return [
        ToolCall(
            requestor="user",
            name="reset_apn_settings",
            arguments={},
        ),
        ToolCall(
            requestor="user",
            name="reboot_device",
            arguments={},
        ),
    ]


def fix_suspend_line_for_overdue_bill(env: TelecomEnvironment) -> list[ToolCall]:
    """
    Fix the suspend line for overdue bill issue.
    """
    user = env.tools.get_customer_by_phone(env.user_tools.db.surroundings.phone_number)
    line = env.tools._get_line_by_phone(env.user_tools.db.surroundings.phone_number)
    for bill_id in user.bill_ids:
        bill = env.tools._get_bill_by_id(bill_id)
        if bill.status == BillStatus.OVERDUE:
            break
    else:
        raise ValueError("No overdue bill found")
    return [
        ToolCall(
            requestor="assistant",
            name="send_payment_request",
            arguments={"customer_id": user.customer_id, "bill_id": bill.bill_id},
        ),
        ToolCall(
            requestor="user",
            name="make_payment",
            arguments={},
        ),
        ToolCall(
            requestor="assistant",
            name="resume_line",
            arguments={
                "customer_id": user.customer_id,
                "line_id": line.line_id,
            },
        ),
        ToolCall(
            requestor="user",
            name="reboot_device",
            arguments={},
        ),
    ]


### Base Tasks
airplane_mode_on_task = BaseTask(
    name="airplane_mode_on",
    description="Airplane mode is on.",
    init_funcs=[airplane_mode_on],
    fix_funcs=[fix_airplane_mode_on],
)
unseat_sim_card_task = BaseTask(
    name="unseat_sim_card",
    description="SIM card is unseated.",
    init_funcs=[unseat_sim_card],
    fix_funcs=[fix_unseat_sim_card],
)
lock_sim_card_pin_task = BaseTask(
    name="lock_sim_card_pin",
    description="SIM card is locked with a PIN",
    init_funcs=[lock_sim_card_pin],
    fix_funcs=[None],
)

# lock_sim_card_puk_task = BaseTask(
#     name="lock_sim_card_puk",
#     description="SIM card is locked with a PUK",
#     init_funcs=[lock_sim_card_puk],
#     fix_funcs=[None],
# )

break_apn_settings_task = BaseTask(
    name="break_apn_settings",
    description="APN settings are broken",
    init_funcs=[break_apn_settings],
    fix_funcs=[fix_broken_apn_settings],
)

suspend_line_for_overdue_bill_task = BaseTask(
    name="overdue_bill_suspension",
    description="Line is suspended for an overdue bill",
    init_funcs=[suspend_line_for_overdue_bill],
    fix_funcs=[fix_suspend_line_for_overdue_bill],
)

suspend_line_for_overdue_bill_and_contract_end_task = BaseTask(
    name="contract_end_suspension",
    description="Line is suspended for an overdue bill and a contract end",
    init_funcs=[suspend_line_for_overdue_bill_and_contract_end],
    fix_funcs=[None],
)

### Selection Sets

# Requires workflow Step 1.1
airplane_mode_issues = SelectionSet(tasks=[airplane_mode_on_task])
# Requires workflow Step 2.1.1
unseat_sim_card_issues = SelectionSet(tasks=[unseat_sim_card_task])
# Requires workflow Step 2.1.2
lock_sim_card_issues = SelectionSet(tasks=[lock_sim_card_pin_task])
# Requires workflow Step 2.1.3
break_apn_settings_issues = SelectionSet(tasks=[break_apn_settings_task])

# Requires workflow Step 2.1.4
suspend_line_for_overdue_bill_issues = SelectionSet(
    tasks=[
        suspend_line_for_overdue_bill_task,
        suspend_line_for_overdue_bill_and_contract_end_task,
    ]
)

service_issues_selection_sets = [
    airplane_mode_issues,
    unseat_sim_card_issues,
    lock_sim_card_issues,
    break_apn_settings_issues,
    suspend_line_for_overdue_bill_issues,
]


### Task Manager
service_issues_task_manager = TaskManager(
    name="service_issue",
    purpose="Test resolution path: No Service/Connection Issues.",
    task_instructions=f"エージェントが提案した手順ですぐに問題が解決しない場合は、案内に従いつつも、最初の試みがうまくいかなかった時点で少し不満を示してください。ステータスバーに電波（シグナル）が表示されれば、問題は解決したとみなします。エージェントからステータス情報を求められた場合は、常にステータスバーを確認してください。エージェントから請求書の支払いを求められた場合は、応じてください。 {TOOL_CALL_INFO_CHECK} {TOOL_CALL_GROUNDING}",
    reason_for_call="数時間前から携帯電話に「圏外（サービスなし）」と表示されています。",
    known_info="あなたの名前は{name}で、電話番号は{phone_number} です。",
    ticket="ユーザーは携帯電話の通信サービスに問題を抱えています。電話の発着信ができず、ステータスバーには「圏外（サービスなし）」と表示されています。顧客名: {name}、電話番号: {phone_number}。ユーザーはすべての延滞料金を支払うことに同意しています。ステータスバーに電波（シグナル）が表示されれば、この問題は解決したとみなされます。",
    selection_sets=service_issues_selection_sets,
    get_env_assertions=get_env_assertions,
    set_surrounding=set_surrounding,
    is_fixed=is_fixed,
    domain="telecom_ja",
)

if __name__ == "__main__":
    tasks = service_issues_task_manager.create_tasks(save_tasks=False)
    print(f"Number of tasks: {len(tasks)}")
