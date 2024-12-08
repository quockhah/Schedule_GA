import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class ScheduleViewer:
    def __init__(self, root, schedule, lecturers, schedule_dates, rooms):
        self.root = root
        self.schedule = schedule
        self.lecturers = lecturers
        self.schedule_dates = schedule_dates
        self.rooms = rooms
        self.current_day = 0
        
        self.num_weeks = len(schedule_dates) // 7
        self.NUM_PROCTORS = len(self.lecturers)
        self.NUM_ROOMS = len(self.rooms)

        self.day_frame = tk.Frame(root)
        self.day_frame.pack(fill="both", expand=True)
        self.navigation_frame = tk.Frame(root)
        self.navigation_frame.pack(fill="x")
        self.prev_button = tk.Button(self.navigation_frame, text="← Ngày trước", command=self.prev_day)
        self.prev_button.pack(side="left", padx=10, pady=5)
        self.next_button = tk.Button(self.navigation_frame, text="Ngày sau →", command=self.next_day)
        self.next_button.pack(side="right", padx=10, pady=5)

        self.save_button = tk.Button(self.navigation_frame, text="Lưu lịch", command=self.save_schedule_to_file)
        self.save_button.pack(side="left", padx=10, pady=5)

        self.display_day()

    def display_day(self):
        for widget in self.day_frame.winfo_children():
            widget.destroy()

        day = self.schedule[self.current_day]
        date_str = self.schedule_dates[self.current_day].strftime("%d/%m/%Y")

        tk.Label(self.day_frame, text=f"Ngày {self.current_day + 1} ({date_str})", font=("Arial", 16, "bold")).pack(pady=20)

        table_frame = tk.Frame(self.day_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Đặt tiêu đề cột
        tk.Label(table_frame, text="Ca/Phòng", font=("Arial", 12, "bold"), anchor="center", width=12).grid(
            row=0, column=0, padx=5, pady=5
        )
        for room in range(self.NUM_ROOMS):
            tk.Label(
                table_frame, text=f"Phòng {room + 1}", font=("Arial", 12, "bold"), anchor="center", width=12
            ).grid(row=0, column=room + 1, padx=5, pady=5)

        time_slots = ["Sáng", "Chiều"]

        # Thêm các hàng trống để căn giữa nhãn "Sáng" và "Chiều"
        empty_row_count = 3
        for i in range(empty_row_count):
            tk.Label(table_frame, text="", width=12).grid(row=i + 1, column=0, padx=5, pady=5)
        # Duyệt qua từng slot trong ngày để hiển thị các giảng viên
        for slot_index, slot in enumerate(day):
            tk.Label(table_frame, text=time_slots[slot_index], font=("Arial", 12, "bold"), anchor="center", width=12).grid(
                row=empty_row_count + slot_index + 1, column=0, padx=5, pady=20
            )
            for room_index, proctor_list in enumerate(slot):
                # Ghép tên giảng viên thành một chuỗi
                lecturer_names = ", ".join([self.lecturers[proctor] for proctor in proctor_list])
                lecturer_label = tk.Label(
                    table_frame,
                    text=lecturer_names,  # Hiển thị nhiều giảng viên
                    font=("Arial", 10),
                    anchor="center",
                    width=20,  # Tăng chiều rộng của nhãn
                    height=3,  # Tăng chiều cao của nhãn
                    wraplength=150  # Điều chỉnh độ dài để chữ tự động xuống dòng
                )
                lecturer_label.grid(row=empty_row_count + slot_index + 1, column=room_index + 1, padx=5, pady=20)

    def save_schedule_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                start_date_str = self.schedule_dates[0].strftime("%d/%m/%Y")
                end_date_str = self.schedule_dates[-1].strftime("%d/%m/%Y")
                file.write(f"Lịch thi từ ngày {start_date_str} đến ngày {end_date_str}:\n")

                for day_index, day in enumerate(self.schedule):
                    date_str = self.schedule_dates[day_index].strftime("%d/%m/%Y")
                    file.write(f"Ngày {day_index + 1} ({date_str}):\n")
                    
                    for slot_index, slot in enumerate(day):
                        for room_index, proctor in enumerate(slot):
                            lecturer_name = self.lecturers[proctor]
                            file.write(f"{lecturer_name},{room_index + 1}, ")
                        file.write("\n")
                
                messagebox.showinfo("Thông báo", "Lịch thi đã được lưu thành công!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu lịch: {e}")

    def prev_day(self):
        if self.current_day > 0:
            self.current_day -= 1
            self.display_day()

    def next_day(self):
        if self.current_day < len(self.schedule) - 1:
            self.current_day += 1
            self.display_day()
