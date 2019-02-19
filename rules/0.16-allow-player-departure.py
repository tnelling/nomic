import util


def should_allow(pr):
    diff = pr.diff()

    if diff.modified_files or diff.added_files:
        raise Exception('All file changes must be deletions')

    author = pr.author()

    for removed_file in diff.removed_files:
        path = removed_file.path

        try:
            s_players, points_user, _ = path.split('/', 2)
        except:
            raise Exception('Removed file %s cannot be parsed to a player file path' % path)

        if s_players != 'players':
            raise Exception('Removed file %s is not a player file' % path)

        if author != points_user:
            raise Exception('%s cannot remove %s without approval' % (author, points_user))

    if author in util.users():
        raise Exception('User %s has not been fully removed.' % author)

    return True
