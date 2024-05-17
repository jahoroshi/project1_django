import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()

from math import ceil
from datetime import date, datetime, timedelta
from typing import Optional, Union

import attr

year_mon_day = "%Y-%m-%d"
mon_day_year = "%m-%d-%Y"
day_mon_year = "%d-%m-%Y"


@attr.s
class SMTwo:
    easiness = attr.ib(validator=attr.validators.instance_of(float))
    interval = attr.ib(validator=attr.validators.instance_of(int))
    repetitions = attr.ib(validator=attr.validators.instance_of(int))
    review_date = attr.ib(init=False)

    @staticmethod
    def first_review(
            quality: int,
            review_date: Optional[Union[date, str]] = None,
            date_fmt: Optional[str] = None,
    ) -> "SMTwo":
        if not review_date:
            review_date = datetime.now()

        if not date_fmt:
            date_fmt = "%Y-%m-%d %H:%M:%S"

        return SMTwo(2.5, 0, 0).review(quality, review_date, date_fmt)

    def review(
            self,
            quality: int,
            review_date: Optional[Union[date, str]] = None,
            date_fmt: Optional[str] = None,
    ) -> "SMTwo":
        if not review_date:
            review_date = datetime.now()

        if not date_fmt:
            date_fmt = "%Y-%m-%d %H:%M:%S"

        if isinstance(review_date, str):
            review_date = datetime.strptime(review_date, date_fmt)

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

        return self

    def get(self):
        return self.easiness, self.interval, self.repetitions


rep = SMTwo.first_review(2)
print(rep.get())
# rep = SMTwo(rep).review(4)
print(rep)

for i in (0.49, 4, 10, 4, 5, 5, 5, 5, 5, 5):
    repp = SMTwo(rep.easiness, rep.interval, rep.repetitions).review(i, rep.review_date)
    rep = repp

    print(i, '  ', rep)

