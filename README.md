# Sassy apps

A Python framework for building SaaS applications using clean architecture.


## Installation

### Install sassy

```
pip install sassy
```

## Usage 

#### Create a project

To create a new project, provide a project name:

```
sassy new_project --create
```

> Note: A git repository will be created.

### Add a feature to your project

To add a feature to your project.

```
sassy new_project new_feature --create
```

To add a feature by selecting folders in your project.

Options are:
    
- *a `applications`
- *d `domains`
- *i `interfaces`
- *p `providers`

> Example: Create a feature `new_feature` in `applications` and `domains` folders.

```
sassy new_project new_feature *a,*d --create
```

### Delete a feature in your project

To delete a feature in your project.

```
sassy new_project new_feature --delete
```

To delete a feature by selecting folders in your project.

Options are:

- *a `applications`
- *d `domains`
- *i `interfaces`
- *p `providers`

> Example: Delete a feature `new_feature` in `applications` and `domains` folders.

```
sassy new_project new_feature *a,*d --delete
```

## Documentation available in this repository at:
https://halia-ca.gitlab.io/sassy
