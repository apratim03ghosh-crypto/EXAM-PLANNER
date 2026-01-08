import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict


class ExamScheduler:
    def __init__(self):
        # Graph where each course is a node, edges mean conflict
        self.graph = defaultdict(set)
        self.courses = set()

    def add_course(self, course):
        """Add a course to the scheduler."""
        self.courses.add(course)

    def remove_course(self, course):
        """Remove a course from the scheduler."""
        if course in self.courses:
            self.courses.remove(course)
            if course in self.graph:
                del self.graph[course]
            for neighbors in self.graph.values():
                neighbors.discard(course)

    def add_conflict(self, course1, course2):
        """Add a conflict between two courses."""
        self.graph[course1].add(course2)
        self.graph[course2].add(course1)
        self.courses.update([course1, course2])

    def schedule_exams(self):
        """Assigns time slots using greedy graph coloring.

        Constraint: at most two courses can be scheduled in the same time slot,
        provided they do not conflict with each other.
        """
        if not self.courses:
            return {}
        
        # Sort courses by number of conflicts (degree)
        sorted_courses = sorted(self.courses, key=lambda c: len(self.graph[c]), reverse=True)
        time_slots = {}
        slot_counts = defaultdict(int)  # number of courses assigned per slot

        for course in sorted_courses:
            # slots already used by conflicting neighbors
            assigned_slots = {time_slots[neighbor] for neighbor in self.graph[course] if neighbor in time_slots}
            slot = 1
            # find the lowest slot that's not used by a neighbor and has capacity (<2)
            while slot in assigned_slots or slot_counts[slot] >= 2:
                slot += 1
            time_slots[course] = slot
            slot_counts[slot] += 1

        return time_slots


class ExamPlannerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Planner")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.scheduler = ExamScheduler()
        self.schedule_result = {}
        
        # Pre-load example data
        self.load_example_data()
        
        self.setup_ui()

    def load_example_data(self):

        # Add CSE/IT courses
        self.scheduler.add_course("Maths(CSE/IT)")
        self.scheduler.add_course("Physics(CSE/IT)")
        self.scheduler.add_course("Basic Electrical Engineering(CSE/IT)")
        self.scheduler.add_course("English(CSE/IT)")

        # Add CT courses
        self.scheduler.add_course("Programming for Problem solving(CT)")
        self.scheduler.add_course("Maths(CT)")
        self.scheduler.add_course("Chemistry(CT)")
        self.scheduler.add_course("Electronics(CT)")

        # Define conflicts among CSE/IT courses
        self.scheduler.add_conflict("Maths(CSE/IT)", "Physics(CSE/IT)")
        self.scheduler.add_conflict("Maths(CSE/IT)", "Basic Electrical Engineering(CSE/IT)")
        self.scheduler.add_conflict("Basic Electrical Engineering(CSE/IT)", "Physics(CSE/IT)")
        self.scheduler.add_conflict("English(CSE/IT)", "Maths(CSE/IT)")
        self.scheduler.add_conflict("Physics(CSE/IT)", "English(CSE/IT)")
        self.scheduler.add_conflict("Basic Electrical Engineering(CSE/IT)", "English(CSE/IT)")

        # Define conflicts among CT courses
        self.scheduler.add_conflict("Programming for Problem solving(CT)", "Maths(CT)")
        self.scheduler.add_conflict("Programming for Problem solving(CT)", "Chemistry(CT)")
        self.scheduler.add_conflict("Maths(CT)", "Electronics(CT)")
        self.scheduler.add_conflict("Maths(CT)", "Chemistry(CT)")
        self.scheduler.add_conflict("Electronics(CT)", "Programming for Problem solving(CT)")
        self.scheduler.add_conflict("Chemistry(CT)", "Electronics(CT)")

        # Define conflicts between CSE/IT and CT courses
        self.scheduler.add_conflict("Maths(CT)", "Maths(CSE/IT)")

    def setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = tk.Label(self.root, text="📚 Exam Planner", font=("Arial", 20, "bold"), bg="#74e4a6", fg="#333")
        title_label.pack(pady=10)

        # Main container with two columns
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for input
        left_panel = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Right panel for results
        right_panel = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # ===== LEFT PANEL =====
        left_title = tk.Label(left_panel, text="Add Course", font=("Arial", 12, "bold"), bg="white", fg="#333")
        left_title.pack(pady=5)

        # Add course input
        course_frame = tk.Frame(left_panel, bg="white")
        course_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(course_frame, text="Course Name:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.course_input = tk.Entry(course_frame, width=25)
        self.course_input.pack(side=tk.LEFT, padx=5)
        
        tk.Button(course_frame, text="Add", command=self.add_course, bg="#4B1FEB", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        tk.Button(course_frame, text="Remove", command=self.remove_selected_course, bg="#4B1FEB", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        # List of courses
        courses_title = tk.Label(left_panel, text="Courses:", font=("Arial", 10, "bold"), bg="white", fg="#333")
        courses_title.pack(padx=10, pady=(10, 5))

        self.courses_listbox = tk.Listbox(left_panel, height=8, width=40, font=("Arial", 9))
        self.courses_listbox.pack(padx=10, pady=5)

        courses_scrollbar = tk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.courses_listbox.config)
        courses_scrollbar.pack(side=tk.RIGHT, padx=(0, 10), fill=tk.Y)
        self.courses_listbox.config(yscrollcommand=courses_scrollbar.set)

        # Add conflict section
        conflict_title = tk.Label(left_panel, text="Add Conflict", font=("Arial", 12, "bold"), bg="white", fg="#333")
        conflict_title.pack(pady=(15, 5))

        course1_frame = tk.Frame(left_panel, bg="white")
        course1_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(course1_frame, text="Course 1:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.conflict_course1 = tk.Entry(course1_frame, width=25)
        self.conflict_course1.pack(side=tk.LEFT, padx=5)

        course2_frame = tk.Frame(left_panel, bg="white")
        course2_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(course2_frame, text="Course 2:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.conflict_course2 = tk.Entry(course2_frame, width=25)
        self.conflict_course2.pack(side=tk.LEFT, padx=5)

        add_conflict_btn = tk.Button(left_panel, text="Add Conflict", command=self.add_conflict, bg="#FF9800", fg="white", font=("Arial", 9), width=20)
        add_conflict_btn.pack(pady=10)

        # Generate schedule button
        generate_btn = tk.Button(left_panel, text="Generate Schedule", command=self.generate_schedule, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=25, height=2)
        generate_btn.pack(pady=15, padx=10)

        # Reset button
        reset_btn = tk.Button(left_panel, text="Clear All & Reset", command=self.reset, bg="#f44336", fg="white", font=("Arial", 9), width=20)
        reset_btn.pack(pady=5, padx=10)

        # ===== RIGHT PANEL =====
        result_title = tk.Label(right_panel, text="Exam Schedule", font=("Arial", 12, "bold"), bg="white", fg="#333")
        result_title.pack(pady=5)

        # Results display
        self.result_text = scrolledtext.ScrolledText(right_panel, height=25, width=50, font=("Courier", 9), bg="#f9f9f9")
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.update_courses_list()
        self.display_initial_schedule()

    def add_course(self):
        """Add a course."""
        course_name = self.course_input.get().strip()
        if not course_name:
            messagebox.showwarning("Input Error", "Please enter a course name.")
            return
        
        if course_name in self.scheduler.courses:
            messagebox.showinfo("Info", "Course already exists.")
            return
        
        self.scheduler.add_course(course_name)
        self.course_input.delete(0, tk.END)
        self.update_courses_list()
        messagebox.showinfo("Success", f"Course '{course_name}' added successfully.")

    def remove_selected_course(self):
        """Remove the selected course from the listbox."""
        selection = self.courses_listbox.curselection()
        if not selection:
           messagebox.showwarning("Selection Error", "Please select a course to remove.")
           return
    
        course_name = self.courses_listbox.get(selection[0])
        self.scheduler.remove_course(course_name)
        self.update_courses_list()
        messagebox.showinfo("Success", f"Course '{course_name}' removed successfully.")

    def add_conflict(self):
        """Add a conflict between two courses."""
        course1 = self.conflict_course1.get().strip()
        course2 = self.conflict_course2.get().strip()

        if not course1 or not course2:
            messagebox.showwarning("Input Error", "Please enter both course names.")
            return

        if course1 == course2:
            messagebox.showwarning("Input Error", "A course cannot conflict with itself.")
            return

        if course1 not in self.scheduler.courses or course2 not in self.scheduler.courses:
            messagebox.showwarning("Input Error", "One or both courses don't exist. Add them first.")
            return

        self.scheduler.add_conflict(course1, course2)
        self.conflict_course1.delete(0, tk.END)
        self.conflict_course2.delete(0, tk.END)
        messagebox.showinfo("Success", f"Conflict added between '{course1}' and '{course2}'.")

    def generate_schedule(self):
        """Generate and display the exam schedule."""
        if not self.scheduler.courses:
            messagebox.showwarning("No Data", "Please add courses first.")
            return

        self.schedule_result = self.scheduler.schedule_exams()
        self.display_schedule()

    def update_courses_list(self):
        """Update the courses listbox."""
        self.courses_listbox.delete(0, tk.END)
        for course in sorted(self.scheduler.courses):
            self.courses_listbox.insert(tk.END, course)

    def display_schedule(self):
        """Display the exam schedule."""
        self.result_text.delete(1.0, tk.END)
        
        if not self.schedule_result:
            self.result_text.insert(tk.END, "No schedule generated yet.\n\nClick 'Generate Schedule' to create one.")
            return

        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, "EXAM SCHEDULE\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")

        # Group by time slot
        slot_dict = defaultdict(list)
        for course, slot in self.schedule_result.items():
            slot_dict[slot].append(course)

        for slot in sorted(slot_dict.keys()):
            self.result_text.insert(tk.END, f"⏰ TIME SLOT {slot}:\n")
            for course in sorted(slot_dict[slot]):
                self.result_text.insert(tk.END, f"   • {course}\n")
            self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"Total Time Slots: {len(slot_dict)}\n")
        self.result_text.insert(tk.END, f"Total Courses: {len(self.schedule_result)}\n")

    def display_initial_schedule(self):
        """Display initial schedule from example data."""
        self.schedule_result = self.scheduler.schedule_exams()
        self.display_schedule()

    def reset(self):
        """Reset everything."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data and reset?"):
            self.scheduler = ExamScheduler()
            self.schedule_result = {}
            self.course_input.delete(0, tk.END)
            self.conflict_course1.delete(0, tk.END)
            self.conflict_course2.delete(0, tk.END)
            self.update_courses_list()
            self.load_example_data()
            self.display_initial_schedule()
            messagebox.showinfo("Reset", "All data cleared. Example data reloaded.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamPlannerUI(root)
    root.mainloop()

