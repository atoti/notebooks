## Generate Fake Credit Card Transaction Data, Including Fraudulent Transactions

### General Usage
* Create customers data file (see generate_customers.bat for syntax)
* Create transactions, utilizing prior customer file (see various .sh/.bat for syntax)

This code is heavily modified, but based on original code by [Josh Plotkin](https://github.com/joshplotkin/data_generation). Change log of modifications to original code are below.

### Modifications:

#### v 0.4
* Only surface-level changes done in scripts so that simulation can be done using Python3
* Corrected bat files to generate transactions files.

#### v 0.3
* Completely re-worked profiles / segementation of customers
* introduced fraudulent transactions
* introduced fraudulent profiles
* modification of transaction amount generation via Gamma distribution
* added 150k_ shell scripts for multi-threaded data generation (one python process for each segment launched in the background)

#### v 0.2
* Added unix time stamp for transactions for easier programamtic evaluation.
* Individual profiles modified so that there is more variation in the data.
* Modified random generation of age/gender. Original code did not appear to work correctly?
* Added batch files for windows users

#### v 0.1
* Transaction times are now included instead of just dates
* Profile specific spending windows (AM/PM with weighting of transaction times)
* Merchant names (specific to spending categories) are now included (along with code for generation)
* Travel probability is added, with profile specific options
* Travel max distances is added, per profile option
* Merchant location is randomized based on home location and profile travel probabilities
* Simulated transaction numbers via faker MD5 hash (replacing sequential 0..n numbering)
* Includes credit card number via faker
* improved cross-platform file path compatibility
