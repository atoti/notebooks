from __future__ import division
import random
import pandas as pd
from pandas import *
import json
import numpy as np
import sys
import datetime
from datetime import timedelta, datetime, date
import math
from random import sample
from random import randint
from faker import Faker

from sparkov_data_generation import profile_weights


def create_header(headers):
    #     headers = line.split('|')
    #     headers[-1] = headers[-1].replace('\n','')
    headers.extend(
        [
            "trans_num",
            "trans_date",
            "trans_time",
            "unix_time",
            "category",
            "amt",
            "is_fraud",
            "merchant",
            "merch_lat",
            "merch_long",
        ]
    )
    #     print(''.join([h + '|' for h in headers])[:-1])
    return headers


class Customer:
    def __init__(self, customer, profile):
        self.customer = customer
        #         self.attrs = self.clean_line(self.customer)
        self.fraud_dates = []

    def print_trans(self, trans, is_fraud, fraud_dates, merch, fake):
        is_traveling = trans[1]
        travel_max = trans[2]

        txn_list = []

        for t in trans[0]:
            ## Get transaction location details to generate appropriate merchant record
            groups = t.split("|")
            trans_cat = groups[4]
            merch_filtered = merch[merch["category"] == trans_cat]
            random_row = merch_filtered.loc[
                random.sample(list(merch_filtered.index), 1)
            ]
            ##sw added list
            chosen_merchant = random_row.iloc[0]["merchant_name"]

            cust_lat = self.customer["lat"]
            cust_long = self.customer["long"]
            cust_str = ("|").join(
                self.customer[["ssn", "cc_num", "acct_num", "profile"]].values.tolist()
            )

            if is_traveling:
                # hacky math.. assuming ~70 miles per 1 decimal degree of lat/long
                # sorry for being American, you're on your own for kilometers.
                rad = (float(travel_max) / 100) * 1.43

                # geo_coordinate() uses uniform distribution with lower = (center-rad), upper = (center+rad)
                merch_lat = fake.coordinate(center=float(cust_lat), radius=rad)
                merch_long = fake.coordinate(center=float(cust_long), radius=rad)
            else:
                # otherwise not traveling, so use 1 decimial degree (~70mile) radius around home address
                rad = 1
                merch_lat = fake.coordinate(center=float(cust_lat), radius=rad)
                merch_long = fake.coordinate(center=float(cust_long), radius=rad)

            if is_fraud == 0 and groups[1] not in fraud_dates:
                # if cust.attrs['profile'] == "male_30_40_smaller_cities.json":
                cust_str = (
                    cust_str
                    + "|"
                    + t
                    + "|"
                    + str(chosen_merchant)
                    + "|"
                    + str(merch_lat)
                    + "|"
                    + str(merch_long)
                )
                #                 print(cust_str)
                txn_list.append(cust_str.split("|"))

            if is_fraud == 1:
                cust_str = (
                    cust_str
                    + "|"
                    + t
                    + "|"
                    + str(chosen_merchant)
                    + "|"
                    + str(merch_lat)
                    + "|"
                    + str(merch_long)
                )
                #                 print(cust_str)
                #                 print("=================")
                txn_list.append(cust_str.split("|"))

        return txn_list


def generate_transactions(customers, profile_name, start, end):
    # read user input into Inputs object
    # to prepare the user inputs

    base_dir = "./sparkov_data_generation/profiles/"

    customers_header = ["ssn", "cc_num", "acct_num", "profile"]
    headers = create_header(customers_header)

    pro = open(base_dir + profile_name, "r").read()
    pro_fraud = open(base_dir + "fraud_" + profile_name, "r").read()

    # generate Faker object to calc merchant transaction locations
    fake = Faker()

    txns = pd.DataFrame(columns=headers)
    # for each customer, if the customer fits this profile
    # generate appropriate number of transactions
    #     for line in customers[1:]:
    for index, row in customers.iterrows():
        profile = profile_weights.Profile(pro, start, end)
        cust = Customer(row, profile)

        if row["profile"] == profile_name:
            merch = pd.read_csv(
                "sparkov_data_generation/data_template/merchants.csv", sep="|"
            )
            is_fraud = 0

            fraud_flag = randint(
                0, 100
            )  # set fraud flag here, as we either gen real or fraud, not both for
            # the same day.
            fraud_dates = []

            # decide if we generate fraud or not
            if fraud_flag < 99:  # 11->25
                fraud_interval = randint(1, 1)  # 7->1
                inter_val = (end - start).days - 7
                # rand_interval is the random no of days to be added to start date
                rand_interval = 1 if inter_val <= 0 else randint(1, inter_val)
                # random start date is selected
                newstart = start + timedelta(days=rand_interval)
                # based on the fraud interval , random enddate is selected
                newend = newstart + timedelta(days=fraud_interval)
                # we assume that the fraud window can be between 1 to 7 days #7->1
                profile = profile_weights.Profile(pro_fraud, newstart, newend)
                cust = Customer(row, profile)
                merch = pd.read_csv(
                    "sparkov_data_generation/data_template/merchants.csv", sep="|"
                )
                is_fraud = 1
                temp_tx_data = profile.sample_from(is_fraud)
                fraud_dates = temp_tx_data[3]

                cust_txns = cust.print_trans(
                    temp_tx_data, is_fraud, fraud_dates, merch, fake
                )
                cust_txns_df = pd.DataFrame(cust_txns, columns=headers)
                txns = txns.append(cust_txns_df, ignore_index=True)
                # parse_index = m.index('profiles/') + 9
                # m = m[:parse_index] +'fraud_' + m[parse_index:]

            # we're done with fraud (or didn't do it) but still need regular transactions
            # we pass through our previously selected fraud dates (if any) to filter them
            # out of regular transactions
            profile = profile_weights.Profile(pro, start, end)
            merch = pd.read_csv(
                "sparkov_data_generation/data_template/merchants.csv", sep="|"
            )
            is_fraud = 0
            temp_tx_data = profile.sample_from(is_fraud)
            cust_txns = cust.print_trans(
                temp_tx_data, is_fraud, fraud_dates, merch, fake
            )
            cust_txns_df = pd.DataFrame(cust_txns, columns=headers)
            txns = txns.append(cust_txns_df, ignore_index=True)

    return txns
