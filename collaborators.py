# THIS FILE IS OUT OF BOUNDS

import util
from util import HttpVerb

def update(repo, users):
  collaborators = [c['login'] for c in util.request(_collaborators_url(repo)).json()]
  _remove_non_players(repo, users, collaborators)
  _add_new_players(repo, users, collaborators)

def _remove_non_players(repo, users, collaborators):
  for collaborator in collaborators:
    if not collaborator in users:
      print('%s is a collaborator, but not a player. Removing their status as a collaborator' % collaborator)
      util.request('%s/%s' % (_collaborators_url(repo), collaborator), HttpVerb.delete)


def _add_new_players(repo, users, collaborators):
  for user in users:
    if not user in collaborators:
      print('%s is a player, but not a collaborator. Adding them as a collaborator' % user)
      util.request('%s/%s' % (_collaborators_url(repo), user), HttpVerb.put)

def _collaborators_url(repo):
  return 'https://www.jefftk.com/nomic-github/repos/%s/collaborators' % repo
