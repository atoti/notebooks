This is an extension used to customize the web app embedded in the Pokemon Project <img src="https://img.shields.io/badge/🔒-Atoti-291A40" /> sessions.
The app extension template linked [here](https://docs.atoti.io/latest/_downloads/8f4997efc312e243404a2c110412528e/extension.zip) was used as a starting point.

**Note: We have compressed the dist and images of the pokemon and stored in our s3.**

1. To test with pre-build, download the [dist](https://data.atoti.io/notebooks/pokemon/dist.zip) and unzip into the `extensions` folder

2. To build the project, follow the steps below:

- Download from this [link](https://data.atoti.io/notebooks/pokemon/images.zip) and unzip into the following folders:**  
    - for new build: src/resources/images

- Build project:

    yarn

- Generate `dist` folder:

    npm run build


The source code has been included for reference, but only the `dist` folder is needed for our notebook.

You can customize the current extension by changing the source code and regenerating the `dist` folder with `npm run build`.

More information about what is possible can be found in the [ActiveUI documentation](https://activeviam.com/activeui/documentation/) and [tutorial](https://activeviam.com/activeui/documentation/latest/docs/tutorial/introduction). 
In particular, development was done in the `activeui-starter-source` project from the tutorial ([link](https://activeviam.com/activeui/documentation/latest/docs/tutorial/setup)), then transferred to the app extension template for ease of development.

Read more: [Exploring OLAP with atoti and Pokemon - Part 2](https://medium.com/atoti/exploring-olap-with-atoti-and-pokemon-c6b4a8542a69)
