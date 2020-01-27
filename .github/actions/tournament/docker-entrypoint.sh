#!/usr/bin/env bash
# unnoficial strict mode, note Bash<=4.3 chokes on empty arrays with set -u
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'
shopt -s nullglob globstar

README="README.md"
TOURNAMENT_OUTPUT_SCOREBOARD_MARKER="#== Scoreboard ==#"
README_SCOREBOARD_MARKER="### Most recent tournament results"

python_env_setup () {
  pipenv install
}

git_changed () {
  GIT_FILES_CHANGED=$(git status --porcelain | grep -cE '([MA]\W).+')
  echo "::set-output name=num_changed::${GIT_FILES_CHANGED}"
}

git_setup () {
  git config --global user.name "${GITHUB_ACTOR}"
  git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
  #git fetch --depth=1 origin +refs/tags/*:refs/tags/*
}

git_commit () {
  git_changed
  if [ "${GIT_FILES_CHANGED}" -eq 0 ]; then
    echo "::warning::No files changed, skipping commit"
  else
    git add "${README}"
    git commit -m "${INPUT_COMMIT_MESSAGE}"
  fi
}

run_tournament () {
	pipenv run python tournament.py random sam simple -n "${INPUT_NUM_HANDS}"
}

filter_scoreboard () {
  sed -e "1,/${TOURNAMENT_OUTPUT_SCOREBOARD_MARKER}/d"
}

delete_in_place_scoreboard () {
  sed -i -e "/${README_SCOREBOARD_MARKER}/,\$d" "${1}"
}

cd "${GITHUB_WORKSPACE}"
python_env_setup
git_setup

echo "running tournament..."
SCORES=$(run_tournament | filter_scoreboard)
SCORES=${SCORES//$'\n'/$'\n\n'}
echo "success"
echo "scores:"
echo "${SCORES}"

echo "modifying ${README}"
delete_in_place_scoreboard "${README}"
echo "${README_SCOREBOARD_MARKER}" >> "${README}"
echo "${SCORES}" >> "${README}"
echo "success"

if [[ "${INPUT_GIT_PUSH}" == "true" ]]; then
  echo "INPUT_GIT_PUSH is true, so committing and pushing"
  echo "committing changes"
  git_commit
  echo "success"
  echo "pushing changes"
  git push
  echo "success"
else
  echo "INPUT_GIT_PUSH is not true"
  git_changed
  echo "have ${GIT_FILES_CHANGED} files changed in git working tree"
  echo "(but not commited or pushed)"
fi

echo "all done"
exit 0
