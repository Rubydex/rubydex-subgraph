#!groovy
pipeline {
  agent {label 'slave01'}
  //change variables value below
  environment {
    py_instance="subgraph"
    dist_host="dev-java-gateway01"
    }
  stages {
    stage('Init') {
      steps {
        cleanWs()
        checkout scm
        dir(env.WORKSPACE) {
          sh "pwd"
        }
      }
    }

  stage('Package'){
    steps{
      dir(env.WORKSPACE) {
        sh "mkdir -p ${env.BUILD_TAG}"
        sh "tar -zcf ${env.BUILD_TAG}/${env.BUILD_TAG}.tar.gz --exclude=${env.BUILD_TAG} --exclude=Jenkinsfile ."
      }
    }
    }

    stage('Deploy'){
      steps{
        dir(env.WORKSPACE) {
          sshPublisher publishers:[
              sshPublisherDesc(
                configName: "${dist_host}",
                transfers: [
                  /*sshTransfer(
                    execCommand: "mkdir -p /data/rubydex/tpc/${py_instance} && cd /data/rubydex/tpc/tpc-scripts && ./python-control.sh stop ${py_instance}"
                  ),*/
                  sshTransfer(
                    sourceFiles: "${env.BUILD_TAG}/${env.BUILD_TAG}.tar.gz",
                    remoteDirectory: "tpc/${py_instance}",
                    cleanRemote: false, //never set to true
                    execTimeout: 120000,
                    execCommand: "cd /data/rubydex/tpc/${py_instance} && tar xvf ${env.BUILD_TAG}/${env.BUILD_TAG}.tar.gz -C ./ && rm -rf ${env.BUILD_TAG}"
                  )/*,
                  sshTransfer(
                    execCommand: "cd /data/rubydex/tpc/tpc-scripts && ./python-control.sh start ${py_instance}"
                  )*/
                ],
              verbose: true
            )
        ]
      }
    }
  }
  }
}
