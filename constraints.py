from typing import Dict, Any

def validate_schedule_constraints(schedule_plan: Dict[str, Any]) -> bool:
    """
    Validates the schedule plan against constraints.
    For example, no more than 3 posts per day.
    """
    max_posts_per_day = 3
    for day, times in schedule_plan.items():
        if len(times) > max_posts_per_day:
            return False
    return True
