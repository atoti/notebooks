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
import demographics
from main_config import MainConfig


class Headers:
    "Store the headers and print to stdout to pipe into csv"

    def __init__(self):
        self.make_headers()
        self.print_headers()

    def make_headers(self):
        headers = ""
        for h in [
            "ssn",
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
            "dob_day",
            "dob_month",
            "dob_year",
            "acct_num",
            "profile",
        ]:
            headers += h + "|"
        self.headers = headers[:-1]

    def print_headers(self):
        print(self.headers)


class Customer:
    "Randomly generates all the attirubtes for a customer"

    def __init__(self):
        self.ssn = fake.ssn()
        self.gender, self.dob = self.generate_age_gender()
        self.first = self.get_first_name()
        self.last = fake.last_name()
        self.street = fake.street_address()
        self.addy = self.get_random_location()
        self.job = fake.job().replace(",", "")

        # skipping CC for now
        # self.cc = fake.credit_card_full()
        self.email = fake.email()
        self.account = fake.random_number()
        self.print_customer()

    def get_first_name(self):
        if self.gender == "M":
            return fake.first_name_male()
        else:
            return fake.first_name_female()

    def generate_age_gender(self):
        g_a = age_gender[min(age_gender, key=lambda x: abs(x - random.random()))]

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
    def get_random_location(self):
        return cities[min(cities, key=lambda x: abs(x - random.random()))]

    def print_customer(self):
        print(
            str(self.ssn)
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
            + str(self.dob.day)
            + "|"
            + str(self.dob.month)
            + "|"
            + str(self.dob.year)
            + "|"
            + str(self.account)
        )


def validate():
    def print_err(n):
        if n == 1:
            print("Error: invalid number of customers")
        elif n == 2:
            print("Error: invalid (non-integer) random seed")
        else:
            print("Error: main.config could not be opened")

        output = "\nENTER:\n (1) Number of customers\n "
        output += "(2) Random seed (int)\n "
        output += "(3) main_config.json"

        print(output)
        sys.exit(0)

    try:
        num_cust = int(sys.argv[1])
    except:
        print_err(1)
    try:
        seed_num = int(sys.argv[2])
    except:
        print_err(2)
    try:
        m = sys.argv[3]
        main = open(m, "r").read()

    except:
        print_err(3)

    return num_cust, seed_num, main


if __name__ == "__main__":
    # read and validate stdin
    num_cust, seed_num, main = validate()

    # from demographics module
    cities = demographics.make_cities()
    age_gender = demographics.make_age_gender_dict()

    fake = Faker()
    fake.seed(seed_num)

    headers = Headers()

    # turn all profiles into dicts to work with
    all_profiles = MainConfig(main).config

    print(all_profiles)

    # for _ in range(num_cust):
    # 	Customer()
