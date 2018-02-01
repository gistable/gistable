def _get_notes(prev_tag, next_tag):
    with hide('stdout'):
        commits = run("git log --graph --pretty=format:'%h - %s (%cr by %an)%d' "
                      + "--abbrev-commit --date=relative"+ " %s..%s" 
                      % (prev_tag, next_tag)).splitlines()
        commits.pop()        # prev_tag went out with the previous release notes.
        commits.reverse()    # order going down with time
        commits = "\n".join(commits)
        commits = re.sub(r"\\",r"__SUB__", commits)
        commits = re.sub(r"/",r"\\", commits)
        commits = re.sub(r"__SUB__", r"/", commits)

        tags = run("git tag -n2 --contains=%s" % prev_tag).splitlines()
        tags = tags[1:]      # again drop the prev tag.
        tags = "\n".join(tags)
        changed_tests = run("git diff --no-color --stat 7.1f0..7.1g2 | grep 'test\|behavior' | cut -d ' ' -f2 | xargs grep 'def test'").splitlines()
        pattern = r"([^:]+):\s+def test([^(]*)\("
        tests_by_file = {}
        for t in changed_tests:
            filename, testname = re.match(pattern, t).group(1,2)
            testname = re.sub(r"(.)(?=[A-Z])", r"\1 ", testname).capitalize()  # Undo CamelCase style for readability.
            # Create a dict of tests by file
            tests = tests_by_file.get(filename, [])
            tests.append(testname)
            tests_by_file[filename] = tests
        # Assemble a string of all the expectations (tests by file)
        expectations = ""
        for f in tests_by_file.keys():
            expectations += "\n%s:\n   - " % f
            expectations += "\n   - ".join(tests_by_file[f])
            expectations += "\n"
        # Generate the output
        notes = """
RELEASE MESSAGES
---
%s

CHANGED EXPECTATIONS (not all tests have changed)
---
%s

COMMIT MESSAGES
---
%s
""" % (tags, expectations, commits)
        return notes
