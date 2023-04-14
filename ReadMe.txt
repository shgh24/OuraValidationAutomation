How to automate usage of the Usleep API:


Use in windows:


Here's how you can run the script using Git Bash:

1.	Install Git for Windows from the official website: https://git-scm.com/download/win if your computer does not have git.

2.	Open Git Bash by typing "git bash" into the Start menu and selecting the "Git Bash" program.

3.	Run the script using the bash command followed by the name of your script. For example, if your script is called Usleep_upload.sh, you can type:

	Usleep_upload.sh

4.	Before running the script you should change these 2 lines in the Usleep_upload.sh files, every 12 hours the API token expires and you should get a new API key from Usleep Website, change the USLEEP_API_TOKEN with the new API token, if you change the folder that data are saved you have to change the path after cd /path/to/EDF Data folder/

cd C:/Users/SCL/Desktop/TestUsleep/
export USLEEP_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NzgzNzk3NTksImlhdCI6MTY3ODMzNjU1OswibmJmIjoxNjc4MzM2NTU5LCJpZGVudGl0eSI6ImUwY2RlM2IyYzUxOSJ9.hhiQ3u5SQb6SbTtn2bSkDpdE-rTOEKj-gLkObt80Yxk


More details about the key is provided here:

Requests to any API endpoint must include an API authentication token. To obtain a token:
1.	Log in to your account at https://sleep.ai.ku.dk/login.
2.	Select "Account" and "Generate API Token" from the drop-down menu.
3.	Paste the API token into your script or create an environment variable to store the token (see details below).





Automate the task on windows computer:
To run the script automatically every morning at 10 am on your Windows computer, you can use the Windows Task Scheduler. Here's how:

1.	Open the Task Scheduler by searching for "Task Scheduler" in the Start menu.

2.	Click "Create Task" in the Actions panel on the right-hand side of the window.

3.	In the General tab, give your task a name and a description. Choose the user account under which the task will run and select "Run whether user is logged on or not".

4.	In the Triggers tab, click "New" to create a new trigger. Choose "Daily" and set the recurrence to "1 day". Set the start time to 10:00 AM.

5.	In the Actions tab, click "New" to create a new action. Choose "Start a program" as the action type. In the "Program/script" field, enter the path to the Bash executable, for example: "C:\Program Files\Git\bin\bash.exe". In the "Add arguments" field, enter the path to your script, for example: "/c/Users/YourUserName/path/to/myscript.sh".
6.	Click "OK" to save the task.




Use in mac:
1.	Save the bash script with a .sh file extension, for example, Usleep_upload.sh.
2.	To run the script, open a terminal or command prompt and navigate to the directory where the script is saved. Then, run the following command:
bash Usleep_pload.sh
3.	Alternatively, you can make the script executable by setting its execute permission using the chmod command. For example, you can run the following command to make the script executable:
4.	chmod +x Usleep_Upload.sh

5.	Bash script is here, copy and paste it to the text file via note pad or vs code, the file extension should be .sh

