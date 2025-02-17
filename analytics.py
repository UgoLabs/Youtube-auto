def compute_reward(performance: dict) -> float:
    """
    Computes a reward based on performance metrics (e.g., watch_time and CTR).
    """
    watch_time = performance.get("watch_time", 0.0)
    ctr = performance.get("ctr", 0.0)
    return watch_time * ctr
