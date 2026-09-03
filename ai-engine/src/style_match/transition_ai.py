"""Transition Intelligence — Context-aware transition matching"""
from typing import List, Dict

class TransitionAI:
    TRANSITION_RULES = {
        "high_energy": "whip",
        "drop_weight": "cut",
        "rest_period": "dissolve",
        "steady_rep": "smooth_cut"
    }

    def recommend_transitions(self, energy_timeline: List[float]) -> List[Dict]:
        timeline_cuts = []
        for i in range(1, len(energy_timeline)):
            prev_e = energy_timeline[i - 1]
            curr_e = energy_timeline[i]
            diff = abs(curr_e - prev_e)
            
            if curr_e > 0.7:
                t_type = self.TRANSITION_RULES["high_energy"]
            elif diff > 0.4:
                t_type = self.TRANSITION_RULES["drop_weight"]
            elif curr_e < 0.25:
                t_type = self.TRANSITION_RULES["rest_period"]
            else:
                t_type = self.TRANSITION_RULES["steady_rep"]
                
            timeline_cuts.append({"index": i, "transition": t_type, "confidence": 0.88})
        return timeline_cuts
