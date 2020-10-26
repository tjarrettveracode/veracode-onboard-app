# Veracode Onboard App

Quickly provision all the things in the Veracode platform to start scanning an application: team, API user, application profile, SCA Agent workspace.

When managing a large number of application profiles in Veracode, it's a good idea to set up each with its own team (to make it easy to manage access to the application), API user (to make it easy for the team to control their credentials and their user's access in in the pipeline), and SCA Agent workspace. This script automates the setup for these items.

## Setup

Clone this repository:

    git clone https://github.com/tjarrettveracode/veracode-onboard-app

Install dependencies:

    cd veracode-onboard-app
    pip install -r requirements.txt

(Optional) Save Veracode API credentials in `~/.veracode/credentials`

    [default]
    veracode_api_key_id = <YOUR_API_KEY_ID>
    veracode_api_key_secret = <YOUR_API_KEY_SECRET>

## Run

If you have saved credentials as above you can run:

    python vconboardapp.py (arguments)

Otherwise you will need to set environment variables:

    export VERACODE_API_KEY_ID=<YOUR_API_KEY_ID>
    export VERACODE_API_KEY_SECRET=<YOUR_API_KEY_SECRET>
    python vconboardapp.py (arguments)

Arguments supported include:

* `--appname`, `-a`: the name of the application to create. This will also be used for the team and API user.
* `--email`, `-e`: Email address for the API user that will be created.
* `--businessunit`, `-b`: Business unit for the team and application profile that will be created (optional).
* `--businesscriticality`, `-c`: Business criticality for the application profile that will be created, one of "VERY HIGH", "HIGH", "MEDIUM", "LOW", "VERY LOW". Defaults to "HIGH".
* `--usernames`, `-u` (opt): the user names to add to the team that will be created.

## NOTES

1. All actions and errors are logged to `vconboardapp.log`.
2. The script will return an error if there is already an app in the account with the same name. It will reuse a team or api user if one already exists with the same name.
