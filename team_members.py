from pulp import LpVariable, LpProblem, lpSum, value, LpMaximize
import matplotlib.pyplot as plt
import random as rand
import tkinter as tk


possible_tasks = {
    "Front-end Development": 80,
    "Back-end Development": 70,
    "Database Management": 50,
    "Testing": 40,
    "Documentation": 30,
    "Debugging": 20
}

team_members = [
    {
        "name": "Member1",
        "skills": {"Python": "Intermediate", "Spring": "Intermediate", "React": "Beginner", "Java": "Advanced"},
        "preferences": {"Front-end Development": 80, "Back-end Development": 70}
    },
    {
        "name": "Member2",
        "skills": {"Python": "Intermediate", "Java": "Intermediate", "SQL": "Intermediate"},
        "preferences": {"Back-end Development": 80, "Database Management": 70}
    },
    {
        "name": "Member3",
        "skills": {"Java": "Advanced", "React": "Intermediate", "SQL": "Intermediate"},
        "preferences": {"Front-end Development": 80, "Back-end Development": 70}
    }
]

prob = LpProblem("Task_Allocation_ILP", LpMaximize)

x = {(task, member): LpVariable(f"x_{task}_{member}", cat="Binary")
     for task in possible_tasks
     for member in range(len(team_members))}

skill_scores = {}


def compute_composite_score(task, member):
    score = 0
    skill_score = 0
    member_name = team_members[member]['name']
    if task in team_members[member]['preferences']:
        score += team_members[member]['preferences'][task]
    if task == "Front-end Development" or task == "Back-end Development":
        for skill in ["Java", "Spring"]:
            skill_level = team_members[member]['skills'].get(skill, "None")
            if skill_level == "Beginner":
                skill_score += 5
            elif skill_level == "Intermediate":
                skill_score += 10
            elif skill_level == "Advanced":
                skill_score += 20
        for skill, level in team_members[member]['skills'].items():
            if skill not in ["Java", "Spring"]:
                skill_score += 5
    elif task == "Database Management":
        for skill in ["SQL"]:
            skill_level = team_members[member]['skills'].get(skill, "None")
            if skill_level == "Beginner":
                skill_score += 5
            elif skill_level == "Intermediate":
                skill_score += 10
            elif skill_level == "Advanced":
                skill_score += 20
        for skill, level in team_members[member]['skills'].items():
            if skill not in ["SQL"]:
                skill_score += 5
    elif task == "Testing" or "Documentation" or "Debugging":
        for level in ["Advanced", "Intermediate", "Beginner"]:
            for skill, skill_level in team_members[member]['skills'].items():
                if skill_level == level:
                    if level == "Advanced":
                        skill_score -= 5
                    elif level == "Intermediate":
                        skill_score -= 10
                    elif level == "Beginner":
                        skill_score -= 20

    score += skill_score
    score += possible_tasks[task]
    luck = rand.random()
    score *= luck

    if member_name not in skill_scores:
        skill_scores[member_name] = {}
    skill_scores[member_name][task] = skill_score

    return score


prob += lpSum(compute_composite_score(task, member) * x[task, member]
              for task in possible_tasks
              for member in range(len(team_members)))


for task in possible_tasks:
    prob += lpSum(x[task, member] for member in range(len(team_members))) == 1

for member in range(len(team_members)):
    prob += lpSum(x[task, member] for task in possible_tasks) <= 2

for member in range(len(team_members)):
    prob += lpSum([x["Front-end Development", member], x["Back-end Development", member]]) <= 1

prob.solve()

members = []
tasks = []
points = []

for member in team_members:
    member_name = member['name']
    members.append(member_name)
    member_tasks = []
    member_points = []
    for task in possible_tasks:
        assigned = False
        for member_idx in range(len(team_members)):
            if value(x[task, member_idx]) == 1 and team_members[member_idx]['name'] == member_name:
                assigned = True
                member_tasks.append(task)
                member_points.append(compute_composite_score(task, member_idx))
                break
        if not assigned:
            member_tasks.append(None)
            member_points.append(0)
    tasks.append(member_tasks)
    points.append(member_points)


def plot_member_scores(member_index):
    member = team_members[member_index]
    members_name = member['name']
    member_scores = [compute_composite_score(task, member_index) for task in possible_tasks]
    allocated_tasks = [task for task in possible_tasks if value(x[task, member_index]) == 1]

    colors = ['blue' if task not in allocated_tasks else 'red' for task in possible_tasks]

    plt.figure(figsize=(14, 6))
    plt.barh(list(possible_tasks.keys()), member_scores, color=colors)
    plt.xlabel('Score')
    plt.ylabel('Task')
    plt.title(f'Score Distribution for {members_name}')
    plt.show()


for i in range(len(team_members)):
    plot_member_scores(i)

window = tk.Tk()
window.title("Skills, Preferences, and Scores")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)


def display_skills_preferences_scores():
    for i, (task, value) in enumerate(possible_tasks.items()):
        task_label = tk.Label(frame, text=f"Task: {task}, Value: {value}")
        task_label.grid(row=i, column=8, sticky="w", padx=5, pady=2)

    for i, member in enumerate(team_members):
        member_label = tk.Label(frame, text=f"Member: {member['name']}")
        member_label.grid(row=i * 5, column=0, sticky="w")

        preferences_label = tk.Label(frame, text="Preferences:")
        preferences_label.grid(row=i * 5 + 1, column=2, sticky="w")

        for j, (task, preference) in enumerate(member['preferences'].items()):
            preference_label = tk.Label(frame, text=f"- {task}: Preference {preference}")
            preference_label.grid(row=i * 5 + 1 + j, column=3, sticky="w", padx=5, pady=2)

        tasks_label = tk.Label(frame, text="Allocated Tasks:")
        tasks_label.grid(row=i * 5 + 1, column=4, sticky="w")

        allocated_row = i * 5 + 2
        for j, task in enumerate(tasks[i]):
            if task:
                task_score = points[i][j]
                task_label = tk.Label(frame, text=f"- {task}: Score {task_score}")
                task_label.grid(row=allocated_row, column=5, sticky="w", padx=5, pady=2)
                allocated_row += 1

        skill_scores_label = tk.Label(frame, text="Skill Scores:")
        skill_scores_label.grid(row=i * 5 + 1, column=6, sticky="w")

        for j, (task, score) in enumerate(skill_scores[member['name']].items()):
            skill_score_label = tk.Label(frame, text=f"- {task}: Skill Score {score}")
            skill_score_label.grid(row=i * 5 + 1 + j, column=7, sticky="w", padx=5, pady=2)


display_skills_preferences_scores()

window.mainloop()

