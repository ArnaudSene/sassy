--
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