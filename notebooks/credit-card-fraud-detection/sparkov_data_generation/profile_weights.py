from __future__ import division
import json
import sys
import datetime
from datetime import date, datetime
from datetime import timedelta
import random
import numpy as np
from faker import Faker
import calendar
import time


class Profile:
    def __init__(self, pro, start, end):
        self.profile = pro
        self.start = start
        self.end = end
        # form profile so it can be sampled from
        self.make_weights()

    def json_to_dict(self):
        self.profile = json.loads(
            json.dumps(self.profile, separators=(", ", ": "))
            .replace("\\n", "")
            .replace("\\t", "")
            .replace("\\", "")
            .replace('"{', "{")
            .replace('}"', "}")
        )

    # turn dict into cumulative sum key
    # with entry value so we can sample
    def weight_to_cumsum(self, cat):
        wt_tot = sum(self.profile[cat].values())
        cumsum = 0
        for k in self.profile[cat]:
            cumsum += self.profile[cat][k] / float(wt_tot)
            self.profile[cat][k] = cumsum
        # invert
        self.profile[cat] = {self.profile[cat][k]: k for k in self.profile[cat]}

    def weight_to_prop(self, profile_cat):
        wt_tot = sum(profile_cat.values())
        return {k: profile_cat[k] / float(wt_tot) for k in profile_cat.keys()}

    # ensures all weekdays are covered,
    # converts weekday names to ints 0-6
    # and turns from weights to log probabilities
    def prep_weekday(self):
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        # create dict of day:weight using integer day values
        weekdays = {
            day_map[day]: self.profile["date_wt"]["day_of_week"][day]
            for day in self.profile["date_wt"]["day_of_week"].keys()
        }
        # replace any missing weekdays with 100
        for d in [
            day_map[day]
            for day in day_map.keys()
            if day not in self.profile["date_wt"]["day_of_week"].keys()
        ]:
            weekdays[d] = 100

        self.profile["date_wt"]["day_of_week"] = self.weight_to_prop(weekdays)

    # take the time_of_year entries and turn into date tuples
    def date_tuple(self):
        holidays = self.profile["date_wt"]["time_of_year"]
        date_tuples = []
        for hol in holidays:
            start = None
            end = None
            weight = None
            for k in holidays[hol].keys():
                if "start" in k:
                    curr_date = holidays[hol][k].split("-")
                    start = date(2000, int(curr_date[0]), int(curr_date[1]))
                elif "end" in k:
                    curr_date = holidays[hol][k].split("-")
                    end = date(2000, int(curr_date[0]), int(curr_date[1]))
                elif "weight" in k:
                    weight = holidays[hol][k]
            if start == None or end == None or weight == None:
                sys.stderr.write(
                    "Start or end date not found for time_of_year: " + str(hol) + "\n"
                )
                sys.exit(0)
            elif start > end:
                sys.stderr.write(
                    "Start date after end date for time_of_year: " + str(hol) + "\n"
                )
                sys.exit(0)
            date_tuples.append({"start": start, "end": end, "weight": weight})
        return date_tuples

    def prep_holidays(self):
        days = {}
        # all month/day combos (including leap day)
        init = date(2000, 1, 1)
        # initialize all to 100
        for i in range(366):
            curr = init + timedelta(days=i)
            days[(curr.month, curr.day)] = 100
        # change weights for holidays
        holidays = self.date_tuple()
        for h in holidays:
            while h["start"] <= h["end"]:
                days[(h["start"].month, h["start"].day)] = h["weight"]
                h["start"] += timedelta(days=1)

        # need separate weights for non-leap years
        days_nonleap = {k: days[k] for k in days.keys() if k != (2, 29)}
        # get proportions for all month/day combos
        self.profile["date_wt"]["time_of_year"] = self.weight_to_prop(days_nonleap)
        self.profile["date_wt"]["time_of_year_leap"] = self.weight_to_prop(days)

    # checks number of years and converts
    # to proportions
    def prep_years(self):
        final_year = {}
        # extract years to have transactions for
        years = [y for y in range(self.start.year, self.end.year + 1)]
        years.sort()
        # extract years provided in profile
        years_wt = [y for y in self.profile["date_wt"]["year"].keys()]
        years_wt.sort()
        # sync weights to extracted years
        for i, y in enumerate(years):
            if years_wt[i] in self.profile["date_wt"]["year"]:
                final_year[y] = self.profile["date_wt"]["year"][years_wt[i]]
            # if not enough years provided, make it 100
            else:
                final_year[y] = 100
        self.profile["date_wt"]["year"] = self.weight_to_prop(final_year)

    def combine_date_params(self):
        new_date_weights = {}
        weights = self.profile["date_wt"]
        curr = self.start
        while curr <= self.end:
            # leap year:
            if curr.year % 4 == 0:
                time_name = "time_of_year_leap"
            else:
                time_name = "time_of_year"

            date_wt = (
                weights["year"][curr.year]
                * weights[time_name][(curr.month, curr.day)]
                * weights["day_of_week"][curr.weekday()]
            )

            new_date_weights[curr] = date_wt
            curr += timedelta(days=1)
        # re-weight to get proportions
        self.profile["date_wt"] = self.weight_to_prop(new_date_weights)

    def date_weights(self):
        self.prep_weekday()
        self.prep_holidays()
        self.prep_years()
        self.combine_date_params()
        self.weight_to_cumsum("date_wt")

    # convert dates from weights to %
    def make_weights(self):
        # convert profile to a dict
        self.json_to_dict()
        # convert weights to proportions and use
        # the cumsum as the key from which to sample
        self.weight_to_cumsum("categories_wt")
        self.weight_to_cumsum("shopping_time")  ###BRANDON
        self.date_weights()

    def closest_rand(self, pro, num):
        return pro[min([k for k in pro.keys() if k > num])]

    def sample_amt(self, category):
        shape = (
            self.profile["categories_amt"][category]["mean"] ** 2
            / self.profile["categories_amt"][category]["stdev"] ** 2
        )
        scale = (
            self.profile["categories_amt"][category]["stdev"] ** 2
            / self.profile["categories_amt"][category]["mean"]
        )
        while True:
            amt = np.random.gamma(shape, scale, 1)[0]

            # seeing lots of <$1.00 charges, hacky fix even though it breaks the gamma distribution
            if amt < 1:
                amt = np.random.uniform(1.00, 10.00)
                return str("{:.2f}".format(amt))
            if amt >= 1:
                return str("{:.2f}".format(amt))

    def sample_time(self, am_or_pm, is_fraud):

        if is_fraud == 0:

            if am_or_pm == "AM":
                hour = random.randrange(0, 12, 1)
            if am_or_pm == "PM":
                hour = random.randrange(12, 24, 1)

            mins = random.randrange(60)
            secs = random.randrange(60)
            time_stamp = (
                str(hour).zfill(2) + ":" + str(mins).zfill(2) + ":" + str(secs).zfill(2)
            )

        if is_fraud == 1:

            # 20% chance that the fraud will still occur during normal hours
            chance = random.randint(1, 100)
            if chance <= 20:

                if am_or_pm == "AM":
                    hour = random.randrange(0, 12, 1)
                if am_or_pm == "PM":
                    hour = random.randrange(12, 24, 1)

                mins = random.randrange(60)
                secs = random.randrange(60)
                time_stamp = (
                    str(hour).zfill(2)
                    + ":"
                    + str(mins).zfill(2)
                    + ":"
                    + str(secs).zfill(2)
                )

            else:
                if am_or_pm == "AM":
                    hour = random.randrange(0, 4, 1)
                if am_or_pm == "PM":
                    hour = random.randrange(22, 24, 1)

                mins = random.randrange(60)
                secs = random.randrange(60)
                time_stamp = (
                    str(hour).zfill(2)
                    + ":"
                    + str(mins).zfill(2)
                    + ":"
                    + str(secs).zfill(2)
                )

        return time_stamp

    # def sample_from(self, inputCat):
    def sample_from(self, is_fraud):
        fake = Faker()
        # randomly sample number of transactions
        num_trans = int(
            (self.end - self.start).days
            * np.random.random_integers(
                self.profile["avg_transactions_per_day"][
                    "min"
                ],  ## need normal, not uniform
                self.profile["avg_transactions_per_day"]["max"],
            )
        )

        # randomly determine if customer is traveling based off of profile travel_pct param
        # if np.random.uniform() < self.profile['travel_pct']/100:
        #     is_traveling = True
        # else:
        #     is_traveling = False
        travel_max = self.profile["travel_max_dist"]
        # travel_max=1
        is_traveling = False

        output = []
        rand_date = np.random.random(num_trans)
        rand_cat = np.random.random(num_trans)

        fraud_dates = []
        for i, num in enumerate(rand_date):
            trans_num = fake.md5(raw_output=False)
            chosen_date = self.closest_rand(self.profile["date_wt"], num)
            if is_fraud == 1:
                fraud_dates.append(chosen_date.strftime("%Y-%m-%d"))
            chosen_cat = self.closest_rand(self.profile["categories_wt"], rand_cat[i])
            chosen_amt = self.sample_amt(chosen_cat)
            chosen_daypart = self.closest_rand(
                self.profile["shopping_time"], rand_cat[i]
            )
            stamp = self.sample_time(chosen_daypart, is_fraud)
            unix_time = datetime.strptime(
                str((chosen_date.strftime("%Y-%m-%d") + " " + stamp)),
                "%Y-%m-%d %H:%M:%S",
            ).timetuple()
            epoch = str(calendar.timegm((unix_time)))
            # if str(chosen_cat) == inputCat:
            output.append(
                "|".join(
                    [
                        str(trans_num),
                        chosen_date.strftime("%Y-%m-%d"),
                        stamp,
                        str(epoch),
                        str(chosen_cat),
                        str(chosen_amt),
                        str(is_fraud),
                    ]
                )
            )
            # else:
            #    pass
        return output, is_traveling, travel_max, fraud_dates
