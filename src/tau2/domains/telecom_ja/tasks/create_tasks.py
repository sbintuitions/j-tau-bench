import json

from tau2.data_model.tasks import Task
from tau2.domains.telecom_ja.tasks.mms_issues import mms_issue_task_manager
from tau2.domains.telecom_ja.tasks.mobile_data_issues import mobile_data_task_manager
from tau2.domains.telecom_ja.tasks.service_issues import service_issues_task_manager
from tau2.utils import DATA_DIR

DOMAIN_DIR = DATA_DIR / "tau2" / "domains" / "telecom_ja"


def create_tasks(save_tasks: bool = True) -> list[Task]:
    tasks: list[Task] = []
    mobile_data_tasks = mobile_data_task_manager.create_tasks(save_tasks=False)
    print(f"Number of mobile data issue tasks: {len(mobile_data_tasks)}")
    tasks.extend(mobile_data_tasks)

    service_tasks = service_issues_task_manager.create_tasks(save_tasks=False)
    print(f"Number of service issue tasks: {len(service_tasks)}")
    tasks.extend(service_tasks)

    mms_tasks = mms_issue_task_manager.create_tasks(save_tasks=False)
    print(f"Number of mms issue tasks: {len(mms_tasks)}")
    tasks.extend(mms_tasks)

    print(f"Number of tasks: {len(tasks)}")

    if save_tasks:
        file = DOMAIN_DIR / "tasks.json"
        with open(file, "w") as f:
            json.dump([t.model_dump() for t in tasks], f, indent=2, ensure_ascii=False)

    validate_splits(tasks)

    return tasks


def validate_splits(tasks: list[Task]) -> None:
    split_file = DOMAIN_DIR / "split_tasks.json"
    with open(split_file) as f:
        splits: dict[str, list[str]] = json.load(f)

    task_ids = {t.id for t in tasks}

    for split_name, split_ids in splits.items():
        if split_name == "full":
            continue
        missing = [sid for sid in split_ids if sid not in task_ids]
        if missing:
            print(f"[WARN] split '{split_name}': {len(missing)} IDs not found in tasks")
            for mid in missing:
                print(f"  - {mid}")
        else:
            print(f"[OK] split '{split_name}': all {len(split_ids)} IDs found")


def main():
    create_tasks()


if __name__ == "__main__":
    main()
