import sys
import requests
import argparse
import logging
import json
import datetime

from veracode_api_py import VeracodeAPI as vapi

def creds_expire_days_warning():
    creds = vapi().get_creds()
    exp = datetime.datetime.strptime(creds['expiration_ts'], "%Y-%m-%dT%H:%M:%S.%f%z")
    delta = exp - datetime.datetime.now().astimezone() #we get a datetime with timezone...
    if (delta.days < 7):
        print('These API credentials expire ', creds['expiration_ts'])

def find_team_named(teamname):
    teams = vapi().get_teams(all_for_org=True)
    for team in teams:
        if team["team_name"] == teamname:
            return[team]
    return []

def create_team(teamname,businessunit=""):
    # we will check to see if we already have a team with this name and just return it, if so
    existingteam = find_team_named(teamname)
    if len(existingteam) > 0: 
        teamguid = existingteam[0]["team_id"]
        logging.info("Found team named {} with guid {}".format(teamname,teamguid))
        return teamguid

    if businessunit == "":
        r = vapi().create_team(team_name=teamname)
    else:
        r = vapi().create_team(team_name=teamname,business_unit=businessunit)
    return r["team_id"]

def find_user_named(username):
    return vapi().get_user_by_name(username) # note that this call always returns a list of 1, or 0

def create_api_user(apiname,email,teamguid):
    existinguser = find_user_named(apiname)
    if len(existinguser) > 0:
        # return existing user rather than creating new one
        userguid = existinguser[0]["user_id"]
        logging.info("Found a user named {} with guid {}".format(apiname,userguid))
        return userguid

    r = vapi().create_user(email=email, firstname=apiname, lastname="API User",type="API",
            roles=[],teams=[teamguid],username=apiname)
    return r["user_id"]

def add_users_to_team(teamguid, users):
    return vapi().update_team(teamguid,members=users)

def find_app_named(appname):
    apps = vapi().get_app_by_name(appname)
    if len(apps) == 0:
        return []
    
    for app in apps:
        if app["profile"]["name"] == appname:
            return [app]

def create_app(appname,teamguid,businesscriticality="HIGH",businessunit=""):
    if len(find_app_named(appname)) > 0:
        errormsg = "There is already an application named {}".format(appname)
        logging.error(errormsg)
        print(errormsg)
        return 0

    if businessunit == "":
        r = vapi().create_app(app_name=appname,business_criticality=businesscriticality,teams=[teamguid])
    else:
        r = vapi().create_app(app_name=appname,business_criticality=businesscriticality,
            teams=[teamguid],business_unit=businessunit)
    return r["guid"]

def create_workspace(appname):
    return vapi().create_workspace(appname)

def main():
    parser = argparse.ArgumentParser(
        description='This script creates an application profile, api user, team and workspace for an application.')
    parser.add_argument('-a', '--appname',help='Name of the application profile to create',required=True)
    parser.add_argument('-e', '--email',help='Email address for the API user to be created',required=True)
    parser.add_argument('-b', '--businessunit',required=False, help='Business unit for the team and application profile (optional)')
    parser.add_argument('-c', '--businesscriticality',default="HIGH", help='Business criticality for the application profile (defaults to HIGH).')
    parser.add_argument('-u', '--usernames',nargs="+", required=False, help='List of usernames to be added to the team (optional).')
    args = parser.parse_args()

    appname = args.appname
    email = args.email
    businessunit = args.businessunit
    businesscriticality = args.businesscriticality
    usernames = args.usernames

    logging.basicConfig(filename='vconboardapp.log',
                        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S%p',
                        level=logging.INFO)

    # CHECK FOR CREDENTIALS EXPIRATION
    creds_expire_days_warning()

    #create team
    team_guid = create_team(teamname=appname,businessunit=businessunit)
    logging.info("Using team named {} with guid {}".format(appname,team_guid))

    #create api user
    api_username = 'api-{}'.format(appname)
    user_guid = create_api_user(api_username,email,team_guid)
    logging.info("Using API user with guid {}".format(user_guid))

    #add users to team
    if usernames == None:
        usernames = [ api_username]
    else:
        usernames.append(api_username)
    add_users_to_team(team_guid,usernames)
    logging.info("Added users to team {}: {}".format(team_guid, usernames))

    #create application profile
    app_guid = create_app(appname,team_guid,businesscriticality=businesscriticality,businessunit=businessunit)
    if app_guid == 0: return
    logging.info("Created application named {} with guid {}".format(appname, app_guid))

    #create workspace
    workspace_guid = create_workspace(appname)
    logging.info("Created workspace named {} with guid {}".format(appname,workspace_guid))

    print("Success. Check the logs for the IDs for the newly created application profile, workspace, team and API user.")
    print("Don't forget to sign into the platform with the user to generate your API credentials!")

if __name__ == '__main__':
    main()