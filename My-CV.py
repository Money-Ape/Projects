# Personal Information

name = "\n\033[1m\033[93mLovepreet Singh\033[0m"
address = "\033[1m\033[93mIndia, Delhi\nR-3, Block-R, Mohan Garden\nNew Delhi-110059\033[0m"
phone = "\033[1m\033[93mContact : +91 9873836147\033[0m"
email = "\033[1m\033[93mmoney.ape01@gmail.com\033[0m"
instagram = "\033[1m\033[93mInstagram Handle : \033[4m\033[94mhttps://instagram.com/money.ape.network/\033[0m"

# Objective
objective = """
\033[1m\033[4m\033[92mObjective :-\033[0m
-------------------------
\033[96mAspiring Python Developer with a strong foundation in Python programming, SQL, and problem-solving.
Seeking an internship opportunity to apply my skills and gain practical experience in a dynamic software development environment.\033[0m
"""

# Education
education = """
\033[1m\033[4m\033[92mEducation :-\033[0m
-------------------------
\033[96mBachelor of Technology (B.Tech) in Computer Science
Indraprastha Institute of Technology and Management (IITM)
Janakpuri-D Block, Janakpuri West

\033[92mRelevant Coursework :-\033[0m
- Python Programming
- Database Management with SQL
- Game Development
- Android Development\033[0m
"""

# Skills
skills = """
\033[1m\033[4m\033[92mSkills :-\033[0m
-------------------------
\033[1m\033[96mProgramming Languages\033[0m: \033[1m\033[91mPython, SQL, C++\033[0m
\033[1m\033[6mVersion Control\033[0m: \033[1m\033[91mGit\033[0m
\033[1m\033[6mDatabases\033[0m: \033[91m\033[1mMySQL\033[0m
\033[1m\033[6mProblem Solving\033[0m
"""

# Projects
# Define the projects as a list of dictionaries
projects = [
    {
        "name": "\033[96mSQL-Automation (Command-Interface-SQL-Automation)\033[0m",
        "description": "\033[96mDeveloped a Python-based Command-Interface-SQL-Automation tool similar to phpMyAdmin. Utilized SQL with the MySQL-connector to perform database operations.\033[0m",
    },
    {
        "name": "\033[96mATM-Project (Command-Interface ATM Machine)\033[0m",
        "description": "\033[96mCreated a Command-Interface ATM machine using Python and integrated it with a SQL-DBMS. Implemented essential ATM functionalities.\033[0m",
    },
    {
        "name": "\033[96mPing-Pong Game (2D Python Game)\033[0m",
        "description": "\033[96mDesigned and developed a 2D Ping-Pong game using Python and the Pygame library. Demonstrated creativity and game development skills.\033[0m",
    }
]

def cv_dic():
    project_info = ""
    project_info += ("\033[1m\033[92mMy Recent Projects :-\033[0m\n\n")
    for idx, project in enumerate(projects, start=1):
        project_info += f"\033[1m\033[92mProject\033[0m \033[1m{idx}\033[0m:\n"
        project_info += f"\033[1m\033[92mName\033[0m: {project['name']}\n"
        project_info += f"\033[1m\033[92mDescription\033[0m: {project['description']}\n\n"
    
    # Return the combined project information string
    return project_info

# Call the function and store the result in cv_project
cv_project = cv_dic()

Github_Project_link=("\033[1m\033[92mMy Github Repository for Projects : \033[4m\033[94mhttps://github.com/Money-Ape/Projects/tree/master/Python/\033[0m")

# Experience
experience = """
\n\033[1m\033[4m\033[92mExperience :-\033[0m

\033[4m\033[92mJunior Ethical Hacker\033[0m :-
-------------------------
\033[96mCyber Underground Discord Server
August 2023 - September 2023
- Collaborated with the team to solve Errors and promote community growth.\033[0m

\033[4m\033[92mDiscord Moderator\033[0m :-
-------------------------
\033[96mNerdsvana Discord Server
August 2023 - Present
- Managed and moderated the Meta-Hi Discord community, organize events, helped community members to solve their problems regarding to different programming languages.\033[0m\033[0m
"""

# References
references = """
\033[1m\033[4m\033[92mReferences :-\033[0m
-------------------------
\033[96mAvailable upon request.\033[0m
"""

# Combine all sections
cv = (
    f"{name}\n{address}\n{phone}\n{email}\n{instagram}\n\n{objective}\n{education}\n{skills}\n{cv_project}\n{Github_Project_link}\n{experience}\n{references}"
)

# Print the CV
print(cv)
