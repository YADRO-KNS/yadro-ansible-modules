#!/usr/bin/env bash

set -e

WORKDIR=$(pwd)
BUILD_DIR=${WORKDIR}/build

print_usage() {
	echo "Parameters (provided via environment):"
	echo "    PYTHON_INTERPRETER    path to python interpreter (optional)"
	echo "Commands:"
	echo "    help                  display this help menu"
	echo "    prepare               prepare environment"
	echo "    sanity                execute collection sanity tests (docker required)"
	echo "    units                 execute collection unit tests (docker required)"
	echo "    integration           execute collection integration tests"
	echo "    build                 pack collection to galaxy tarball"
	echo "    webdocs               build html documentation for collection"
	echo "    clean                 clean all build files"
}

prepare() {
  echo "=> PREPARE ENVIRONMENT"

  if [[ "${PYTHON_INTERPRETER}" = "" ]] ; then
    PYTHON_INTERPRETER=$(which python3)
  fi

  if docker ps 1>/dev/null; then
    echo "Docker is OK"
  else
    echo "ERROR: Can't find active docker. Is it installed?"
    exit 1
  fi

  echo "Create virtual environment"
  ${PYTHON_INTERPRETER} -m venv "${BUILD_DIR}/venv"
  source "${BUILD_DIR}/venv/bin/activate"
  echo "Python: $(which python)"

  echo "Installing requirements"
  pip install --upgrade pip
  pip install -r "${BUILD_DIR}/build-requirements.txt"
}

clean() {
  echo "=> CLEAN"
  rm -rfv "${BUILD_DIR}"/yadro-obmc-*.tar.gz
  rm -rfv "${BUILD_DIR}/rst"
  rm -rfv "${BUILD_DIR}/html"
}

sanity() {
  ansible-test sanity -v --docker
}

units() {
  ansible-test units -v --docker --coverage
}

integration() {
  ansible-test integration
}

build() {
  ansible-galaxy collection build --output-path "${BUILD_DIR}"
}

webdocs() {
  if ! find "${BUILD_DIR}"/yadro-obmc-*.tar.gz; then
    echo "Build tarball not found. Execute 'build' command first."
    exit 1
  fi
  mkdir -p "${BUILD_DIR}/rst"
  chmod go-w "${BUILD_DIR}/rst"
  echo "Installing collection to virtual environment"
  ansible-galaxy collection install "${BUILD_DIR}"/yadro-obmc-*.tar.gz --force
  echo "Generate rst files"
  antsibull-docs collection --use-current --squash-hierarchy --dest-dir "${BUILD_DIR}/rst" yadro.obmc
  cp "${BUILD_DIR}/conf.py" "${BUILD_DIR}/rst"
  echo "Generate html pages"
  sphinx-build "${BUILD_DIR}/rst" "${BUILD_DIR}/html"
}

case $1 in
  help)
    print_usage
    exit 0
    ;;
  prepare)
    prepare
    exit 0
    ;;
  clean)
    clean
    exit 0
    ;;
  sanity)
    prepare
    sanity
    exit 0
    ;;
  units)
    prepare
    units
    exit 0
    ;;
  integration)
    prepare
    integration
    exit 0
    ;;
  build)
    clean
    prepare
    build
    exit 0
    ;;
  webdocs)
    clean
    prepare
    build
    webdocs
    exit 0
    ;;
  *)
    echo "Unknown command: $1"
    print_usage
    exit 1
    ;;
esac
