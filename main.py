import math
import random
import json
import os
from datetime import datetime, timedelta

class FSRS:
    def __init__(self, params=None):
        # Default parameters if not provided
        if params is None:
            self.params = {
                'w1': 1.0, 'w2': 1.0, 'w3': 1.0, 'w4': 1.0,
                'w5': 1.0, 'w6': 1.0, 'w7': 1.0, 'w8': 1.0,
                'w11': 1.0, 'w12': 1.0, 'w15': 1.0, 'w16': 1.0
            }
        else:
            self.params = params

    def calculate_retrievability(self, t, S):
        return (1 + (t / S) ** -1) ** -1

    def stability_increase(self, S, D, R, grade):
        grade_map = {'Again': 1, 'Hard': 2, 'Good': 3, 'Easy': 4}
        G = grade_map.get(grade, 3)

        f_D = 11 - D
        f_S = max(1, (math.log(S + 1) / math.log(2)) ** -1)
        f_R = max(1, (math.log(R + 1) / math.log(2)) ** -1)

        w15 = 0 if grade == 'Again' else 1 if grade in ['Good', 'Easy'] else 0.5
        w16 = 1 if grade in ['Hard', 'Good'] else 3

        SInc = (f_D * f_S * f_R) * self.params['w1'] * w15 * w16
        return max(1, SInc)

    def update_stability(self, current_S, D, R, grade):
        if grade == 'Again':
            f_D = D ** -self.params['w12']
            S_new = min(current_S, current_S * f_D * self.params['w11'])
        else:
            S_new = current_S * self.stability_increase(current_S, D, R, grade)
        return S_new

    def update_difficulty(self, current_D, grade, R):
        difficulty_change = {
            'Again': 1.0, 'Hard': 0.2, 'Good': 0.0, 'Easy': -0.2
        }
        D_change = difficulty_change.get(grade, 0.0)
        D_new = current_D + D_change
        D_new = D_new * 0.9 + self.params['w4'] * 0.1
        return max(1, min(10, D_new))

class PhysicsQuestion:
    def __init__(self, question_type):
        self.question_type = question_type
        self.stability = 0.0001  # Changed from 1.0 to 0.0001
        self.difficulty = 5.0
        self.last_reviewed = datetime.now()
        self.next_review = datetime.now()

    def generate_question(self):
        methods = {
            'kinematics': self.generate_kinematics_question,
            'dynamics': self.generate_dynamics_question,
            'energy': self.generate_energy_question,
            'circular_motion': self.generate_circular_motion_question
        }
        return methods[self.question_type]()

    def generate_kinematics_question(self):
        initial_velocity = round(random.uniform(0, 20), 2)
        acceleration = round(random.uniform(0.5, 5), 2)
        time = round(random.uniform(1, 10), 2)

        final_velocity = initial_velocity + acceleration * time

        question = (f"An object starts with an initial velocity of {initial_velocity} m/s. "
                    f"If it accelerates at {acceleration} m/s², "
                    f"what is its velocity after {time} seconds?")
        
        return {
            'question': question,
            'answer': round(final_velocity, 2),
            'solution_steps': [
                f"v = v₀ + at",
                f"v = {initial_velocity} + {acceleration} × {time}",
                f"v = {final_velocity} m/s"
            ]
        }

    def generate_dynamics_question(self):
        mass = round(random.uniform(1, 100), 2)
        acceleration = round(random.uniform(0.5, 10), 2)

        force = mass * acceleration

        question = (f"A {mass} kg object experiences an acceleration of {acceleration} m/s². "
                    f"What is the net force acting on it?")
        
        return {
            'question': question,
            'answer': round(force, 2),
            'solution_steps': [
                "F = ma",
                f"F = {mass} × {acceleration}",
                f"F = {force} N"
            ]
        }

    def generate_energy_question(self):
        mass = round(random.uniform(1, 50), 2)
        height = round(random.uniform(1, 20), 2)
        g = 9.8

        potential_energy = mass * g * height

        question = (f"An object with a mass of {mass} kg is raised to a height of {height} m. "
                    f"Calculate its gravitational potential energy.")
        
        return {
            'question': question,
            'answer': round(potential_energy, 2),
            'solution_steps': [
                "PE = mgh",
                f"PE = {mass} × {g} × {height}",
                f"PE = {potential_energy} J"
            ]
        }

    def generate_circular_motion_question(self):
        radius = round(random.uniform(1, 10), 2)
        velocity = round(random.uniform(5, 30), 2)

        centripetal_acceleration = velocity**2 / radius

        question = (f"An object moves in a circular path with a radius of {radius} m "
                    f"and a velocity of {velocity} m/s. "
                    f"What is its centripetal acceleration?")
        
        return {
            'question': question,
            'answer': round(centripetal_acceleration, 2),
            'solution_steps': [
                "a = v²/r",
                f"a = {velocity}²/{radius}",
                f"a = {centripetal_acceleration} m/s²"
            ]
        }

