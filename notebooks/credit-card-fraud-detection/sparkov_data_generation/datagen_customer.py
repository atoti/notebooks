import faker
from faker import Faker
import random
import numpy as np
import sys
import datetime
from datetime import date
from datetime import timedelta
import fileinput
import random
from collections import defaultdict
import json
import sparkov_data_generation.demographics as demographics
from sparkov_data_generation.main_config import MainConfig
import pandas as pd


class Headers:
    "Store the headers and print to stdout to pipe into csv"

    def __init__(self):
        self.header = [
            "ssn",
            "cc_num",
            "first",
            "last",
            "gender",
            "street",
            "city",
            "state",
            "zip",
            "lat",
            "long",
            "city_pop",
            "job",
            "dob",
            "acct_num",
            "profile",
        ]
        self.make_headers()

    def make_headers(self):
        headers = ""
        for h in self.header:
            headers += h + "|"
        self.headers = headers[:-1]

    def print_headers(self):
        print(self.headers)

    def fetch_headers(self):
        return self.header


class Customer:
    "Randomly generates all the attirubtes for a customer"

    def __init__(self, fake, headers, cities, age_gender, all_profiles):
        self.ssn = fake.ssn()
        self.gender, self.dob = self.generate_age_gender(fake, age_gender)
        self.first = self.get_first_name(fake)
        self.last = fake.last_name()
        self.street = fake.street_address()
        self.addy = self.get_random_location(cities)
        self.job = fake.job()
        self.cc = fake.credit_card_number()
        self.email = fake.email()
        self.account = fake.random_number(digits=12)
        self.profile = self.find_profile(all_profiles)

    #         self.print_customer()

    def get_first_name(self, fake):
        if self.gender == "M":
            return fake.first_name_male()
        else:
            return fake.first_name_female()

    def generate_age_gender(self, fake, age_gender):
        # g_a = age_gender[min([a for a in age_gender if a > np.random.random()])]
        # g_a = age_gender[min(age_gender, key=lambda x:abs(x-random.random()))]

        a = np.random.random()
        c = []
        for b in age_gender.keys():
            if b > a:
                c.append(b)
        g_a = age_gender[min(c)]

        while True:
            dob = fake.date_time_this_century()

            # adjust the randomized date to yield the correct age
            start_age = (date.today() - date(dob.year, dob.month, dob.day)).days / 365.0
            dob_year = dob.year - int(g_a[1] - int(start_age))

            # since the year is adjusted, sometimes Feb 29th won't be a day
            # in the adjusted year
            try:
                # return first letter of gender and dob
                return g_a[0][0], date(dob_year, dob.month, dob.day)
            except:
                pass

    # find nearest city
    def get_random_location(self, cities):
        return cities[min(cities, key=lambda x: abs(x - random.random()))]

    def find_profile(self, all_profiles):
        age = (date.today() - self.dob).days / 365.25
        city_pop = float(self.addy.split("|")[-1])

        match = []
        for pro in all_profiles:
            # -1 represents infinity
            if (
                self.gender in all_profiles[pro]["gender"]
                and age >= all_profiles[pro]["age"][0]
                and (
                    age < all_profiles[pro]["age"][1]
                    or all_profiles[pro]["age"][1] == -1
                )
                and city_pop >= all_profiles[pro]["city_pop"][0]
                and (
                    city_pop < all_profiles[pro]["city_pop"][1]
                    or all_profiles[pro]["city_pop"][1] == -1
                )
            ):
                match.append(pro)
        if match == []:
            match.append("leftovers.json")

        # found overlap -- write to log file but continue
        if len(match) > 1:
            f = open("profile_overlap_warnings.log", "a")
            output = (
                " ".join(match)
                + ": "
                + self.gender
                + " "
                + str(age)
                + " "
                + str(city_pop)
                + "\n"
            )
            f.write(output)
            f.close()
        return match[0]

    def print_customer(self):
        print(
            str(self.ssn)
            + "|"
            + str(self.cc)
            + "|"
            + self.first
            + "|"
            + self.last
            + "|"
            + self.gender
            + "|"
            + self.street
            + "|"
            + self.addy
            + "|"
            + self.job
            + "|"
            + str(self.dob)
            + "|"
            + str(self.account)
            + "|"
            + self.profile
        )

    def fetch_customer(self):
        return (
            str(self.ssn)
            + "|"
            + str(self.cc)
            + "|"
            + self.first
            + "|"
            + self.last
            + "|"
            + self.gender
            + "|"
            + self.street
            + "|"
            + self.addy
            + "|"
            + self.job
            + "|"
            + str(self.dob)
            + "|"
            + str(self.account)
            + "|"
            + self.profile
        ).split("|")


def generate_customers(fake, num_cust, profile_config):
    ## m = 'profiles/main_config.json'
    main = open(profile_config, "r").read()

    # from demographics module
    cities = demographics.make_cities()
    age_gender = demographics.make_age_gender_dict()

    headers = Headers()

    # turn all profiles into dicts to work with
    all_profiles = MainConfig(main).config

    cust_list = []
    for _ in range(num_cust):
        cust = Customer(fake, headers, cities, age_gender, all_profiles)
        cust_dtl = cust.fetch_customer()
        cust_list.append(cust_dtl)

    cust_df = pd.DataFrame(cust_list, columns=headers.fetch_headers())
    return cust_df
