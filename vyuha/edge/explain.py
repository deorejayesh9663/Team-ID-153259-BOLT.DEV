def explain_congestion_decision(predicted_wait_time, node_id, threshold=2.0):
    """
    Formats the output of the Congestion GRU model into a human-readable explanation.
    """
    if predicted_wait_time > threshold:
        return f"Routing altered: High congestion predicted at node {node_id} (Wait time: {predicted_wait_time:.1f}s > threshold {threshold}s)"
    return f"Routing normal: Node {node_id} is clear (Wait time: {predicted_wait_time:.1f}s)"

def explain_priority_decision(priority_class, payload_weight, deadline_urgency):
    """
    Formats the output of the Priority Advisor Decision Tree into a human-readable explanation.
    """
    priority_map = {
        1: "Critical",
        2: "High",
        3: "Medium",
        4: "Low",
        5: "Background"
    }
    
    priority_name = priority_map.get(priority_class, "Unknown")
    
    return (f"Base priority set to [{priority_class}] {priority_name} "
            f"due to payload weight ({payload_weight:.1f} kg) and deadline urgency ({deadline_urgency*100:.0f}%).")

def explain_pibt_yield(yielding_robot, higher_priority_robot, node_id):
    """
    Formats PIBT yield actions into human readable strings.
    """
    return f"Robot {yielding_robot} yielded priority at node {node_id} to Robot {higher_priority_robot}"

if __name__ == "__main__":
    import sys
    # Fix Windows console encoding
    sys.stdout.reconfigure(encoding='utf-8')
    print("Testing Explainability Formatter...")
    print(explain_congestion_decision(3.5, node_id="(12, 15)", threshold=2.0))
    print(explain_congestion_decision(0.5, node_id="(2, 4)", threshold=2.0))
    print(explain_priority_decision(1, payload_weight=85.0, deadline_urgency=0.9))
    print(explain_priority_decision(5, payload_weight=10.0, deadline_urgency=0.1))
    print(explain_pibt_yield("R12", "R4", "(5, 5)"))
