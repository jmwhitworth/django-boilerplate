# django-boilerplate

This is a template repository for starting new django projects the way I like it.

## Packages

- uv as package manager
- Vite & `django-vite` for assets
- Tailwind v4
- `whitenoise`
- `django-tasks-db`
- In local/development:
    - `django-debug-toolbar`
    - `django-zeal` for N+1 detection

## Features

Includes a `common` app which has some base models/utils derived from HackSoftware's [Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide).

Includes a `users` app which overrides the default `User` model. It add no extra functionality out of the gate, but having it in place in a project from day 1 ensures that there's no complications in the future in the common situation where you need to add fields to the user model.

Includes Dockerfile and compose file for containerisation. It's tailored towards deploying via Dokploy, but can be easily modified.

## Prettifying

There's 3 packages for making things pretty:

- djhtml (Django prettifying)
- prettier
- rustywind

These can be ran individually, but there's also a `prettify.sh` bash script to make it a bit easier.
