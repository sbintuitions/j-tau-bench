import json
import random
from argparse import ArgumentParser
from collections import defaultdict

from tau2.data_model.tasks import Task
from tau2.domains.telecom_ja.tasks.mms_issues import mms_issue_task_manager
from tau2.domains.telecom_ja.tasks.mobile_data_issues import mobile_data_task_manager
from tau2.domains.telecom_ja.tasks.service_issues import service_issues_task_manager
from tau2.domains.telecom_ja.tasks.utils import get_persona_from_task_id
from tau2.utils import DATA_DIR


def create_tasks(save_tasks: bool = True, max_count_per_bin: int = 3) -> list[Task]:
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

    domain_data_dir = DATA_DIR / "tau2" / "domains" / "telecom_ja"

    file_full = domain_data_dir / "tasks_full.json"
    if save_tasks:
        with open(file_full, "w") as f:
            json.dump([t.model_dump() for t in tasks], f, indent=2, ensure_ascii=False)

    # tasks.json contains all tasks (same as tasks_full.json).
    # Actual subsets used for evaluation are controlled by split_tasks.json.
    file_tasks = domain_data_dir / "tasks.json"
    if save_tasks:
        with open(file_tasks, "w") as f:
            json.dump([t.model_dump() for t in tasks], f, indent=2, ensure_ascii=False)

    # Build tasks with attributes
    tasks_with_attrs = []
    for intent_tasks, intent in [
        (mobile_data_tasks, "mobile_data"),
        (service_tasks, "service"),
        (mms_tasks, "mms"),
    ]:
        for task in intent_tasks:
            num_subtasks = len(task.id.split("|"))
            tasks_with_attrs.append(
                {
                    "task": task,
                    "intent": intent,
                    "num_subtasks": num_subtasks,
                    "persona": get_persona_from_task_id(task.id),
                }
            )

    file_small = domain_data_dir / "tasks_small.json"
    small_tasks = [t["task"] for t in tasks_with_attrs if t["num_subtasks"] == 1]
    print(f"Number of tasks in small set: {len(small_tasks)}")
    if save_tasks:
        with open(file_small, "w") as f:
            json.dump([t.model_dump() for t in small_tasks], f, indent=2, ensure_ascii=False)

    # Sample tasks for the "base" split: max_count_per_bin per (intent, num_subtasks, persona) bin
    tasks_by_bins = defaultdict(list)
    for task in tasks_with_attrs:
        if task["num_subtasks"] < 2:  # We only keep tasks with at least 2 subtasks
            continue
        tasks_by_bins[(task["intent"], task["num_subtasks"], task["persona"])].append(
            task["task"]
        )

    sampled_tasks = []
    for (intent, num_subtasks, persona), bin_tasks in tasks_by_bins.items():
        num_sampled = min(max_count_per_bin, len(bin_tasks))
        sampled_tasks.extend(random.sample(bin_tasks, num_sampled))
        print(
            f"Sampled {num_sampled} tasks for {intent} with {num_subtasks} subtasks and persona {persona}..."
        )
    print(f"Number of sampled tasks: {len(sampled_tasks)}")

    # Generate split_tasks.json
    if save_tasks:
        _create_split_tasks(
            domain_data_dir,
            all_tasks=tasks,
            small_tasks=small_tasks,
            base_tasks=sampled_tasks,
        )

    return tasks


def _create_split_tasks(
    domain_data_dir,
    all_tasks: list[Task],
    small_tasks: list[Task],
    base_tasks: list[Task],
    train_ratio: float = 0.65,
) -> None:
    """Generate split_tasks.json with small/base/train/test/full splits.

    Splits:
      - small: single-issue tasks
      - base: sampled tasks (max_count_per_bin per bin, subtasks >= 2)
      - train: ~65% of base (for RL training etc.)
      - test: ~35% of base
      - full: all generated tasks
    """
    base_ids = sorted([t.id for t in base_tasks])

    # Split base into train/test
    base_shuffled = list(base_ids)
    random.shuffle(base_shuffled)
    train_size = int(len(base_shuffled) * train_ratio)
    train_ids = sorted(base_shuffled[:train_size])
    test_ids = sorted(base_shuffled[train_size:])

    split_tasks = {
        "small": sorted([t.id for t in small_tasks]),
        "train": train_ids,
        "test": test_ids,
        "full": sorted([t.id for t in all_tasks]),
        "base": base_ids,
    }

    file = domain_data_dir / "split_tasks.json"
    with open(file, "w") as f:
        json.dump(split_tasks, f, indent=2, ensure_ascii=False)

    print(f"Split tasks saved: small={len(split_tasks['small'])}, "
          f"base={len(base_ids)}, train={len(train_ids)}, "
          f"test={len(test_ids)}, full={len(split_tasks['full'])}")


def main():
    parser = ArgumentParser()
    parser.add_argument("-s", "--seed", type=int, default=42)
    parser.add_argument("-m", "--max-count-per-bin", type=int, default=3)
    args = parser.parse_args()
    random.seed(args.seed)
    create_tasks(max_count_per_bin=args.max_count_per_bin)


if __name__ == "__main__":
    main()
