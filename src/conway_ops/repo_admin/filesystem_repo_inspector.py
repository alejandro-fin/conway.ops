import git
import datetime as _dt

from conway.observability.logger                                    import Logger
from conway.util.date_utils                                         import DateUtils

from conway_ops.repo_admin.repo_inspector                           import RepoInspector, CommitInfo, CommittedFileInfo
from conway_ops.util.git_local_client                                     import GitLocalClient


class FileSystem_RepoInspector(RepoInspector):

    '''
    Utility class that is able to execute GIT commands for repos located in the file system.

    :param str parent_url: A string identifying the location under which the repo of interest lives as
        a "subfolder" or "sub resource". May be a path to the local file system or the URL to a remote server.
    :param str repo_name: A string identifying the name of the repo of interest, as a "subfolder"
        or "sub resource" under the ``parent_url``.

    '''
    def __init__(self, parent_url, repo_name):

        super().__init__(parent_url, repo_name)

        self.executor                       = GitLocalClient(parent_url + "/" + repo_name)

    def init_repo(self):
        '''
        Initializes an empty repo and returns a GitPython handle for it.
        
        '''
        full_path                           = self.parent_url + "/" + self.repo_name
        repo                                = git.Repo.init(full_path)
        return repo


    async def current_branch(self):
        '''
        :return: The name of the current branch
        :rtype: str
        '''
        result                              = await self.executor.execute(command = "git rev-parse --abbrev-ref HEAD")
        return result
    
    async def modified_files(self):
        '''
        :return: List of files that have been modified but not yet staged. In the boundary case where a file
            has an unstaged deletion, that does not count as "modified" as per the semantics of this method.
        :rtype: list
        '''
        raw                                 = await self.executor.execute(command = "git ls-files -m")

        # raw is something like
        #
        #       'src/vulnerability_management/projector/vm_database_projector.py\nsrc/vulnerability_management/util/static_globals.py'
        #
        # so need to split string by new lines
        #
        files_l                             = [x for x in raw.split("\n") if len(x) > 0]

        # Under git semantics, the modified files obtained by doing "git ls-files -m" includes unstaged deletions.
        # So to get the "real" list of modified files, exclude deletes
        #
        deleted_files_l                     = await self.deleted_files()
        result                              = [f for f in files_l if not f in deleted_files_l]

        return result
    
    async def deleted_files(self):
        '''
        :return: List of files with an unstaged deletion
        :rtype: list
        '''
        raw                                 = await self.executor.execute(command = "git ls-files -d")
        # raw is something like
        #
        #       'src/vulnerability_management/projector/vm_database_projector.py\nsrc/vulnerability_management/util/static_globals.py'
        #
        # so need to split string by new lines
        #
        result                              = [x for x in raw.split("\n") if len(x) > 0]

        return result

    async def untracked_files(self):
        '''
        :return: List of files that are not tracked
        :rtype: list
        '''
        raw                                 = await self.executor.execute(command = "git ls-files -o --exclude-standard")
        # raw is something like
        #
        #       'src/vulnerability_management/projector/vm_database_projector.py\nsrc/vulnerability_management/util/static_globals.py'
        #
        # so need to split string by new lines
        #
        result                              = [x for x in raw.split("\n") if len(x) > 0]

        return result

    async def last_commit(self):
        '''
        :return: A :class:`CommitInfo` with information about last commit"
        :rtype: str
        '''
        raw                                 = await self.executor.execute(command = 'git log -1 --pretty=format:"%H|%ai|%s"')

        # raw is something like
        #
        #   'a72013ecceca532f6d99453d4a9a5a67d5ce8a90|2023-06-05|Added logic to create submissions directory if missing'
        #
        # so we must split it by the delimeter "|" and parse each token as required
        #
        #   GOTCHA:
        #       In Linux, it seems that raw is surrounded by double quotes, so it is something like:
        #
        #   '"a72013ecceca532f6d99453d4a9a5a67d5ce8a90|2023-06-05|Added logic to create submissions directory if missing"'
        #
        #   So for that reason we strip off any leading or trailing double quote
        #
        tokens                              = raw.strip('"').split("|")
        commit_hash                         = tokens[0]
        
        
        #commit_ts                           = Timestamp.from_datetime(_dt.datetime.strptime(tokens[1], "%Y-%m-%d"))

        # tokens[1] is something like
        #
        #           "2023-06-14 20:32:57 -0700"
        #
        # and we want to convert it ``commit_ts``, something like
        #
        #           "230614.203257"
        #
        parsed_dt                           =  _dt.datetime.strptime(tokens[1], "%Y-%m-%d %H:%M:%S %z")

        # Convert the commit date the the standard timezone used in CCL, which is California
        #
        parsed_dt                           = DateUtils().to_ccl_timezone(parsed_dt)


        commit_ts                           = parsed_dt.strftime("%y%m%d.%H%M%S")

        commit_msg                          = "|".join(tokens[2:])

        result                              = CommitInfo(commit_hash, commit_msg, commit_ts)

        return result
    
    async def branches(self):
        '''
        :return: (local) branches for the repo
        :rtype: list[str]
        '''
        raw                                 = await self.executor.execute(command = 'git branch')
        # raw is something like
        #
        #               '  ah-dev\n  integration\n  operate\n* story_1485'
        #
        # so to turn it into a list we must split by new lines and then strip out empty spaces and the "*"
        result                              = [b.strip("*").strip() for b in raw.split("\n") if not "->" in b]
        return result

    async def checkout(self, branch_name):
        '''
        :return: A status from switching to branch ``branch_name``
        :rtype: str
        '''
        result                              = await self.executor.execute(command = "git checkout " + str(branch_name))
        return result

    async def committed_files(self):
        '''
        Returns an iterable over CommitedFileInfo objects, yielding in chronological order the history of commits
        (i.e., a log) for the repo associated to this :class:`RepoInspector`
        '''
        log                                             = await self.executor.execute(command = "git log --name-only")
        commits                                         = log.split("commit ")
        commits                                         = [c for c in commits if len(c)>0] # Filter out spurious tokens

        result                                          = []


        for commit_idx in range(len(commits)): # Use reversed to list commits in the order in which they were made
            commit                                      = commits[commit_idx]

            # commit_idx goes like 0, 1, 2, ..., listing commits in reverse order, so if we count commits
            # from the first commit to the last, we need to make commit_nb go in the reverse ordering: .., 2, 1, 0
            commit_nb                                   = len(commits) - 1 - commit_idx
            lines                                       = commit.split("\n")
            '''
            The business logic below is inspired by this observation: if we print the lines
            with a prefix for the line number, by doing

                    for idx in range(len(lines)):
                        line = lines[idx]
                        print(str(idx) + ": " + line)

            then the result is something like

                0: 0d7521b185f4ba7748ca1e78f990b61a4bdfd8b8
                1: Author: Alejandro Hernandez <alejandro.hernandez@finastra.com>
                2: Date:   Wed May 17 14:03:58 2023 -0700
                3: 
                4:     [LEA UserStory 1455] Moved notebooks to ops repo
                5: 
                6: src/notebooks/.ipynb_checkpoints/GIT dashboard-checkpoint.ipynb
                7: src/notebooks/.ipynb_checkpoints/Scratch-checkpoint.ipynb
                8: src/notebooks/.ipynb_checkpoints/exploreClassifier-checkpoint.ipynb

                        ...             ...

            (Preliminary) UPSHOT: this tells that lines 0,1,2,4 give us the hash, author, date and summary, and lines 6+ the 
                files that changed.

            The above needs to be more nuanced, because if a commit is a merge, then it looks like this:

                0: e7f556f218ad218a2484581e0b7efec522dcf33a
                1: Merge: e9fc7d3 5019add
                2: Author: Alejandro Hernandez at CC Labs <alejandro@chateauclaudia-labs.com>
                3: Date:   Sat Jun 3 21:22:05 2023 -0700
                4:    Merge pull request #1 from ChateauClaudia-Labs/integration
                5:    
                6:    First MVP

            So for the (real UPSHOT):
            - As we parse lines, if they start with "Author:" or "Date", that is whwere we get these fields from
            - If a list is not blank but starts with blanks, then we treat it as part of the Summary
            - Only when we are past the lines that start with blanks we assume we have the committed files
            - And be aware that for merge commits, there might not be any files at all...

            So we traverse through these states, progressing the line_idx as we go

            '''
            line_idx                                        = 0
            hash                                            = lines[line_idx]

            author                                          = None
            date                                            = None
            summary                                         = None

            MAX_LINES                                       = len(lines)
            A_SPACE                                         = " "
            def _advance_to_summary():
                nonlocal author
                nonlocal date
                nonlocal line_idx

                while line_idx + 1 < MAX_LINES:
                    next_line                               = lines[line_idx + 1]
                    if next_line.startswith("Author:"):
                        author                              = next_line.strip("Author:").strip()
                    elif next_line.startswith("Date:"):
                        date                                = next_line.strip("Date:").strip()
                    elif next_line.startswith(A_SPACE):
                        # Got to the summary. Done parsing this phase of the text
                        return
                    
                    line_idx                                = line_idx + 1
            
            def _advance_to_committed_files():
                nonlocal summary
                nonlocal line_idx

                while line_idx + 1 < MAX_LINES:
                    next_line                               = lines[line_idx + 1]
                    if len(next_line) == 0:
                        line_idx                            = line_idx + 1
                        continue
                    elif next_line.startswith(A_SPACE):
                        # This is part of the summary
                        commit_msg                          = next_line.strip()
                        summary                             = commit_msg if summary is None else summary + "; " + commit_msg
                        line_idx                            = line_idx + 1
                    else:
                        # We don't start with a space or have an empty line, so we are done with the summary
                        return


            _advance_to_summary()
            _advance_to_committed_files()

            OFFSET                                          = line_idx + 1
            for idx in range(OFFSET, MAX_LINES):
                file                                        = lines[idx]
                if len(file) == 0: # Empty line, ignore it
                    continue

                cfi                                         = CommittedFileInfo(commit_nb           = commit_nb,
                                                                                commit_date         = date,
                                                                                summary             = summary,
                                                                                commit_file_nb      = idx - OFFSET,
                                                                                commit_file         = file,
                                                                                commit_hash         = hash,
                                                                                commit_author       = author)

                result.append(cfi)
            
            # Boundary case: perhaps there were no files at all, so in that case we still want to register
            # the commit
            if OFFSET >= MAX_LINES:
                cfi                                         = CommittedFileInfo(commit_nb           = commit_nb,
                                                                                commit_date         = date,
                                                                                summary             = summary,
                                                                                commit_file_nb      = 0,
                                                                                commit_file         = "",
                                                                                commit_hash         = hash,
                                                                                commit_author       = author)

                result.append(cfi)


        return result
    

    async def pull_request(self, scheduling_context, from_branch, to_branch, title, body):
        '''
        Creates and completes a pull request from the ``from_branch`` to the ``to_branch``.

        If anything goes wrong it raises an exception.

        :param scheduling_context: contains information about the stack at the time that this coroutine was created.
            Typical use case is to reflect in the logs that order in which the code was written (i.e., the logical
            order) as opposed to the order in which the code is executed asynchronousy.
        :type scheduling_context: conway.async_utils.scheduling_context.SchedulingContext

        :param str from_branch: GIT branch used as the source for the pull request
        :param str to_branch: GIT branch used as the destination for the pull request
        :param str title: this parameter is not used in this class, so it is ignored. The only reason the parameter
                exists is that it was mandated by the abstract parent class.
        :param str body: this parameter is not used in this class, so it is ignored. The only reason the parameter
                exists is that it was mandated by the abstract parent class.
        :returns: The pull request information. If the pull request was not created for a benign reason
                (for example, if there are no commits to merge from the `from_branch` to the `to_branch`)
                it returns None.
        '''    
        # Remember the original branch that is checked out in the remote, so that later we can go back to it
        original_branch     = await self.current_branch()
        executor            = GitLocalClient(self.parent_url + "/" + self.repo_name) 

        if to_branch != original_branch:
            status1         = await executor.execute(command = 'git checkout ' + to_branch)
            Logger.log_info(f"@ '{to_branch}' (local):\n\n{status1}",
                                  xlabels=scheduling_context.as_xlabel())

        status2             = await executor.execute(command = 'git merge ' + from_branch)
        Logger.log_info(f"'{from_branch}' (local) -> '{to_branch}' (local):\n\n{status2}",
                                  xlabels=scheduling_context.as_xlabel())

        # Restore original branch
        if to_branch != original_branch:
            status3             = await executor.execute(command = 'git checkout ' + original_branch)
            Logger.log_info(f"@ '{original_branch}' (local):\n\n{status3}",
                                  xlabels=scheduling_context.as_xlabel())

    async def update_local(self, scheduling_context, branch):
        '''
        Updates the local repo from the remote, for the given ``branch``.

        If anything goes wrong it raises an exception.

        :param scheduling_context: contains information about the stack at the time that this coroutine was created.
            Typical use case is to reflect in the logs that order in which the code was written (i.e., the logical
            order) as opposed to the order in which the code is executed asynchronousy.
        :type scheduling_context: conway.async_utils.scheduling_context.SchedulingContext

        :param str branch: repo local branch to update from the remote.
        '''
        Logger.log_info(f"local = '{self.parent_url}/{self.repo_name}'",
                                  xlabels=scheduling_context.as_xlabel())
        # Remember the original branch that is checked out in the remote, so that later we can go back to it
        original_branch     = await self.current_branch()

        executor            = GitLocalClient(self.parent_url + "/" + self.repo_name) 

        if branch != original_branch:
            status1         = await executor.execute(command = 'git checkout ' + branch)
            Logger.log_info(f"@ '{branch}' (local):\n\n{status1}",
                                  xlabels=scheduling_context.as_xlabel())

        status2             = await executor.execute(command = 'git pull')
        Logger.log_info(f"'{branch}' (remote) -> '{branch}' (local):\n\n{status2}",
                                  xlabels=scheduling_context.as_xlabel())

        # Restore original branch
        if branch != original_branch:
            status3             = await executor.execute(command = 'git checkout ' + original_branch)
            Logger.log_info(f"@ '{original_branch}' (local):\n\n{status3}",
                                  xlabels=scheduling_context.as_xlabel())
            