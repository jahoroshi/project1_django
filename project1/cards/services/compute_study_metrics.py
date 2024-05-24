from datetime import datetime, timedelta
from math import ceil, exp, log

import attr



class NextReviewDate:
    def __init__(self, params):
        if params:
            self.easiness = params['easiness']
            self.interval = params['interval']
            self.repetitions = params['repetitions']
        else:
            self.easiness = 2.5
            self.interval = 0
            self.repetitions = 0


    def review(self, quality: int, ):
        review_date = datetime.now()

        if quality < 3:
            self.interval = 1
            self.repetitions = 0
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = ceil(self.interval * self.easiness)

            self.repetitions = self.repetitions + 1

        self.easiness += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        if self.easiness < 1.3:
            self.easiness = 1.3

        review_date += timedelta(days=self.interval)
        self.review_date = review_date
        params = {
            'easiness': self.easiness,
            'interval': self.interval,
            'repetitions': self.repetitions
        }
        return params, review_date


def compute_study_easiness(easiness, rating, repetitions):
    """
    Вычисляет interval для следующего повторения на основе difficulty,
    текущего interval и количества repetitions.
    Возвращает interval в диапазоне от 1.0 до 5.0.
    """
    # Параметры для настройки влияния difficulty и repetitions
    difficulty_weight = 0.1
    repetitions_weight = 0.5
    rating_map = {3:5, 2:3}
    rating = rating_map.get(rating, rating)
    easiness = float(easiness) if not isinstance(easiness, float) else easiness

    difficulty_factor = exp(difficulty_weight * (5 - easiness))

    # Вычисление влияния repetitions на interval
    repetitions_factor = log(repetitions + 1) * repetitions_weight

    # Вычисление базового interval
    base_interval = rating / difficulty_factor

    # Вычисление итогового interval с учетом repetitions
    next_easiness = base_interval / (1 + repetitions_factor)

    return min(next_easiness, 2)


def scale_easiness(easiness, current_min=0, current_max=2):
    scaled_value = 1 + (easiness - current_min) * (5 - 1) / (current_max - current_min)

    return max(1, min(scaled_value, 5))




# a = 1
# b, c = 1, 1
# x = (5, 5, 2, 2, 3, 3, 3)
# for i in x:
#     a = compute_study_easiness(a, b, c)
#     # aa = max(1.0, min(a*10, 5.0))
#     aa = a / 0.355
#     # aa = max(1.0, min(aa, 5.0))
#
#     print("\033[33;40;1m  %-6s%-30s%-30s%-6s%-10s%-6s%-10s\033[0m" % ('es', aa, a, 'int', b, 'rep', c))
#
#     b = i
#     c += 1
# print(sum(x)/len(x))

# a = CalculateNextInterval.first_review(3.4)
params = {
            # 'easiness': 0,
            # 'interval': 0,
            # 'repetitions': 0
        }
a, b = NextReviewDate(params).review(5)
# print(a)
