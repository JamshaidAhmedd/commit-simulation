#!/usr/bin/env python
import argparse
import os
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()
    directory = 'repository-contributions'  # Fixed directory name
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email

    if not os.path.exists(directory):
        os.mkdir(directory)
        os.chdir(directory)
        run(['git', 'init', '-b', 'main'])
        print(f"Initialized a new repository in {directory}")
    else:
        os.chdir(directory)

    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    start_date = curr_date.replace(hour=20, minute=0) - timedelta(args.days_before)
    for day in (start_date + timedelta(n) for n in range(args.days_before + args.days_after)):
        if (not args.no_weekends or day.weekday() < 5) and randint(0, 100) < args.frequency:
            for commit_time in (day + timedelta(minutes=m) for m in range(contributions_per_day(args))):
                contribute(commit_time)

    if repository is not None:
        run(['git', 'remote', 'remove', 'origin'], ignore_error=True)  # Remove existing remote
        run(['git', 'remote', 'add', 'origin', repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'add', 'README.md'])
        run(['git', 'commit', '-m', f"Automated contributions up to {curr_date.strftime('%Y-%m-%d')}"])
        run(['git', 'push', '-u', 'origin', 'main', '--force'])

    print('\nRepository contributions successfully updated!')


def contribute(date):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands, ignore_error=False):
    process = Popen(commands)
    process.wait()
    if process.returncode != 0 and not ignore_error:
        sys.exit(f"Command failed: {' '.join(commands)}")


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    max_c = args.max_commits
    if max_c > 20:
        max_c = 20
    if max_c < 1:
        max_c = 1
    return randint(1, max_c)


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--no_weekends', required=False, action='store_true', default=False,
                        help="Do not commit on weekends")
    parser.add_argument('-mc', '--max_commits', type=int, default=10, required=False,
                        help="Max commits per day (default: 10)")
    parser.add_argument('-fr', '--frequency', type=int, default=80, required=False,
                        help="Percentage of days with commits (default: 80)")
    parser.add_argument('-r', '--repository', type=str, required=False,
                        help="Remote repository URL (e.g., https://github.com/JamshaidAhmedd/commit-simulation)")
    parser.add_argument('-un', '--user_name', type=str, required=False,
                        help="Git user.name (overrides global config)")
    parser.add_argument('-ue', '--user_email', type=str, required=False,
                        help="Git user.email (overrides global config)")
    parser.add_argument('-db', '--days_before', type=int, default=365, required=False,
                        help="Number of days before today to simulate commits")
    parser.add_argument('-da', '--days_after', type=int, default=0, required=False,
                        help="Number of days after today to simulate commits")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
