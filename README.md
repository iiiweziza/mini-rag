# mini-rag

mini rag application for questions ansowering

## Requirments 
Python =3.8 or later
### used Packages and projects: 
#### FastAPI 

### Install Python using MiniConda
Download and install MiniConda from here

Create a new environment using the following command:
```bash
$ conda create -n mini-rag python=3.8
```
Activate the environment:
```bash
$ conda activate mini-rag
```

# files

## .gitignore => Git can specify which files or parts of your project should be ignored  
## LICENSE => You can write your license
## .env => to put environment variables (puplic and private)=> .env put in .gitignore file so git ignore it 
## .env.example => to put environment variables but to seeing in git (public)

## asset :
### .gitkeep ==> reverse of gitignore 
### postman collectin => if you want to use postman to host your web easily 

## routs:
### __init__ =>
### base => putting routs APIs details to call it from main file 





### requirements.txt 
 to install packages from the file 


 ## Install the requirements packages
 ```bash
 $ pip install -r requirements.txt 
 ```


## Setup the environment variables 

```bash 
$ cp .env.example .env
```
copy file in .env and set your private environment variables in .env 
like 'OPEN_API_KEY' value. 
 

 ## Run host by Uvicorn 

 ```bash 
 uvicorn main:app --reload --host 0.0.0.0 --port 5000
 ```
 host 0.0.0.0 => access all to the host 