import random
from datetime import datetime, timedelta

# Định nghĩa lớp GeneticAlgorithm (Thuật toán di truyền)
class GeneticAlgorithm:
    # Khởi tạo các thông tin và tham số cơ bản
    def __init__(self, num_proctors, num_rooms, num_days, num_slots_per_day, population_size, generations, mutation_rate, valid_dates):
        self.num_proctors = num_proctors  # Tổng số giám thị
        self.num_rooms = num_rooms  # Tổng số phòng
        self.num_days = num_days  # Tổng số ngày làm việc
        self.num_slots_per_day = num_slots_per_day  # Số khoảng thời gian trong mỗi ngày
        self.population_size = population_size  # Kích thước quần thể (số lượng lịch trình trong dân số)
        self.generations = generations  # Số thế hệ (iterations) cần lặp
        self.mutation_rate = mutation_rate  # Tỷ lệ đột biến trong quá trình tiến hóa
        self.valid_dates = valid_dates  # Danh sách ngày hợp lệ (nếu có)

    # Tính toán độ phù hợp (fitness) cho một lịch trình
    def calculate_fitness(self, schedule):
        fitness = 0  # Khởi điểm giá trị fitness là 0
        daily_counts = [0] * self.num_proctors  # Lưu trữ số lần làm việc của từng giám thị

        # Duyệt qua từng ngày và từng khoảng thời gian trong lịch trình
        for day in schedule:
            for slot in day:
                for room in slot:
                    # Phạt nếu phòng không có đúng 2 giám thị
                    if len(room) != 2:
                        fitness -= 10
                    # Phạt nếu trong cùng một phòng có giám thị trùng lặp
                    if len(set(room)) != len(room):
                        fitness -= 5

                # Kiểm tra các giám thị trong khoảng thời gian này
                proctors_in_slot = [proctor for room in slot for proctor in room]
                for proctor in proctors_in_slot:
                    daily_counts[proctor] += 1

                # Phạt nếu giám thị làm việc nhiều hơn một khoảng thời gian trong ngày
                if any(daily_counts[proctor] > 1 for proctor in proctors_in_slot):
                    fitness -= 10
        return fitness

    # Tạo một lịch trình ngẫu nhiên
    def create_random_schedule(self):
        schedule = []
        for _ in range(self.num_days):
            day_schedule = []
            for _ in range(self.num_slots_per_day):
                slot_schedule = []
                available_proctors = list(range(self.num_proctors))  # Tạo danh sách giám thị khả dụng
                for _ in range(self.num_rooms):
                    if len(available_proctors) < 2:
                        available_proctors = list(range(self.num_proctors))

                    # Lấy ngẫu nhiên 2 giám thị
                    room_proctors = random.sample(available_proctors, 2)
                    slot_schedule.append(room_proctors)  # Thêm vào lịch trình
                    for proctor in room_proctors:
                        available_proctors.remove(proctor)  # Loại giám thị vừa được chọn khỏi danh sách

                day_schedule.append(slot_schedule)
            schedule.append(day_schedule)
        return schedule

    # Kiểm tra và chuẩn hóa lịch trình để đảm bảo mọi phòng đều có đúng 2 giám thị
    def validate_schedule(self, schedule):
        for day in schedule:
            for slot in day:
                for room in slot:
                    # Thêm giám thị ngẫu nhiên nếu phòng thiếu giám thị
                    while len(room) < 2:
                        available_proctors = list(set(range(self.num_proctors)) - set(room))
                        room.append(random.choice(available_proctors))
                    # Cắt số giám thị thừa nếu phòng có quá 2 giám thị
                    if len(room) > 2:
                        room[:] = room[:2]
        return schedule

    # Thực hiện thao tác giao phối (crossover) giữa hai lịch trình cha
    def crossover(self, parent1, parent2):
        point = random.randint(0, self.num_days - 1)  # Chọn điểm giao phối ngẫu nhiên
        child = parent1[:point] + parent2[point:]  # Kết hợp hai lịch trình
        return self.validate_schedule(child)

    # Thực hiện thao tác đột biến trên lịch trình
    def mutate(self, schedule):
        if random.random() < self.mutation_rate:  # Kiểm tra xem có đột biến hay không
            day = random.randint(0, len(schedule) - 1)  # Chọn một ngày ngẫu nhiên
            slot = random.randint(0, len(schedule[day]) - 1)  # Chọn khoảng thời gian ngẫu nhiên
            room = random.randint(0, len(schedule[day][slot]) - 1)  # Chọn phòng ngẫu nhiên

            # Thay đổi một giám thị ngẫu nhiên trong phòng nếu có khả năng
            available_proctors = list(set(range(self.num_proctors)) - set(schedule[day][slot][room]))
            if available_proctors:
                schedule[day][slot][room][random.randint(0, 1)] = random.choice(available_proctors)

        return self.validate_schedule(schedule)

    # Thực hiện thuật toán di truyền chính
    def genetic_algorithm(self):
        # Tạo dân số ban đầu
        population = [self.validate_schedule(self.create_random_schedule()) for _ in range(self.population_size)]
        best_schedule = None
        best_fitness = float('-inf')  # Thiết lập giá trị fitness tối ưu ban đầu là vô cùng âm

        for _ in range(self.generations):  # Duyệt qua số thế hệ được chỉ định
            fitness_scores = [self.calculate_fitness(schedule) for schedule in population]  # Tính fitness cho mỗi lịch trình
            max_fitness = max(fitness_scores)  # Lấy fitness cao nhất trong dân số
            if max_fitness > best_fitness:  # Cập nhật lịch trình tốt nhất
                best_fitness = max_fitness
                best_schedule = population[fitness_scores.index(max_fitness)]

            # Thực hiện chọn lọc và tạo thế hệ mới
            new_population = [best_schedule]
            for _ in range(self.population_size // 2 - 1):
                parent1 = self.selection(population, fitness_scores)  # Lựa chọn cha 1
                parent2 = self.selection(population, fitness_scores)  # Lựa chọn cha 2
                child1 = self.mutate(self.crossover(parent1, parent2))  # Thao tác giao phối và đột biến
                child2 = self.mutate(self.crossover(parent2, parent1))
                new_population.extend([child1, child2])  # Thêm các con cái vào dân số mới

            population = new_population  # Cập nhật dân số mới

        return best_schedule

    # Lựa chọn một lịch trình từ dân số dựa vào phương pháp chọn lọc (tournament selection)
    def selection(self, population, fitness_scores):
        tournament_size = 5  # Kích thước của nhóm chọn lọc
        tournament = random.sample(range(len(population)), tournament_size)  # Lấy ngẫu nhiên một tập các cá thể
        best_individual = max(tournament, key=lambda i: fitness_scores[i])  # Chọn cá thể tốt nhất trong nhóm
        return population[best_individual]
