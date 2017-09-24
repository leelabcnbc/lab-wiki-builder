#!/usr/bin/env bash

# inspired by https://gist.github.com/willprice/e07efd73fb7f13f917ea

setup_git() {
  git config --global user.email "leelabcnbc@gmail.com"
  git config --global user.name "leelabcnbc-bot"
}

setup_backup() {
  rm -rf ~/lab-wiki-gh-pages
  mkdir -p ~/lab-wiki-gh-pages/demo_proj
  # copy output.
  cp -af output/demo_proj/. ~/lab-wiki-gh-pages/demo_proj


  mkdir -p ~/lab-wiki-gh-pages/demo_ref
  # copy src, as I need those files for ipynb as well.
  cp -af src/demo_ref/. ~/lab-wiki-gh-pages/demo_ref

  # touch a nojekyll
  touch ~/lab-wiki-gh-pages/.nojekyll
}

commit_website_files() {
  git checkout -b gh-pages-new
  rm -rf *
  cp -af ~/lab-wiki-gh-pages/. .
  git add --all .
  # ci skip to ignore
  git commit --message "Circle CI build: ${CIRCLE_BUILD_URL} [ci skip]"
}

upload_files() {
  git push --quiet -f origin gh-pages-new:gh-pages > /dev/null 2>&1
}

setup_git
setup_backup
commit_website_files

if [ "$1" == "0" ]; then
    upload_files
    echo "done"
elif [ "$1" == "1" ]; then
    echo "mock"
fi

