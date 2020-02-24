/* generated jenkins file used for building and deploying monitor in projects zz */
def final projectId = 'zz'
def final componentId = 'monitor'
def final credentialsId = "${projectId}-cd-cd-user-with-password"
def sharedLibraryRepository
def dockerRegistry
node {
  sharedLibraryRepository = env.SHARED_LIBRARY_REPOSITORY
  dockerRegistry = env.DOCKER_REGISTRY
}

library identifier: 'ods-library@production', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: sharedLibraryRepository,
   credentialsId: credentialsId])

/*
  See readme of shared library for usage and customization
  @ https://github.com/opendevstack/ods-jenkins-shared-library/blob/master/README.md
  eg. to create and set your own builder slave instead of
  the python slave used here - the code of the python slave can be found at
  https://github.com/opendevstack/ods-quickstarters/tree/master/common/jenkins-slaves/python
 */
odsPipeline(
  image: "${dockerRegistry}/cd/jenkins-slave-python:2.x",
  projectId: projectId,
  componentId: componentId,
  branchToEnvironmentMapping: [
    'master': 'test',
    '*': 'dev'
  ]
) { context ->
  stageBuild(context)
  stageStartOpenshiftBuild(context, [nexusHostWithBasicAuth: context.nexusHostWithBasicAuth, nexusHostWithoutScheme: context.nexusHost.tokenize('//')[1]])
  stageDeployToOpenshift(context)
}

def stageBuild(def context) {
  withEnv(["TAGVERSION=${context.tagversion}"]) {
      stage('Test') {
        String testLocation = 'build/test-results/test';
        String coverageLocation = 'build/test-results/coverage';
        def status = sh(
          script: """
            pip install --user virtualenv &&
            virtualenv venv &&
            . \$(pwd)/venv/bin/activate &&
            pip install -r src/test_requirements.txt &&
            export PYTHONPATH="src" &&
            mkdir -p ${testLocation} &&
            mkdir -p ${coverageLocation} &&
            cd src/tests &&
            nosetests -v --with-xunit --xunit-file=../../${testLocation}/nosetests.xml --with-coverage --cover-xml --cover-xml-file=../../${coverageLocation}/coverage.xml --cover-erase --cover-inclusive --cover-package=..
          """,
          returnStatus: true
        )
        junit "${testLocation}/nosetests.xml"
        stageScanForSonarqube(context)
        if (status != 0) {
          error "One or more unit tests failed!"
        }
      }
      stage('PEP8') {
        // Stage is VERY IMPORTANT! Do not remove or comment!
        sh """
          cd src &&
          pycodestyle --show-source --show-pep8 . &&
          pycodestyle --statistics -qq .
        """
      }
      stage('Build') {
         sh """
           mkdir docker/dist
           cp -r src docker/dist
         """
      }
  }
}
