# 507-w20-final-proj-pisacha

This is Pisacha Wichianchan's final project for University of Michigan's SI 507 (Winter 2020).


## Getting Started
**Data source:** https://livingwage.mit.edu/states/26/locations

**About:** The program obtains data on living wages and necessary expenses across Michigan's counties and metropolitan statistical areas (MSAs) from the MIT​ Living Wage Calculator.

**Structure:** I first set up a caching mechanism to avoid overloading the data source's server. I then scraped and crawled data and store it in a 3-table database -- in this process, the program automatically created a cache in the form of a JSON file. From this point on, every time the program proccesses data, it would read from the cache file rather than scraping and crawling anew. Under the "if name equals main" section, I called functions that process data from the created database. The user can select an area of interest (e.g. county or MSA) in Michigan to find information about the area's wages and expenses.

**Purpose:** The program's target audiences (i.e. users) are scholars and professionals in public policy. Its main purpose is to encourage users to adopt the living wage approach in public policy analysis and management. For policymakers, this approach entails developing living wage policies for their constituents. Such policies could be raising the minimum wage to a living wage and/or implementing economic development initiatives to upskill workers for living-wage jobs.

**Required pip installation:** Including but not limited to beautifulsoup4, requests, sqlite, plotly, and PrettyTable.


## How to interact with the program:
1) In your terminal, go to the folder in which the program file (i.e. living_wage.py) is in.
2) Enter in "python3 living_wage.py" to initiate the program. *Note: If this is your first time running the program, it may take 15 to 20 minutes for the program to completely crawl and scrape data from the source. If you've run the program before, it will only takes a few seconds for the program to call data from the cache file.
3) The program will generate a welcome message that describes the program's intent. Enter anything to continue or "exit" to leave the program.
4) Upon entering something, the program will generate a list** of counties and MSAs in Michigan, each with an assigned number. Enter a specific number to learn more about the respective county or MSA, "back" to return to the welcome message, or "exit" to leave the program.
5) Upon entering a valid number, the program will display a table** featuring the living wage, poverty wage, and minimum wage for each family composition in the selected county. The table will be displayed in the terminal.
6) The user then has the option to enter "w"** for wages, "e"** for expenses, or "exit" to leave the program. If the user enters "w", a plotly graph that displays the gap between the average living wage of the selected area and the minimum wage of Michigan as well as a caption that describes the calculated difference/gap will populate in a web browser. If the user enters "e", a plotly graph that displays the required annual income before taxes for each family composition in the selected area will populate in a web browser.
7) If the user enters either "w" or "e" in step 6, the terminal will then ask the user to enter a specific number to learn more about a specific county or MSA, "back" to return to the welcome message, or "exit" to leave the program, again, like in step 4.

** = A kind of presentation, such as displays or graphs.

**Got questions?** Contact me at pisacha@umich.edu
