pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        DOCKERHUB_USERNAME = 'sahithi3377'
        DOCKERHUB_REPO = 'event-registration-system'
        GITHUB_REPO = 'https://github.com/Sahi-thi-3377/Event-Registration-System.git'
    }

    stages {

        stage('Build and Push All Versions') {
            steps {
                script {
                    def versions = [
                        [branch: 'main',             tag: 'v1'],
                        [branch: 'v2-register-user', tag: 'v2'],
                        [branch: 'v3-view-list',     tag: 'v3']
                    ]

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'dockerhub-creds',
                            usernameVariable: 'DH_USER',
                            passwordVariable: 'DH_TOKEN'
                        )
                    ]) {
                        bat '''
                            echo %DH_TOKEN% | docker login -u %DH_USER% --password-stdin
                        '''

                        for (version in versions) {
                            stage("Build and Push ${version.tag}") {
                                deleteDir()

                                checkout([
                                    $class: 'GitSCM',
                                    branches: [[name: "*/${version.branch}"]],
                                    userRemoteConfigs: [[
                                        url: "${GITHUB_REPO}"
                                    ]]
                                ])

                                bat """
                                    docker build -t ${DOCKERHUB_USERNAME}/${DOCKERHUB_REPO}:${version.tag} .
                                    docker push ${DOCKERHUB_USERNAME}/${DOCKERHUB_REPO}:${version.tag}
                                """
                            }
                        }

                        bat 'docker logout'
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                deleteDir()

                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: "${GITHUB_REPO}"
                    ]]
                ])

                bat '''
                    kubectl apply -f kubernetes/deployment-v1.yaml
                    kubectl apply -f kubernetes/service-v1.yaml

                    kubectl apply -f kubernetes/deployment-v2.yaml
                    kubectl apply -f kubernetes/service-v2.yaml

                    kubectl apply -f kubernetes/deployment-v3.yaml
                    kubectl apply -f kubernetes/service-v3.yaml

                    kubectl rollout status deployment/event-registration-v1
                    kubectl rollout status deployment/event-registration-v2
                    kubectl rollout status deployment/event-registration-v3

                    kubectl get deployments
                    kubectl get services
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All three versions have been built, pushed, and deployed.'
        }

        failure {
            echo 'FAILED: Check the Jenkins Console Output for the error.'
        }
    }
}