class PhysicsFlashcardStudyApp:
    def __init__(self, study_duration, categories=None):
        self.fsrs = FSRS()
        self.study_duration = timedelta(minutes=study_duration)
        self.start_time = datetime.now()
        self.questions = []
        self.save_file = 'physics_flashcard_data.json'

        # Default categories if none specified
        if categories is None:
            categories = ['kinematics', 'dynamics', 'energy', 'circular_motion']

        # Load existing data if available
        existing_data = self.load_previous_data()

        # Create or update questions based on loaded data and selected categories
        for category in categories:
            # Check if a question of this category already exists in loaded data
            existing_question = next((q for q in existing_data if q['question_type'] == category), None)
            
            if existing_question:
                # Restore question from saved data
                question = PhysicsQuestion(category)
                question.stability = existing_question['stability']
                question.difficulty = existing_question['difficulty']
                question.last_reviewed = datetime.fromisoformat(existing_question['last_reviewed'])
                question.next_review = datetime.fromisoformat(existing_question['next_review'])
            else:
                # Create new question if no saved data exists
                question = PhysicsQuestion(category)
                question.next_review = datetime.now()  # Make it immediately reviewable

            self.questions.append(question)

    def load_previous_data(self):
        """ Load data from the saved file if it exists. """
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def run_study_session(self):
        # Calculate the minimum stability needed to "master" the questions
        # Stability is in days, so we convert study duration to days
        min_stability_days = max(0.1, self.study_duration.total_seconds() / (24 * 3600))

        while datetime.now() - self.start_time < self.study_duration:
            current_time = datetime.now()

            # Check if all questions have reached the desired stability
            if all(q.stability >= min_stability_days for q in self.questions):
                print("\n🎉 All questions have reached the desired stability. Study session complete!")
                break
            
            # Find reviewable questions
            reviewable_questions = [q for q in self.questions if q.next_review <= current_time]
            if not reviewable_questions:
                reviewable_questions = self.questions

            question_to_review = min(reviewable_questions, key=lambda q: q.next_review)
            problem = question_to_review.generate_question()
            
            print("\n" + "=" * 50)
            print(problem['question'])
            print("=" * 50)

            # Ask user if they want to see the solution steps
            show_solution = input("Would you like to see the solution steps? (y/n): ").lower()
            if show_solution == 'y':
                print("\nSolution Steps:")
                for step in problem['solution_steps']:
                    print(step)

            # Get user answer
            try:
                user_answer = float(input("\nEnter your answer: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            correct_answer = problem['answer']
            tolerance = 0.1 * abs(correct_answer)
            is_correct = abs(user_answer - correct_answer) <= tolerance

            if is_correct:
                print(f"Correct! The answer is {correct_answer}.\n")
            else:
                print(f"Incorrect. The correct answer is {correct_answer}.\n")

            # Ask for difficulty rating
            grade = input("How difficult was this problem? (Again/Hard/Good/Easy): ").capitalize()
            question_to_review.stability = self.fsrs.update_stability(question_to_review.stability, 
                                                                     question_to_review.difficulty, 
                                                                     len(self.questions), 
                                                                     grade)
            question_to_review.difficulty = self.fsrs.update_difficulty(question_to_review.difficulty, 
                                                                       grade, len(self.questions))
            question_to_review.next_review = datetime.now() + timedelta(days=question_to_review.stability)
            elapsed_time = datetime.now() - self.start_time
            remaining_time = self.study_duration - elapsed_time
            print(f"\n📊 Progress: {elapsed_time.total_seconds() / self.study_duration.total_seconds() * 100:.1f}% complete")
            print(f"Time remaining: {remaining_time}")

    def save_data(self):
        """ Save the study session data for future reference. """
        data = [
            {
                'question_type': q.question_type,
                'stability': q.stability,
                'difficulty': q.difficulty,
                'last_reviewed': q.last_reviewed.isoformat(),
                'next_review': q.next_review.isoformat()
            }
            for q in self.questions
        ]
        with open(self.save_file, 'w') as f:
            json.dump(data, f)

def main():
    study_duration = int(input("Enter study session duration (minutes): "))
    print("Select categories (separate by commas):\n1. Kinematics\n2. Dynamics\n3. Energy\n4. Circular Motion")
    categories_input = input("Your selection: ")
    
    category_map = {
        '1': 'kinematics', 
        '2': 'dynamics', 
        '3': 'energy', 
        '4': 'circular_motion'
    }
    
    # Convert numeric inputs to category names
    categories = []
    for cat in categories_input.split(','):
        cat = cat.strip()
        if cat in category_map:
            categories.append(category_map[cat])
        else:
            print(f"Invalid category: {cat}. Skipping.")
    
    # Ensure at least one valid category
    if not categories:
        print("No valid categories selected. Using all categories.")
        categories = None

    app = PhysicsFlashcardStudyApp(study_duration, categories)
    app.run_study_session()
    app.save_data()

if __name__ == "__main__":
    main()