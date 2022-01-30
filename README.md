# Sassy apps

A Python framework for building SaaS applications using clean architecture.


## Installation

### Halia pypi

```
pip install sassy --extra-index-url https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/31729495/packages/pypi/simple
```

## Usage 

#### Create a project

To create a new project, provide a project name:

```
python3 sassy new_project --create
```

> Note: A git repository will be created.

### Add a feature to your project

To add a feature to your project, provide a project name and a feature name.

```
python3 sassy new_project new_feature --create
```


### Delete a feature in your project

To delete a feature in your project, provide a project name and a feature name.

```
python3 sassy new_project new_feature --delete
```

## Documentation available in this repository at:
https://halia-ca.gitlab.io/sassy
