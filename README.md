# 507-w20-final-proj-pisacha

This is Pisacha Wichianchan's final project for University of Michigan's SI 507 (Winter 2020).

**Data source:** https://livingwage.mit.edu/states/26/locations

**About:** The program obtains data on living wages and necessary expenses across Michigan's counties and metropolitan statistical areas (MSAs) from the MIT​ Living Wage Calculator.

**Structure:** I first set up a caching mechanism to avoid overloading the data source's server. I then scraped and crawled data and store it in a 3-table database -- in this process, the program automatically created a cache in the form of a JSON file. From this point on, every time the program proccesses data, it would read from the cache file rather than scraping and crawling anew. In the interactive portion under 'if name equals main', I called functions that process data from the created database. The user can enter the area of interest (e.g. county or MSA) in Michigan to find information on wages and expenses.

**Purpose:** The program's target audiences (i.e. users) are scholars and professionals in public policy. Its purpose is to encourage users to adopt the living wage approach in public policy analysis and management. For policymakers, this approach entails developing living wage policies for their constituents. Such policies could be raising the minimum wage to a living wage and/or implementing economic development initiatives to upskill workers for living-wage jobs.

**How to interact with the program:**
1) In your terminal, go to the folder in which the program file (i.e. living_wage.py) is in.
2) Type in 'python3 living_wage.py' to initiate the program.
3) The program will generates a welcome message that describes the program's intent. Enter anything to continue or 'exit' to leave the program.
4) Upon entering something, the program will generate a list of counties and MSAs in Michigan, each with an assigned number. Enter a specific number to learn more about the respective county or MSA, "back" to return to the welcome message, or "exit" to leave the program.
5) Upon entering a valid number, the program will display a table featuring the living wage, poverty wage, and minimum wage for each family composition in the selected county. The table will be displayed in the terminal.
6) The user then has the option to enter "w" for wages, "e" for expenses, or "exit" to leave the program.
 


README is included in repo containing special requirements and required packages (including “None” if appropriate), as well as brief instructions for how to interact with your program.
