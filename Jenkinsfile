pipeline {
    // agent none, deliberately. The two deploy stages below only wait on
    // homelab-k8s, which runs on label 'ops' -- a different node. Holding an
    // 'ansible' executor while waiting for one is how jenkins-node-1 deadlocked
    // for 18 hours on 2026-09-01: wrappers pinned to one node blocked on
    // downstream builds that needed another. node-2 has only TWO executors, so
    // two concurrent deploys here are enough to wedge it the same way.
    agent none

    options {
        buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '30'))
    }

    environment {
        // Set ECR_REGISTRY as a Jenkins global env var; the default is a placeholder account.
        ECR_REGISTRY = "${env.ECR_REGISTRY ?: '123456789012.dkr.ecr.us-west-2.amazonaws.com'}"
        ECR_REPO = 'homelab/wagtail-resume'
        AWS_REGION = 'us-west-2'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build and publish') {
            agent { label 'ansible' }

            stages {
                stage('Checkout') {
                    steps {
                        checkout scm
                    }
                }

                stage('Build Docker Image') {
                    steps {
                        script {
                            sh """
                                docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} .
                                docker tag ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:latest
                            """
                        }
                    }
                }

                stage('Push to ECR') {
                    steps {
                        withCredentials([
                            [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'ecr-credentials', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']
                        ]) {
                            script {
                                sh """
                                    docker run --rm \
                                        -e AWS_ACCESS_KEY_ID \
                                        -e AWS_SECRET_ACCESS_KEY \
                                        amazon/aws-cli ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                                    docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                                    docker push ${ECR_REGISTRY}/${ECR_REPO}:latest
                                """
                            }
                        }
                    }
                }
            }

            // Cleanup belongs to the stage that built the image: it needs the
            // workspace, and this is the only scope guaranteed to be on the
            // agent that created the tags.
            post {
                always {
                    sh "docker rmi ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} || true"
                }
            }
        }

        // No agent on these two on purpose -- see the note on `agent none`.
        // `build` needs no workspace, so they run on a flyweight executor.
        stage('Refresh ECR Credentials') {
            steps {
                build job: 'homelab-k8s',
                    parameters: [
                        string(name: 'CLUSTER', value: 'k3s-public'),
                        string(name: 'ACTION', value: 'refresh-ecr'),
                        string(name: 'NAMESPACE', value: 'resume-site'),
                        booleanParam(name: 'DRY_RUN', value: false)
                    ],
                    wait: true
            }
        }

        stage('Deploy to k3s-public') {
            steps {
                build job: 'homelab-k8s',
                    parameters: [
                        string(name: 'CLUSTER', value: 'k3s-public'),
                        string(name: 'ACTION', value: 'restart'),
                        string(name: 'NAMESPACE', value: 'resume-site'),
                        string(name: 'APP', value: 'wagtail'),
                        booleanParam(name: 'DRY_RUN', value: false)
                    ],
                    wait: true
            }
        }
    }

    post {
        success {
            echo 'Deployment successful! Site available at https://resume.nonagonmedia.net'
        }
        failure {
            echo 'Deployment failed. Check logs for details.'
        }
    }
}
