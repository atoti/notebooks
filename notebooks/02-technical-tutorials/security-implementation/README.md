# Securing an Atoti session

Securing a session comes in two parts:

1. Implementing an authentication mechanism to secure access to the session
2. Restricting access of modules or data access by users based on the roles granted

Atoti supports multiple [authentication mechanisms](https://docs.atoti.io/latest/lib/atoti/atoti.config.authentication.html) to cater to the needs of our end users.

We will explore some of these options with [<img src="https://img.shields.io/badge/🔒-Atoti-291A40" />](https://docs.atoti.io/latest/how_tos/unlock_all_features.html#) using the [Top 50 Fast Food](https://www.kaggle.com/datasets/stetsondone/top50fastfood) dataset from Kaggle, combined with its parent company information sourced from the internet.

---

## Environment setup

### <img src="https://img.shields.io/badge/🔒-Atoti-291A40" />  

[Atoti](https://docs.atoti.io) is ActiveViam’s unified platform for enterprise data analysis.
[Unlock all the features of Atoti](https://docs.atoti.io/latest/how_tos/unlock_all_features.html#) to implement security. [Request for a trial license online](https://atoti.io/evaluation-license-request/) to give it a try!

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
- [04-LDAP.ipynb](./04-LDAP.ipynb)
