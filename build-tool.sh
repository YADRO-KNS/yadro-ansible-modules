#!/usr/bin/env bash

set -e

WORKDIR=$(pwd)
BUILD_DIR=${WORKDIR}/build
TEST_DIR=${WORKDIR}/tests

DOCKER_MOCKUP_SERVER_IMAGE="***REMOVED***"
DOCKER_MOCKUP_SERVER_PORT=8000

SUBCOMMAND_ARGS="${*:2}"

print_usage() {
	echo "Parameters (provided via environment):"
	echo "    PYTHON_INTERPRETER    path to python interpreter (optional)"
	echo "Commands:"
	echo "    help                  display this help menu"
	echo "    prepare               prepare environment"
	echo "    sanity                execute collection sanity tests (docker required)"
	echo "    units                 execute collection unit tests (docker required)"
	echo "    integration           execute collection integration tests (docker required, mockup server will be used)"
	echo "    build                 pack collection to galaxy tarball"
	echo "    report                disaply test report"
	echo "    webdocs               build html documentation for collection"
	echo "    clean                 clean all build files"
}

prepare() {
  echo "=> PREPARE ENVIRONMENT"

  if docker ps 1>/dev/null; then
    echo "Docker is OK"
  else
    echo "ERROR: Can't find active docker. Is it installed?"
    exit 1
  fi

  if [[ -d "${BUILD_DIR}/venv" ]] ; then
    echo "Looks like environment exists. Activating..."
    source "${BUILD_DIR}/venv/bin/activate"
  else
    echo "Environment directory not found. Creating..."
    if [[ "${PYTHON_INTERPRETER}" = "" ]] ; then
      PYTHON_INTERPRETER=$(which python3)
    fi
    ${PYTHON_INTERPRETER} -m venv "${BUILD_DIR}/venv"
    source "${BUILD_DIR}/venv/bin/activate"
    echo "Installing requirements"
    pip install --upgrade pip
    pip install -r "${BUILD_DIR}/build-requirements.txt"
  fi
  echo "Python: $(which python)"
}

clean() {
  echo "=> CLEAN"
  rm -rfv "${BUILD_DIR}"/yadro-obmc-*.tar.gz
  rm -rfv "${BUILD_DIR}/rst"
  rm -rfv "${BUILD_DIR}/html"
  if [[ -d "${TEST_DIR}/output" ]]; then
    rm -rfv "${TEST_DIR}/output"
  fi
}

sanity() {
  echo "=> SANITY TESTS"
  ansible-test sanity -v --docker
}

units() {
  echo "=> UNIT TESTS"
  ansible-test units -v --docker --coverage
  sed -i 's/file="/file="tests\/unit\/plugins\//g' "${TEST_DIR}"/output/junit/*
  ansible-test coverage xml
  ansible-test coverage report
}

integration() {
  echo "=> INTEGRATION TESTS"

  echo "Creating mockup server"
  docker pull "${DOCKER_MOCKUP_SERVER_IMAGE}"
  CONTAINER_ID=$(docker run --rm -d "${DOCKER_MOCKUP_SERVER_IMAGE}")
  CONTAINER_IP_ADDRESS=$(docker inspect -f "{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}" "${CONTAINER_ID}")
  echo "Mockup server IP address: http://${CONTAINER_IP_ADDRESS}:${DOCKER_MOCKUP_SERVER_PORT}"

  echo "Creating integration_config.yml"
  (
    echo "---"
    echo "connection_hostname: http://${CONTAINER_IP_ADDRESS}"
    echo "connection_port: ${DOCKER_MOCKUP_SERVER_PORT}"
    echo "connection_username: admin"
    echo "connection_password: admin"
    echo "connection_validate_certs: false"
  ) > tests/integration/integration_config.yml

  echo "Executing ansible-test"
  set +e
  # shellcheck disable=SC2086
  ansible-test integration ${SUBCOMMAND_ARGS}
  ANSIBLE_TEST_RC=$?
  set -e

  echo "Destroying mockup server"
  docker kill "${CONTAINER_ID}" 1>/dev/null

  if [[ "${ANSIBLE_TEST_RC}" -eq 0 ]]; then
    echo "Tests finished successfuly"
  else
    echo "Tests failed"
    exit ${ANSIBLE_TEST_RC}
  fi
}

build() {
  echo "=> BUILD TAR"
  ansible-galaxy collection build --output-path "${BUILD_DIR}"
}

webdocs() {
  echo "=> BUILD WEBDOCS"
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
    clean
    prepare
    sanity
    exit 0
    ;;
  units)
    clean
    prepare
    units
    exit 0
    ;;
  integration)
    clean
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
