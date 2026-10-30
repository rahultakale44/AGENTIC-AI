
"""
Smart Study Planner - ReAct Reasoning Agent
Uses Python standard library only.
Run: python react_agent.py
"""

class StudyPlannerAgent:

    def __init__(self):
        self.goal = "Create a 4-hour study schedule for Mathematics, DBMS and Python."
        self.plan = [
            "check_library",
            "collect_materials",
            "create_schedule"
        ]

    # Simulated tools
    def check_library(self):
        return "Library is closed today."

    def prepare_home(self):
        return "Home study space is ready."

    def collect_materials(self):
        return "Mathematics, DBMS and Python materials collected."

    def create_schedule(self):
        return [
            "Mathematics: 90 minutes",
            "DBMS: 75 minutes",
            "Python: 60 minutes",
            "Break: 15 minutes"
        ]

    def run(self):
        print("SMART STUDY PLANNER - ReAct AGENT")
        print("=" * 55)
        print("\nGOAL:", self.goal)

        print("\nINITIAL PLAN:")
        for task in self.plan:
            print("-", task)

        print("\nREASONING TRACE")

        for task in self.plan:

            if task == "check_library":
                print("\nTHOUGHT: I should first check whether the library is available.")
                print("ACTION: check_library()")
                observation = self.check_library()
                print("OBSERVATION:", observation)

                if "closed" in observation.lower():
                    print("THOUGHT: The library is unavailable. I need an alternative.")
                    self.plan = [
                        "prepare_home",
                        "collect_materials",
                        "create_schedule"
                    ]
                    print("REPLANNING: Switching to a home study setup.")
                    print("UPDATED PLAN:", self.plan)

            elif task == "prepare_home":
                print("\nTHOUGHT: I should prepare an alternative study location.")
                print("ACTION: prepare_home()")
                observation = self.prepare_home()
                print("OBSERVATION:", observation)

            elif task == "collect_materials":
                print("\nTHOUGHT: I need all three subject materials.")
                print("ACTION: collect_materials()")
                observation = self.collect_materials()
                print("OBSERVATION:", observation)

            elif task == "create_schedule":
                print("\nTHOUGHT: The study space and materials are ready.")
                print("ACTION: create_schedule()")
                observation = self.create_schedule()
                print("OBSERVATION: Schedule created.")

                for item in observation:
                    print("-", item)

        print("\nFINAL RESULT: Goal completed successfully.")


if __name__ == "__main__":
    agent = StudyPlannerAgent()
    agent.run()
