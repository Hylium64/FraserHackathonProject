import math
import numpy as np

class FSRS:
    def __init__(self, params=None):
        # Default parameters if not provided
        if params is None:
            # These are example values and should be optimized
            self.params = {
                'w1': 1.0,   # Overall scale factor
                'w2': 1.0,   # Difficulty impact factor
                'w3': 1.0,   # Stability increase factor
                'w4': 1.0,   # Default difficulty
                'w5': 1.0,   # Retrievability impact
                'w6': 1.0,   # Memory stability impact
                'w7': 1.0,   # Interval scaling
                'w8': 1.0,   # Lapse stability scaling
                'w11': 1.0,  # Lapse stability factor
                'w12': 1.0,  # Non-linear difficulty in lapse
                'w15': 1.0,  # Hard/Easy adjustment for stability increase
                'w16': 1.0   # Hard/Easy adjustment for stability increase
            }
        else:
            self.params = params

    def calculate_retrievability(self, t, S):
        """
        Calculate retrievability using the power function from FSRS v4.5
        t: time elapsed since last review
        S: memory stability
        """
        return (1 + (t / S) ** -1) ** -1

    def stability_increase(self, S, D, R, grade):
        """
        Calculate the stability increase factor
        S: current memory stability
        D: difficulty
        R: retrievability
        grade: review grade (Again, Hard, Good, Easy)
        """
        # Grade mapping
        grade_map = {'Again': 1, 'Hard': 2, 'Good': 3, 'Easy': 4}
        G = grade_map.get(grade, 3)  # Default to Good if unknown

        # Components of stability increase
        f_D = 11 - D  # Linear difficulty factor
        f_S = max(1, (math.log(S + 1) / math.log(2)) ** -1)  # Stability saturation
        f_R = max(1, (math.log(R + 1) / math.log(2)) ** -1)  # Retrievability impact

        # Stability adjustment based on grade
        if grade == 'Again':
            w15 = 0  # Stability scaling for Again
        else:
            w15 = 1 if grade in ['Good', 'Easy'] else 0.5

        w16 = 1 if grade in ['Hard', 'Good'] else 3  # Grade-based multiplier

        # Combined stability increase factor
        SInc = (f_D * f_S * f_R) * self.params['w1'] * w15 * w16

        return max(1, SInc)  # Ensure stability doesn't decrease

    def update_stability(self, current_S, D, R, grade):
        """
        Update memory stability based on review
        """
        if grade == 'Again':
            # Special formula for lapse
            f_D = D ** -self.params['w12']
            S_new = min(current_S, current_S * f_D * self.params['w11'])
        else:
            # Normal stability increase
            S_new = current_S * self.stability_increase(current_S, D, R, grade)

        return S_new

    def update_difficulty(self, current_D, grade, R):
        """
        Update card difficulty
        """
        # Grade impact on difficulty
        difficulty_change = {
            'Again': 1.0,   # Significant increase
            'Hard': 0.2,    # Small increase
            'Good': 0.0,    # No change
            'Easy': -0.2    # Small decrease
        }

        # Update difficulty
        D_change = difficulty_change.get(grade, 0.0)
        D_new = current_D + D_change

        # Mean reversion
        D_new = D_new * 0.9 + self.params['w4'] * 0.1

        return max(1, min(10, D_new))  # Constrain difficulty between 1-10

    def predict_review_outcome(self, S, D, R):
        """
        Predict probability of successfully recalling the card
        """
        return (1 + (1/R - 1) / math.exp(S * math.log(math.e) / 10)) ** -1

def calculate_stability(initial_stability, initial_difficulty, initial_retrievability, grade):
    fsrs = FSRS()

    # Simulate a few reviews
    current_S = initial_stability
    current_D = initial_difficulty
    
    intervals = []
    # Calculate retrievability at review time
    R = fsrs.calculate_retrievability(1, current_S)
    
    # Predict review outcome
    success_probability = fsrs.predict_review_outcome(current_S, current_D, R)
    
    # Update stability and difficulty
    current_S = fsrs.update_stability(current_S, current_D, R, grade)
    current_D = fsrs.update_difficulty(current_D, grade, R)
    
    print(f"Grade: {grade}")
    print(f"New Stability: {current_S}")
    print(f"New Difficulty: {current_D}")
    print(f"Success Probability: {success_probability}\n")

#calculate_stability(1.0, 2.0, 1.0, 'Hard')