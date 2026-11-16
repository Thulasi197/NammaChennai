import json
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / "NammaCity"
DATA_FILE = APP_DIR / "namma_city_data.json"
CATEGORIES = [
    "Water Leakage", "Garbage Overflow", "Damaged Road",
    "Broken Streetlight", "Infrastructure Defect", "Other"
]
PRIORITY = {
    "Water Leakage": 92, "Damaged Road": 81,
    "Garbage Overflow": 64, "Broken Streetlight": 58,
    "Infrastructure Defect": 76, "Other": 50
}


def now_text():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


class NammaCityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Namma City — Smart Civic Reporting")
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        APP_DIR.mkdir(exist_ok=True)
        self.data = self.load_data()
        self.selected_rating = 0
        self.report_photo = ""
        self.after_photo = ""

        self.setup_style()
        self.build_header()
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.home_tab = ttk.Frame(self.tabs, padding=18)
        self.report_tab = ttk.Frame(self.tabs, padding=18)
        self.reports_tab = ttk.Frame(self.tabs, padding=18)
        self.map_tab = ttk.Frame(self.tabs, padding=18)
        self.work_tab = ttk.Frame(self.tabs, padding=18)
        self.feedback_tab = ttk.Frame(self.tabs, padding=18)

        for frame, title in [
            (self.home_tab, "Home"), (self.report_tab, "Report Issue"),
            (self.reports_tab, "My Reports"), (self.map_tab, "Live Map"),
            (self.work_tab, "Work Updates"), (self.feedback_tab, "Rate & Feedback")
        ]:
            self.tabs.add(frame, text=title)

        self.build_home()
        self.build_report()
        self.build_reports()
        self.build_map()
        self.build_work()
        self.build_feedback()
        self.refresh_all()

    def load_data(self):
        if DATA_FILE.exists():
            try:
                with DATA_FILE.open("r", encoding="utf-8") as f:
                    saved = json.load(f)
                return {
                    "reports": saved.get("reports", []),
                    "feedback": saved.get("feedback", [])
                }
            except (json.JSONDecodeError, OSError):
                pass
        return {"reports": [], "feedback": []}

    def save_data(self):
        try:
            with DATA_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            messagebox.showerror("Save error", f"Could not save data:\n{e}")

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook.Tab", padding=(15, 9), font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#183b35")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#5d6b67")
        style.configure("Card.TLabelframe", padding=14)
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def build_header(self):
        header = tk.Frame(self.root, bg="#173f38", height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="NAMMA CITY", bg="#173f38", fg="white",
                 font=("Segoe UI", 19, "bold")).pack(side="left", padx=(22, 12), pady=16)
        tk.Label(header, text="SMART CIVIC REPORTING", bg="#173f38", fg="#c5ded5",
                 font=("Segoe UI", 9, "bold")).pack(side="left", pady=22)
        tk.Label(header, text="HELPLINE NUMBER - DIAL 1004", bg="#173f38", fg="#f4d27a",
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=22)

    def heading(self, parent, title, subtitle):
        ttk.Label(parent, text=title, style="Title.TLabel").pack(anchor="w", pady=(2, 4))
        ttk.Label(parent, text=subtitle, style="Sub.TLabel", wraplength=900).pack(anchor="w", pady=(0, 18))

    def build_home(self):
        p = self.home_tab
        self.heading(p, "Make your city work better.",
                     "Report civic problems, follow every fix and help your neighbourhood stay informed.")
        hero = ttk.LabelFrame(p, text="WELCOME TO NAMMA CITY", style="Card.TLabelframe")
        hero.pack(fill="x", pady=(0, 14))
        ttk.Label(hero, text="A simple place to report local civic issues.",
                  font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=5)
        ttk.Label(hero, text="1. Snap & report     2. Smart priority     3. Community confirmation     4. Repair with proof",
                  wraplength=900).pack(anchor="w", pady=6)
        actions = ttk.Frame(hero)
        actions.pack(anchor="w", pady=10)
        ttk.Button(actions, text="Report an issue", style="Accent.TButton",
                   command=lambda: self.tabs.select(self.report_tab)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="View my reports",
                   command=lambda: self.tabs.select(self.reports_tab)).pack(side="left")
        stats = ttk.Frame(p)
        stats.pack(fill="x")
        self.home_stats = []
        for label in ("Reports submitted", "In progress", "Resolved", "Community ratings"):
            box = ttk.LabelFrame(stats, text=label, style="Card.TLabelframe")
            box.pack(side="left", fill="both", expand=True, padx=(0, 8))
            value = ttk.Label(box, text="0", font=("Segoe UI", 20, "bold"), foreground="#1c6657")
            value.pack(anchor="w")
            self.home_stats.append(value)
        note = ttk.LabelFrame(p, text="How it works", style="Card.TLabelframe")
        note.pack(fill="x", pady=16)
        for text in [
            "01  Submit the category, location and a short description.",
            "02  The prototype assigns a suggested priority score based on the selected category.",
            "03  Track report status in My Reports.",
            "04  Staff can add repair notes and an after-work photo in Work Updates."
        ]:
            ttk.Label(note, text=text).pack(anchor="w", pady=4)

    def build_report(self):
        p = self.report_tab
        self.heading(p, "Tell us what needs fixing.",
                     "Add the issue details below. Location and description are required.")
        form = ttk.LabelFrame(p, text="01 · ISSUE DETAILS", style="Card.TLabelframe")
        form.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Issue category").grid(row=0, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.category_var, values=CATEGORIES,
                     state="readonly", width=38).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        ttk.Label(form, text="Location").grid(row=1, column=0, sticky="w", pady=5)
        self.location_entry = ttk.Entry(form, width=55)
        self.location_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        ttk.Label(form, text="Describe the problem").grid(row=2, column=0, sticky="nw", pady=5)
        self.description_text = tk.Text(form, width=65, height=5, font=("Segoe UI", 10), wrap="word")
        self.description_text.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        evidence = ttk.LabelFrame(p, text="02 · PHOTO EVIDENCE (OPTIONAL)", style="Card.TLabelframe")
        evidence.pack(fill="x", pady=(0, 12))
        self.report_photo_label = ttk.Label(evidence, text="No photo selected")
        self.report_photo_label.pack(side="left", padx=5)
        ttk.Button(evidence, text="Choose photo", command=self.choose_report_photo).pack(side="right")
        buttons = ttk.Frame(p)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Submit civic report", style="Accent.TButton",
                   command=self.submit_report).pack(side="left")
        self.priority_label = ttk.Label(buttons, text="Suggested priority: — / 100")
        self.priority_label.pack(side="left", padx=18)
        self.category_var.trace_add("write", self.update_priority)

    def update_priority(self, *_):
        score = PRIORITY.get(self.category_var.get(), 0)
        self.priority_label.config(text=f"Suggested priority: {score if score else '—'} / 100")

    def choose_report_photo(self):
        path = filedialog.askopenfilename(title="Choose issue photo",
                    filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")])
        if path:
            self.report_photo = path
            self.report_photo_label.config(text=Path(path).name)

    def submit_report(self):
        category = self.category_var.get().strip()
        location = self.location_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        if not category or not location or not description:
            messagebox.showwarning("Missing details", "Please choose a category and enter the location and description.")
            return
        report_id = f"NC-{random.randint(1000, 9999)}"
        while any(r["id"] == report_id for r in self.data["reports"]):
            report_id = f"NC-{random.randint(1000, 9999)}"
        report = {
            "id": report_id, "category": category, "location": location,
            "description": description, "created_at": now_text(),
            "photo": self.report_photo, "after_photo": "",
            "resolution_notes": "", "resolved_at": "",
            "status": "Submitted", "confirmations": 1,
            "priority": PRIORITY.get(category, 50)
        }
        self.data["reports"].insert(0, report)
        self.save_data()
        self.category_var.set("")
        self.location_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")
        self.report_photo = ""
        self.report_photo_label.config(text="No photo selected")
        self.update_priority()
        self.refresh_all()
        messagebox.showinfo("Report submitted", f"Your report {report_id} was submitted.")
        self.tabs.select(self.reports_tab)

    def build_reports(self):
        p = self.reports_tab
        self.heading(p, "Follow every fix.", "Your reports remain visible from submission to resolution.")
        cols = ("id", "category", "location", "priority", "status", "created")
        self.reports_tree = ttk.Treeview(p, columns=cols, show="headings", height=14)
        headings = {"id":"Report ID", "category":"Issue", "location":"Location",
                    "priority":"Priority", "status":"Status", "created":"Submitted"}
        widths = {"id":100, "category":175, "location":180, "priority":75, "status":120, "created":160}
        for c in cols:
            self.reports_tree.heading(c, text=headings[c])
            self.reports_tree.column(c, width=widths[c], anchor="w")
        self.reports_tree.pack(fill="both", expand=True)
        self.report_detail = tk.Text(p, height=6, wrap="word", state="disabled", font=("Segoe UI", 9))
        self.report_detail.pack(fill="x", pady=(12, 0))
        self.reports_tree.bind("<<TreeviewSelect>>", self.show_report_detail)

    def show_report_detail(self, _=None):
        selected = self.reports_tree.selection()
        if not selected:
            return
        report_id = selected[0]
        r = next((x for x in self.data["reports"] if x["id"] == report_id), None)
        if not r:
            return
        text = (f"{r['id']} — {r['category']}\\nLocation: {r['location']}\\n"
                f"Description: {r['description']}\\nStatus: {r['status']}\\n"
                f"Priority: {r['priority']}/100\\nRepair notes: {r.get('resolution_notes') or 'Not resolved yet'}\\n"
                f"Before photo: {r.get('photo') or 'Not attached'}\\nAfter photo: {r.get('after_photo') or 'Not attached'}")
        self.report_detail.config(state="normal")
        self.report_detail.delete("1.0", "end")
        self.report_detail.insert("1.0", text)
        self.report_detail.config(state="disabled")

    def build_map(self):
        p = self.map_tab
        self.heading(p, "See what your neighbourhood needs.",
                     "This is a report-location list for the desktop prototype, not a GPS map.")
        self.map_list = ttk.Treeview(p, columns=("category", "location", "status", "priority"),
                                     show="headings", height=16)
        for c, label, width in [
            ("category", "Issue", 220), ("location", "Reported location", 300),
            ("status", "Status", 150), ("priority", "Priority", 100)
        ]:
            self.map_list.heading(c, text=label)
            self.map_list.column(c, width=width, anchor="w")
        self.map_list.pack(fill="both", expand=True)
        ttk.Label(p, text="Tip: add an accurate street or landmark in the report location field.",
                  style="Sub.TLabel").pack(anchor="w", pady=10)

    def build_work(self):
        p = self.work_tab
        self.heading(p, "Show the work is done.",
                     "Select an unresolved report, add repair notes and attach an after-repair photo.")
        form = ttk.LabelFrame(p, text="REPAIR PROOF", style="Card.TLabelframe")
        form.pack(fill="x")
        ttk.Label(form, text="Reported issue").grid(row=0, column=0, sticky="w", pady=7)
        self.work_report_var = tk.StringVar()
        self.work_combo = ttk.Combobox(form, textvariable=self.work_report_var, state="readonly", width=65)
        self.work_combo.grid(row=0, column=1, sticky="w", padx=10, pady=7)
        ttk.Label(form, text="Repair notes").grid(row=1, column=0, sticky="nw", pady=7)
        self.work_notes = tk.Text(form, width=65, height=4, wrap="word", font=("Segoe UI", 10))
        self.work_notes.grid(row=1, column=1, sticky="w", padx=10, pady=7)
        self.after_photo_label = ttk.Label(form, text="No after-work photo selected")
        self.after_photo_label.grid(row=2, column=1, sticky="w", padx=10, pady=7)
        ttk.Button(form, text="Choose after photo", command=self.choose_after_photo).grid(row=2, column=0, sticky="w", pady=7)
        ttk.Button(form, text="Save repair proof & resolve", style="Accent.TButton",
                   command=self.complete_work).grid(row=3, column=1, sticky="w", padx=10, pady=12)
        history = ttk.LabelFrame(p, text="REPAIR VERIFICATION TRAIL", style="Card.TLabelframe")
        history.pack(fill="x", pady=16)
        for line in ("01  Original complaint and report ID",
                     "02  After-work photo evidence",
                     "03  Repair notes and resolution date",
                     "04  Location history can help identify repeat issues"):
            ttk.Label(history, text=line).pack(anchor="w", pady=4)

    def choose_after_photo(self):
        path = filedialog.askopenfilename(title="Choose after-repair photo",
                    filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")])
        if path:
            self.after_photo = path
            self.after_photo_label.config(text=Path(path).name)

    def complete_work(self):
        label = self.work_report_var.get()
        if not label:
            messagebox.showwarning("Choose a report", "Select an unresolved report first.")
            return
        report_id = label.split(" | ")[0]
        notes = self.work_notes.get("1.0", "end").strip()
        if not notes or not self.after_photo:
            messagebox.showwarning("Missing repair proof", "Add repair notes and choose an after-work photo.")
            return
        r = next((x for x in self.data["reports"] if x["id"] == report_id), None)
        if not r:
            messagebox.showerror("Not found", "That report could not be found.")
            return
        r["after_photo"] = self.after_photo
        r["resolution_notes"] = notes
        r["resolved_at"] = now_text()
        r["status"] = "Resolved"
        self.save_data()
        self.work_notes.delete("1.0", "end")
        self.after_photo = ""
        self.after_photo_label.config(text="No after-work photo selected")
        self.refresh_all()
        messagebox.showinfo("Resolved", f"Repair proof saved. {report_id} is now resolved.")

    def build_feedback(self):
        p = self.feedback_tab
        self.heading(p, "Help us make Namma City better.",
                     "Rate your experience from 1 to 5 stars and share a suggestion.")
        form = ttk.LabelFrame(p, text="CITIZEN REVIEW", style="Card.TLabelframe")
        form.pack(fill="x", pady=(0, 14))
        ttk.Label(form, text="Your rating").grid(row=0, column=0, sticky="w", pady=5)
        stars = ttk.Frame(form)
        stars.grid(row=0, column=1, sticky="w")
        self.star_buttons = []
        for n in range(1, 6):
            b = ttk.Button(stars, text="☆", width=3, command=lambda x=n: self.choose_rating(x))
            b.pack(side="left", padx=2)
            self.star_buttons.append(b)
        self.rating_hint = ttk.Label(form, text="Select a rating.")
        self.rating_hint.grid(row=1, column=1, sticky="w")
        ttk.Label(form, text="Name (optional)").grid(row=2, column=0, sticky="w", pady=5)
        self.feedback_name = ttk.Entry(form, width=45)
        self.feedback_name.grid(row=2, column=1, sticky="w", padx=8, pady=5)
        ttk.Label(form, text="Feedback about").grid(row=3, column=0, sticky="w", pady=5)
        self.feedback_topic = tk.StringVar()
        topics = ["Reporting an issue", "Map and location", "Issue status and updates",
                  "Staff response", "Desktop app design and usability", "Other suggestion"]
        ttk.Combobox(form, textvariable=self.feedback_topic, values=topics,
                     state="readonly", width=42).grid(row=3, column=1, sticky="w", padx=8, pady=5)
        ttk.Label(form, text="Custom feedback").grid(row=4, column=0, sticky="nw", pady=5)
        self.feedback_message = tk.Text(form, width=60, height=4, wrap="word", font=("Segoe UI", 10))
        self.feedback_message.grid(row=4, column=1, sticky="w", padx=8, pady=5)
        ttk.Button(form, text="Submit rating & feedback", style="Accent.TButton",
                   command=self.submit_feedback).grid(row=5, column=1, sticky="w", padx=8, pady=10)
        self.feedback_summary = ttk.Label(p, text="No ratings yet.")
        self.feedback_summary.pack(anchor="w", pady=5)
        self.feedback_list = tk.Listbox(p, height=6)
        self.feedback_list.pack(fill="both", expand=True)

    def choose_rating(self, rating):
        self.selected_rating = rating
        for i, button in enumerate(self.star_buttons, 1):
            button.config(text="★" if i <= rating else "☆")
        self.rating_hint.config(text=f"You selected {rating} out of 5 stars.")

    def submit_feedback(self):
        topic = self.feedback_topic.get().strip()
        message = self.feedback_message.get("1.0", "end").strip()
        if not self.selected_rating or not topic or not message:
            messagebox.showwarning("Missing feedback", "Select a rating, choose a topic and enter your feedback.")
            return
        self.data["feedback"].insert(0, {
            "rating": self.selected_rating,
            "name": self.feedback_name.get().strip() or "Anonymous citizen",
            "topic": topic, "message": message, "created_at": now_text()
        })
        self.data["feedback"] = self.data["feedback"][:100]
        self.save_data()
        self.selected_rating = 0
        self.feedback_name.delete(0, "end")
        self.feedback_topic.set("")
        self.feedback_message.delete("1.0", "end")
        for b in self.star_buttons:
            b.config(text="☆")
        self.rating_hint.config(text="Select a rating.")
        self.refresh_all()
        messagebox.showinfo("Thank you", "Your rating and feedback have been saved.")

    def refresh_all(self):
        reports = self.data["reports"]
        for tree in (self.reports_tree, self.map_list):
            for item in tree.get_children():
                tree.delete(item)
        for r in reports:
            self.reports_tree.insert("", "end", iid=r["id"],
                values=(r["id"], r["category"], r["location"], r["priority"], r["status"], r["created_at"]))
            self.map_list.insert("", "end", values=(r["category"], r["location"], r["status"], r["priority"]))
        unresolved = [r for r in reports if r["status"] != "Resolved"]
        self.work_combo["values"] = [
            f"{r['id']} | {r['category']} | {r['location']}" for r in unresolved
        ]
        if self.work_report_var.get() not in self.work_combo["values"]:
            self.work_report_var.set("")
        total = len(reports)
        in_progress = sum(r["status"] == "In Progress" for r in reports)
        resolved = sum(r["status"] == "Resolved" for r in reports)
        self.home_stats[0].config(text=str(total))
        self.home_stats[1].config(text=str(in_progress))
        self.home_stats[2].config(text=str(resolved))
        self.home_stats[3].config(text=str(len(self.data["feedback"])))
        ratings = self.data["feedback"]
        if ratings:
            avg = sum(x["rating"] for x in ratings) / len(ratings)
            self.feedback_summary.config(text=f"Community rating: {avg:.1f}/5  •  {len(ratings)} rating(s)")
        else:
            self.feedback_summary.config(text="No ratings yet.")
        self.feedback_list.delete(0, "end")
        for item in ratings:
            self.feedback_list.insert("end",
                f"{'★' * item['rating']}  {item['topic']} — {item['message'][:100]} ({item['name']})")


if __name__ == "__main__":
    root = tk.Tk()
    app = NammaCityApp(root)
    root.mainloop()
