###
# Generates n merchants per category, to be piped into demographic_data/merchants.csv
# >python static_merchant_generator.py >> ./data/merchants.csv
###
__author__ = "Brandon Harris - brandonharris.io"
from faker import Factory

n = 500

fake = Factory.create("en_US")

header = "category|merchant_name"
category_list = [
    "gas_transport",
    "grocery_net",
    "grocery_pos",
    "pharmacy",
    "misc_net",
    "misc_pos",
    "shopping_net",
    "shopping_pos",
    "utilities",
    "entertainment",
    "food_dining",
    "health_fitness",
    "home",
    "kids_pets",
    "personal_care",
    "travel",
]
print(header)

for c in category_list:
    for _ in range(0, n):
        print(c + "|" + "fraud_" + fake.company())
