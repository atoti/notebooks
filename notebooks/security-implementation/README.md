# Securing an atoti session

Securing a session comes in two parts:

1. Implementing an authentication mechanism to secure access to the session
2. Restricting access of modules or data access by users based on the roles granted

atoti supports multiple [authentication mechanisms](https://docs.atoti.io/latest/lib/atoti/atoti.config.authentication.html) to cater to the needs of our end users.

We will explore some of these options with [atoti Business Edition](https://www.atoti.io/discover-atoti-for-business/) using the [Top 50 Fast Food](https://www.kaggle.com/datasets/stetsondone/top50fastfood) dataset from Kaggle, combined with its parent company information sourced from the internet.

---

## Environment setup

### atoti Business Edition

[atoti Business Edition](https://www.atoti.io/discover-atoti-for-business/) is required to download the additional plugin required for security implementation.

### Authentication platform

Other than Basic authentication, users will have to set up their own authentication provider in order to test run the notebooks.

Users can make use of the free services/tools to try out the various authentication providers:

- Auth0: https://auth0.com/
- Google Cloud Credential: https://cloud.google.com/
- LDAP: https://directory.apache.org/apacheds/

---

## [main.ipynb](./main.ipynb)

To understand how different authentication mechanisms vary from one another, this notebook aligns the code snippets of the following authentication mechanisms sequentially for comparison:

- Basic authentication
- OIDC via Auth0
- OIDC via Google
- LDAP

To focus on just one of the above security mechanisms, check out the following notebooks instead:

- [01-Basic-authentication.ipynb](./01-Basic-authentication.ipynb)
- [02-OIDC-Auth0.ipynb](./02-OIDC-Auth0.ipynb)
- [03-OIDC-Google.ipynb](./03-OIDC-Google.ipynb)
- [04-LDAP.ipynb](./03-OIDC-Google.ipynb)
