# 507-w20-final-proj-pisacha

This is Pisacha Wichianchan's final project for University of Michigan's SI 507 (Winter 2020).

Data source: https://livingwage.mit.edu/states/26/locations

About: The program obtains data on living wages and necessary expenses across Michigan's counties and metropolitan statistical areas (MSAs) from the MIT​ Living Wage Calculator.

Structure: I first set up a caching mechanism to avoid overloading the data source's server. I then scraped and crawled data and store it in a 3-table database -- in this process, the program automatically created a cache in the form of a JSON file. From this point on, every time the program proccesses data, it would read from the cache file rather than scraping and crawling anew. In the interactive portion under 'if __name__ == "__main__":', I called functions that process data from the created database. The user can enter the area of interest (e.g. county or MSA) in Michigan to find information on wages and expenses.

Purpose: The program's target audiences (i.e. users) are scholars and professionals in public policy. Its purpose is to encourage users to adopt the living wage approach in public policy analysis and management. For policymakers, this approach entails developing living wage policies for their constituents. Such policies could be raising the minimum wage to a living wage and/or implementing economic development initiatives to upskill workers for living-wage jobs.
