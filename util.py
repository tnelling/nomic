import os
import re
import requests
import subprocess
import time
from enum import Enum
from typing import Callable, Dict, List

class HttpVerb(Enum):
  get = 1
  put = 2
  delete = 3

def _request_by_verb() -> Dict[HttpVerb, Callable[[str, Dict[str, str]], requests.Response]]:
  return {
    HttpVerb.get: requests.get,
    HttpVerb.put: requests.put,
    HttpVerb.delete: requests.delete
  }

def _ok_codes_by_verb() -> Dict[HttpVerb, List[int]]:
  return {
    HttpVerb.get: [200],
    HttpVerb.put: [201],
    HttpVerb.delete: [204]
  }

def request(url: str, verb=HttpVerb.get) -> requests.Response:
  request_headers = {'User-Agent': 'jeffkaufman/nomic'}
  response = _request_by_verb().get(verb)(url, headers=request_headers)

  for header in ['X-RateLimit-Limit',
                 'X-RateLimit-Remaining',
                 'X-RateLimit-Reset']:
    if header in response.headers:
      print('    > %s: %s' % (header, response.headers[header]))

  if response.status_code not in _ok_codes_by_verb().get(verb):
    print('   > %s' % response.content)

  response.raise_for_status()
  return response

def iso8601_to_ts(iso8601: str) -> int:
  return int(time.mktime(time.strptime(iso8601, "%Y-%m-%dT%H:%M:%SZ")))

def users() -> List[str]:
  return list(sorted(os.listdir('players/')))

def latest_master_commit_info(format) -> str:
  cmd = ['git', 'log', 'master', '-1', '--format=%s' % format]
  completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
  if completed_process.returncode != 0:
    raise Exception(completed_process)

  return completed_process.stdout.decode('utf-8')

def last_commit_ts() -> int:
  # When was the last commit on master?
  return int(latest_master_commit_info(format='%ct'))

def last_commit_sha() -> str:
  # What is the commit sha of the last commit on master?
  return latest_master_commit_info(format='%H').strip()

def seconds_since(ts) -> int:
  return int(time.time() - ts)

def seconds_to_days(seconds: int) -> int:
  return int(seconds / 60 / 60 / 24)

def days_since(ts: int) -> int:
  return seconds_to_days(seconds_since(ts))

def days_since_last_commit() -> int:
  return days_since(last_commit_ts())

def get_user_points() -> Dict[str, int]:
  points = {}

  for user in users():
    points[user] = 0

    bonus_directory = os.path.join('players', user, 'bonuses')
    if os.path.isdir(bonus_directory):
      for named_bonus in os.listdir(bonus_directory):
        with open(os.path.join(bonus_directory, named_bonus)) as inf:
          points[user] += int(inf.read())


  # Iterate through all commits in reverse chronological order, assigning
  # points to PR authors.
  #
  # We only look at master, and we look at the --first-parent history which
  # just shows the merges: http://www.davidchudzicki.com/posts/first-parent/
  cmd = ['git', 'log', 'master', '--first-parent', '--format=%H %s']
  completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
  if completed_process.returncode != 0:
    raise Exception(completed_process)
  process_output = completed_process.stdout.decode('utf-8')

  # This can't fully be trusted, since it's under the control of the person who
  # merges the PR, except that editing the merge text on GitHub is out of
  # bounds.
  merge_regexp = '^Merge pull request #[\\d]* from ([^/]*)/'
  for line in process_output.split('\n'):
    if not line.strip():
      continue

    hash, commit_subject = line.split(' ', 1)

    if hash == 'e5229a56a942126dc35c463d0f94f348b3d5389a':
      # Only look at PRs merged since restarting the game.
      break

    match = re.match(merge_regexp, commit_subject)
    if match:
      # Regexp match means this is a merge commit.

      commit_username, = match.groups()

      if commit_username in points:
        points[commit_username] += 1

  return points

def random() -> float:
  # Produces a number between 0 and 1 based on the hash of the most recent
  # commit to master.
  sha = last_commit_sha()
  if len(sha) != 40:
    raise Exception('commit hash wrong length: "%s"' % sha)

  def hash_to_int(s: str) -> int:
    return int(s, 16)

  biggest_possible_hash = 'f'*len(sha)

  return hash_to_int(sha) / hash_to_int(biggest_possible_hash)
