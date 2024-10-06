# petbnb


## Installation
After cloning the repository, the dependencies should be installed seperately for backend and front end
 ### Back End
   Using a command line interface, (preferably the terminal of Visual Studio Code) 
   1. Navitage to the 'backend' directory
   2. enter the command '*pipenv install*'
   3. Wait for the packages to be installed
   4. After the installation is complete we need to perform migrations. Enter the command '*python manage.py makemigrations*'
      4a. Alternatively, if the migratiosn for seperate apps are not created the following set of commands can be used to create migraitons for each app:
          *python manage.py makemikrations users*
          *python manage.py makemigrations services*
          *python manage.py makemigrations reviews*
          *python manage.py makemikrations messaging*
   5. After the migrations are prepared, run the command '*python manage.py migrate*' to perform the migrations
   6. The back end should now be ready and can be started with the command 'python manage.py runserver*'
   7. After the first 6 steps are completed, they don't need to be performed again. the back end can be started by using the commands '*pipenv shell*' and 'python manage.py runserver*' while in the backend directory

### Front End
  Again, similar to the backend, using a command line interface
  1. Navigate to the 'frontend' directory
  2. Enter the command '*yarn install*'
  3. Wait for the packages to be installed
  4. After installetion is complete, the front end can be started with the command '*yarn start*'
  5. Similar to the back end, the first 4 steps are only necessary during the initial installation

## Notes
  1. For the back end to run, Python 3.12.6 should be installed in the system from https://www.python.org
  2. pipenv should be installed beforehand using the command '*pip install pipenv*'
  3. For the front end to run, node.js should be installed  from nodejs.org
  4. The backend by default runs at localhost:8000
  5. The front end by default runs at localhost:3000
  6. If these ports are to be changed, one needs to update the proper references inside the code
   
