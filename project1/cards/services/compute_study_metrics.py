from datetime import datetime, timedelta
from math import ceil, exp, log


class NextReviewDate:
    """
    A class to calculate the next review date for spaced repetition learning.
    """

    def __init__(self, params=None):
        """
        Initialize the NextReviewDate object with given parameters or defaults.

        :param params: Dictionary containing 'easiness', 'interval', and 'repetitions'.
        """
        if params:
            self.easiness = params.get('easiness', 2.5)
            self.interval = params.get('interval', 0)
            self.repetitions = params.get('repetitions', 0)
        else:
            self.easiness = 2.5
            self.interval = 0
            self.repetitions = 0

    def review(self, quality: int):
        """
        Update the review metrics based on the quality of the review.

        :param quality: An integer representing the quality of recall (1-5 scale).
        :return: A tuple containing the updated parameters and the next review date.
        """
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

            self.repetitions += 1

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
    Computes the next interval for study based on the current easiness, rating, and number of repetitions.

    :param easiness: Current easiness factor.
    :param rating: User's rating of recall quality.
    :param repetitions: Number of times the item has been repeated.
    :return: Computed next interval, adjusted by easiness and repetitions.
    """
    difficulty_weight = 0.1
    repetitions_weight = 0.5
    rating_map = {3: 5, 2: 3}
    rating = rating_map.get(rating, rating)
    easiness = float(easiness) if not isinstance(easiness, float) else easiness

    difficulty_factor = exp(difficulty_weight * (5 - easiness))
    repetitions_factor = log(repetitions + 1) * repetitions_weight
    base_interval = rating / difficulty_factor
    next_easiness = base_interval / (1 + repetitions_factor)

    return min(next_easiness, 2)


def scale_easiness(easiness, current_min=0, current_max=2):
    """
    Scales the easiness value to a range between 1 and 5.

    :param easiness: The current easiness factor.
    :param current_min: The minimum easiness value.
    :param current_max: The maximum easiness value.
    :return: Scaled easiness value within the range [1, 5].
    """
    scaled_value = 1 + (easiness - current_min) * (5 - 1) / (current_max - current_min)
    return max(1, min(scaled_value, 5))


# Example usage:
params = {}
next_review = NextReviewDate(params)
review_params, review_date = next_review.review(quality=5)
# print(review_params, review_date)
