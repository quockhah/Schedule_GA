import random
from datetime import datetime, timedelta

class GeneticAlgorithm:
    def __init__(self, num_proctors, num_rooms, num_days, num_slots_per_day, population_size, generations, mutation_rate, valid_dates,proctors_per_room=1):
        # Khởi tạo các biến từ tham số đầu vào
        self.num_proctors = num_proctors
        self.num_rooms = num_rooms
        self.num_days = num_days
        self.num_slots_per_day = num_slots_per_day
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.valid_dates = valid_dates 
        self.proctors_per_room = proctors_per_room
    def calculate_fitness(self, schedule):
        fitness = 0
        daily_counts = [0] * self.num_proctors
        weekly_counts = [0] * self.num_proctors  # Lưu số ca làm việc trong một tuần
        
        for day_index, day in enumerate(schedule):
            if day_index % 7 == 6:  # Bỏ qua Chủ Nhật
                continue
            
            if not day:
                fitness -= 100  # Phạt nặng nếu ngày rỗng
                continue

            daily_counts.clear()
            for slot in day:
                # Kiểm tra không có trùng lặp trong slot
                # Lấy tất cả giảng viên trong slot (phẳng nếu có danh sách giảng viên trong slot)
                proctors_in_slot = [proctor for room in slot for proctor in room]  # Làm phẳng nếu mỗi phòng có danh sách giảng viên
                if len(set(proctors_in_slot)) == len(proctors_in_slot):  # Kiểm tra trùng lặp
                    fitness += 1

                for proctor in proctors_in_slot:
                    daily_counts.append(proctor)
            
            # Kiểm tra phân công ca làm việc hợp lý trong ngày
            for proctor in daily_counts:
                if daily_counts.count(proctor) > 1:
                    fitness -= 10  # Phạt nếu giám thị làm nhiều ca trong ngày
            
            # Đảm bảo sự phân bổ giám thị hợp lý trong tuần
            if len(set(daily_counts)) != len(daily_counts):
                fitness -= 10  # Phạt nếu có giám thị làm quá nhiều ca trong tuần
            
            # Kiểm tra phân bổ đều ca làm việc
            for proctor in set(daily_counts):
                weekly_counts[proctor] += 1
    
        return fitness

    def create_random_schedule(self):
        start_date = datetime(2024, 12, 1)
        schedule = []
        
        for day in range(self.num_days):
            current_date = start_date + timedelta(days=day)
            
            if current_date.weekday() == 7:  # Chủ Nhật
                # Tạo ngày hoàn toàn không có phân công
                day_schedule = [[] for _ in range(self.num_slots_per_day)]
            else:
                # Ngày không phải Chủ Nhật
                day_schedule = []
                all_available_proctors = list(range(self.num_proctors))
                
                for _ in range(self.num_slots_per_day):
                    # Nếu không đủ giám thị, reset danh sách giám thị
                    if not all_available_proctors:
                        all_available_proctors = list(range(self.num_proctors))
                    
                    # Chọn giám thị cho slot
                    slot_proctors = []
                    for _ in range(self.num_rooms):
                        if not all_available_proctors:
                            all_available_proctors = list(range(self.num_proctors))
                        
                        # Chọn 3 giảng viên cho mỗi phòng thi
                    selected_proctors = random.sample(all_available_proctors, 2)
                    slot_proctors.append(selected_proctors)
                    
                    # Xóa các giảng viên đã chọn khỏi danh sách có sẵn
                    for proctor in selected_proctors:
                        all_available_proctors.remove(proctor)
                    
                    day_schedule.append(slot_proctors)
            
            schedule.append(day_schedule)
        
        return schedule

    def initialize_population(self):
        return [self.create_random_schedule() for _ in range(self.population_size)]

    def selection(self, population, fitness_scores):
        tournament_size = 5  # Số lượng cá thể tham gia vào mỗi vòng đấu
        tournament = random.sample(range(len(population)), tournament_size)
        best_individual = max(tournament, key=lambda i: fitness_scores[i])
        return population[best_individual]


    def validate_schedule(self, schedule):
        for day_index, day in enumerate(schedule):
            if day_index % 7 == 6:  # Chủ Nhật
                continue  # Không làm gì cả nếu là Chủ Nhật
            
            # Kiểm tra nếu một ngày không có đủ giám thị
            if not any(day):  # Nếu tất cả slot trống
                # Phân bổ giám thị lại cho các slot trống
                available_proctors = list(range(self.num_proctors))
                for slot in day:
                    for room in range(self.num_rooms):
                        if not slot:
                            proctor = random.choice(available_proctors)
                            slot.append(proctor)
                            available_proctors.remove(proctor)
            # Kiểm tra các điều kiện khác của phân công (giám thị không làm nhiều ca trong ngày)
            daily_proctors = [proctor for slot in day for proctor in slot]
            for slot in day:
                for room, proctor in enumerate(slot):
                    if daily_proctors.count(proctor) > 1:  # Giám thị này đã trực nhiều hơn 1 ca
                        available_proctors = [p for p in range(self.num_proctors) if daily_proctors.count(p) == 0]
                        if available_proctors:
                            slot[room] = random.choice(available_proctors)
                            daily_proctors = [proctor for slot in day for proctor in slot]
        return schedule


    def crossover(self, parent1, parent2):
        point = random.randint(0, self.num_days - 1)
        if point % 7 == 6:  # Tránh cắt qua ngày Chủ Nhật
            point = 5  # Đặt điểm cắt vào ngày thứ 6 (thứ Bảy)
        
        child = parent1[:point] + parent2[point:]
        # Kiểm tra và điều chỉnh lại nếu cần để đảm bảo lịch phân công hợp lý
        child = self.validate_schedule(child)
        return child

    def mutate(self, schedule):
        if random.random() < self.mutation_rate:
            day = random.randint(0, len(schedule) - 1)
            if day % 7 == 6:  # Không thay đổi lịch vào Chủ Nhật
                return schedule
            slot = random.randint(0, len(schedule[day]) - 1)
            if schedule[day][slot]:  # Kiểm tra nếu slot không rỗng
                room = random.randint(0, len(schedule[day][slot]) - 1)
                # Kiểm tra và đảm bảo giám thị làm việc hợp lý trong ngày và tuần
                schedule = self.validate_schedule(schedule)
        return schedule


    def genetic_algorithm(self):
        population = [self.validate_schedule(schedule) for schedule in self.initialize_population()]
        best_schedule = None
        best_fitness = float('-inf')

        for _ in range(self.generations):
            fitness_scores = [self.calculate_fitness(schedule) for schedule in population]
            max_fitness = max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_schedule = population[fitness_scores.index(max_fitness)]
            
            # Elitism: giữ lại cá thể tốt nhất
            new_population = [best_schedule]  # Giữ lại cá thể tốt nhất
            for _ in range(self.population_size // 2 - 1):  # Tạo thêm cá thể mới
                parent1 = self.selection(population, fitness_scores)
                parent2 = self.selection(population, fitness_scores)
                child1 = self.mutate(self.crossover(parent1, parent2))
                child2 = self.mutate(self.crossover(parent2, parent1))
                new_population.append(child1)
                new_population.append(child2)
            
            population = new_population
        
        return best_schedule