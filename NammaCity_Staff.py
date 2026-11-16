import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


APP_DIR = Path.home() / "NammaCity"
DATA_FILE = APP_DIR / "namma_city_data.json"
STATUSES = ("Submitted", "Acknowledged", "In Progress", "Resolved")


class StaffDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Namma City — Staff Dashboard")
        self.root.geometry("1120x760")
        self.root.minsize(900, 600)
        self.data = {"reports": [], "feedback": []}

        self.build_ui()
        self.reload_data()

    def build_ui(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#183b35")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        header = tk.Frame(self.root, bg="#173f38", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="NAMMA CITY · STAFF DASHBOARD", bg="#173f38",
            fg="white", font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=22, pady=16)

        content = ttk.Frame(self.root, padding=18)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="Staff workspace", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            content,
            text="Review citizen feedback, track complaints and assign workers to civic issues.",
        ).pack(anchor="w", pady=(4, 12))

        summary = ttk.Frame(content)
        summary.pack(fill="x", pady=(0, 12))
        self.total_label = ttk.Label(summary, text="Total complaints: 0", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(side="left", padx=(0, 24))
        self.open_label = ttk.Label(summary, text="Open: 0", font=("Segoe UI", 11, "bold"))
        self.open_label.pack(side="left", padx=(0, 24))
        self.resolved_label = ttk.Label(summary, text="Resolved: 0", font=("Segoe UI", 11, "bold"))
        self.resolved_label.pack(side="left")
        ttk.Button(summary, text="Refresh", command=self.reload_data).pack(side="right")

        self.tabs = ttk.Notebook(content)
        self.tabs.pack(fill="both", expand=True)
        self.reports_tab = ttk.Frame(self.tabs, padding=12)
        self.feedback_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.reports_tab, text="Complaints & Assignments")
        self.tabs.add(self.feedback_tab, text="Citizen Reviews & Feedback")

        self.build_reports_tab()
        self.build_feedback_tab()

    def build_reports_tab(self):
        columns = ("id", "issue", "location", "priority", "status", "worker")
        self.report_tree = ttk.Treeview(
            self.reports_tab, columns=columns, show="headings", height=11
        )
        headings = {
            "id": ("Report ID", 100), "issue": ("Issue", 170),
            "location": ("Location", 190), "priority": ("Priority", 75),
            "status": ("Status", 120), "worker": ("Assigned worker", 150),
        }
        for column, (title, width) in headings.items():
            self.report_tree.heading(column, text=title)
            self.report_tree.column(column, width=width, anchor="w")
        self.report_tree.pack(fill="both", expand=True)
        self.report_tree.bind("<<TreeviewSelect>>", self.show_report)

        details = ttk.LabelFrame(self.reports_tab, text="Selected complaint", padding=10)
        details.pack(fill="x", pady=(12, 0))
        self.report_details = tk.Text(details, height=4, wrap="word", state="disabled")
        self.report_details.pack(fill="x", pady=(0, 8))

        controls = ttk.Frame(details)
        controls.pack(fill="x")
        ttk.Label(controls, text="Assign worker").pack(side="left")
        self.worker_entry = ttk.Entry(controls, width=28)
        self.worker_entry.pack(side="left", padx=(8, 18))
        ttk.Label(controls, text="Status").pack(side="left")
        self.status_var = tk.StringVar(value=STATUSES[0])
        self.status_combo = ttk.Combobox(
            controls, textvariable=self.status_var, values=STATUSES,
            state="readonly", width=18
        )
        self.status_combo.pack(side="left", padx=8)
        ttk.Button(
            controls, text="Save assignment and status", command=self.save_report
        ).pack(side="right")

    def build_feedback_tab(self):
        columns = ("rating", "topic", "name", "date")
        self.feedback_tree = ttk.Treeview(
            self.feedback_tab, columns=columns, show="headings", height=12
        )
        headings = {
            "rating": ("Rating", 100), "topic": ("Topic", 220),
            "name": ("Citizen", 200), "date": ("Submitted", 200),
        }
        for column, (title, width) in headings.items():
            self.feedback_tree.heading(column, text=title)
            self.feedback_tree.column(column, width=width, anchor="w")
        self.feedback_tree.pack(fill="both", expand=True)
        self.feedback_tree.bind("<<TreeviewSelect>>", self.show_feedback)

        details = ttk.LabelFrame(self.feedback_tab, text="Citizen feedback", padding=10)
        details.pack(fill="x", pady=(12, 0))
        self.feedback_details = tk.Text(details, height=5, wrap="word", state="disabled")
        self.feedback_details.pack(fill="x")

    def load_data(self):
        if not DATA_FILE.exists():
            self.data = {"reports": [], "feedback": []}
            return True

        try:
            with DATA_FILE.open("r", encoding="utf-8") as data_file:
                saved = json.load(data_file)
        except (json.JSONDecodeError, OSError) as error:
            messagebox.showerror("Data error", f"Could not read {DATA_FILE}:\n{error}")
            return False

        if not isinstance(saved, dict):
            messagebox.showerror("Data error", "The saved Namma City data is not a JSON object.")
            return False

        reports = saved.get("reports", [])
        feedback = saved.get("feedback", [])
        if not isinstance(reports, list) or not isinstance(feedback, list):
            messagebox.showerror("Data error", "Reports and feedback must be lists in the saved data.")
            return False

        self.data = {"reports": reports, "feedback": feedback}
        return True

    def reload_data(self):
        if self.load_data():
            self.refresh_views()

    def refresh_views(self):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        for report in self.data["reports"]:
            self.report_tree.insert(
                "", "end", iid=str(report.get("id", "")),
                values=(
                    report.get("id", ""), report.get("category", ""),
                    report.get("location", ""), report.get("priority", ""),
                    report.get("status", "Submitted"),
                    report.get("assigned_worker", ""),
                ),
            )

        for item in self.feedback_tree.get_children():
            self.feedback_tree.delete(item)
        for index, feedback in enumerate(self.data["feedback"]):
            self.feedback_tree.insert(
                "", "end", iid=str(index),
                values=(
                    f"{feedback.get('rating', 0)}/5", feedback.get("topic", ""),
                    feedback.get("name", "Anonymous citizen"),
                    feedback.get("created_at", ""),
                ),
            )

        reports = self.data["reports"]
        resolved = sum(report.get("status") == "Resolved" for report in reports)
        self.total_label.config(text=f"Total complaints: {len(reports)}")
        self.open_label.config(text=f"Open: {len(reports) - resolved}")
        self.resolved_label.config(text=f"Resolved: {resolved}")
        self.clear_text(self.report_details)
        self.clear_text(self.feedback_details)
        self.worker_entry.delete(0, "end")
        self.status_var.set(STATUSES[0])

    @staticmethod
    def set_text(widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    @staticmethod
    def clear_text(widget):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.config(state="disabled")

    def selected_report(self):
        selection = self.report_tree.selection()
        if not selection:
            return None
        report_id = selection[0]
        return next(
            (report for report in self.data["reports"] if str(report.get("id", "")) == report_id),
            None,
        )

    def show_report(self, event=None):
        if event is not None and event.widget is not self.report_tree:
            return
        report = self.selected_report()
        if not report:
            return
        self.worker_entry.delete(0, "end")
        self.worker_entry.insert(0, report.get("assigned_worker", ""))
        status = report.get("status", "Submitted")
        self.status_var.set(status if status in STATUSES else STATUSES[0])
        self.set_text(
            self.report_details,
            f"{report.get('id', '')} — {report.get('category', '')}\n"
            f"Location: {report.get('location', '')}\n"
            f"Description: {report.get('description', '')}",
        )

    def save_report(self):
        selection = self.report_tree.selection()
        if not selection:
            messagebox.showwarning("Select a complaint", "Choose a complaint before saving.")
            return
        if not self.load_data():
            return

        report_id = selection[0]
        report = next(
            (item for item in self.data["reports"] if str(item.get("id", "")) == report_id),
            None,
        )
        if report is None:
            messagebox.showerror("Complaint not found", "Refresh the dashboard and select the complaint again.")
            return

        worker = self.worker_entry.get().strip()
        if worker:
            report["assigned_worker"] = worker
        report["status"] = self.status_var.get()

        try:
            APP_DIR.mkdir(exist_ok=True)
            with DATA_FILE.open("w", encoding="utf-8") as data_file:
                json.dump(self.data, data_file, indent=2, ensure_ascii=False)
        except OSError as error:
            messagebox.showerror("Save error", f"Could not save the complaint update:\n{error}")
            return

        self.refresh_views()

    def show_feedback(self, event=None):
        if event is not None and event.widget is not self.feedback_tree:
            return
        selection = self.feedback_tree.selection()
        if not selection:
            return
        feedback = self.data["feedback"][int(selection[0])]
        self.set_text(
            self.feedback_details,
            f"{feedback.get('rating', 0)} / 5 stars — {feedback.get('topic', '')}\n"
            f"From: {feedback.get('name', 'Anonymous citizen')}\n"
            f"Date: {feedback.get('created_at', '')}\n\n"
            f"{feedback.get('message', '')}",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = StaffDashboard(root)
    root.mainloop()
