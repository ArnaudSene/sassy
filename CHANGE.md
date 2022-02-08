# 0.1.10
## fix: setup.py

- replace entry_point by entry_points

---
# 0.1.9
## update: setup.py

- add entry_point to declare sassy as a console_Script

---
# 0.1.8
## update: gitlab-ci

- update build-docs with same behavior as deploy-prod

---
# 0.1.7
## update: gitlab-ci add gitlab-dev

- add gitlab-dev for pypi_dev package registry
- rename main to prod 

---
# 0.1.6
## gitlab-ci update

- update names
- update rules

---
# 0.1.5
## gitlab-ci update

- new stages in gitlab-ci
- utilization of a image inside container registry

---
# 0.1.4
## New feature: 

- replace sub dir from apps name to src
- create or delete a module by selecting target directories
  - *a = applications
  - *d = domains
  - *i = interfaces
  - *p = providers
  
  ####Example:
    
    To `create` a `module_name` inside `apps_name` project for `applications` and `domains` directories 
  ```
  sassy.py apps_name module_name *a,*d --create
  ``` 


---
# 0.1.3
## code refactor

- move from os to pathlib
- limit lib import with from against import 

---
# 0.1.2
## refacto

- move all code into __init__.py file.
- rewrite logger with config file. 

---
# 0.1.1
## fix pathlib

- use pathlib to manage path

---
# 0.1.0
## apis

- Add apis to the clean architecture structure

---
# 0.0.3

- add .coveragerc
- add __init__ for tests directories

---
# 0.0.2

## Git repo

- Add git repo at structure creation

## MessageLogger

- Log messages through a decorator

## Documentation

- Update documentation

---
# 0.0.1.dev7

## Add doc with sphinx

---
# 0.0.1.dev6

## Remove a feature
  
- Remove a feature by deleting all files

---
# 0.0.1.dev5

## refacto, logging/color, feature 'feature' 
  
- code refactoring
- add feature to the clean architecture structure. 
  - The file name created as <span style="color:cyan">*FEATURE_NAME*.
    py</span> at:
    - domains
    - applications
    - interfaces
    - providers

  - The file name created as <span style="color:cyan">*test_FEATURE_NAME*.
    py</span> at:
    - tests/domains
    - tests/applications
    - tests/providers

- Add logging for console output with color depending on severity  

---
# 0.0.1.dev4

## fix 
  
- Dependency injection by using interface for Message
- add _ROOT_PATH for apps location

---
# 0.0.1.dev3

## Split sassy.pl main file and create a_sassy.pl for application. 

---
# 0.0.1.dev2

## Created sassy in TDD/clean architecture simplified

- defined domains, interface, provider and apps
- configuration with YAML file
- features:
  - new sassy.yml file
  - new messages.yml file
  - Add provider/interface for messages
  - Add domains for
    - Result
    - Message
  - create 'apps' clean architecture structure
    - create directories defined in YAML file
    - create files set defined in YAML file
  - printer decorator  
---
# 0.0.1.dev1

## Init project