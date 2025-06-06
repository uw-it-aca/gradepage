# GradePage

[![Build Status](https://github.com/uw-it-aca/gradepage/workflows/Build%2C%20Test%20and%20Deploy/badge.svg)](https://github.com/uw-it-aca/gradepage/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/gradepage/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/gradepage?branch=main)

UW grade submission app

## System Requirements

- Python (3.10+)
- Docker
- Node

## Development Stack

- Django (5.2)
- Vue (3.2)
- Vite (2.9)
- Vitest (0.10.2)

## Design Stack

- Bootstrap (5.2)
- Bootstrap Icons (1.9.0)

## Installation

Clone the repository

        $ git clone git@github.com:uw-it-aca/compass.git

Go to your working directory

        $ cd compass

Copy the sample .env file so that your environment can be run.

        $ cp .env.sample .env

Update any .env variables for local development purposes

## Development (using Docker)

Docker/Docker Compose is used to containerize your local build environment and deploy it to an 'app' container which is exposed to your localhost so you can view your application. Docker Compose creates a 'devtools' container - which is used for local development. Changes made locally are automatically syncd to the 'app' container.

        $ docker-compose up --build

View your application using your specified port number in the .env file

        Demo: http://localhost:8000/

### Testing (using Vitest)

Run Vitest test scripts and generate coverage report

        $ npm run test
        $ npm run coverage

### Linting (using ESLint and Stylelint)

Run ESLint for JS linting

        $ npm run eslint

Run Stylelint for CSS linting

         $ npm run stylelint
