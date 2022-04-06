This is an extension used to customize the web app embedded in the Pokemon Project Atoti+ sessions.
The app extension template linked [here](https://docs.atoti.io/latest/lib/atoti/atoti.session.html#atoti.Session.__init__) was used as a starting point.

Build project:

    yarn

Generate `dist` folder:

    npm run build

The source code has been included for reference, but only the `dist` folder is needed for our notebook.

You can customize the current extension by changing the source code and regenerating the `dist` folder with `npm run build`.

More information about what is possible can be found in the [ActiveUI documentation](https://activeviam.com/activeui/documentation/) and [tutorial](https://activeviam.com/activeui/documentation/latest/docs/tutorial/introduction). 
In particular, development was done in the `activeui-starter-source` project from the tutorial ([link](https://activeviam.com/activeui/documentation/latest/docs/tutorial/setup)), then transferred to the app extension template for ease of development.

Read more: [Exploring OLAP with atoti and Pokemon - Part 2](https://medium.com/atoti/)
