pipeline {
    agent {
        label "agent"; 
    }
    environment {
        project_id = sh(script: 'gcloud config get-value project', returnStdout: true).trim()
        artifact_registry = 'us-central1-docker.pkg.dev'
        artifact_name = 'pythonapp'
        repo = 'jenkins-repo'
    }
    stages {
        stage('Preparando el entorno') {
            steps {
                sh 'whoami'
                sh 'echo POR FAVOR !!!!!! fijaos en este dato'
                sh 'hostname'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }
        
        stage('Calidad de código') {
            steps {
                sh 'whoami'
                sh 'hostname'
                sh 'python3 -m pylint app.py'
            }
        }

        stage('Tests') {         
            steps {
                sh 'whoami'
                sh 'hostname'
                sh 'python3 -m pytest'
            }
        }

        stage('Construcción del artefacto') {
            steps {
                sh 'whoami'
                sh 'hostname'
                sh 'docker build ${GIT_URL}#main -t ${artifact_registry}/${project_id}/${repo}/${artifact_name}:${GIT_COMMIT}'
            }
        }

        stage('Subir artefacto a repositorio docker') {
            steps {
                sh 'gcloud auth configure-docker ${artifact_registry} --quiet'
                sh 'docker push ${artifact_registry}/${project_id}/${repo}/${artifact_name}:${GIT_COMMIT}'
            }
        }

        // stage('Despliegue') {
        //     steps {
        //         sh 'whoami'
        //         sh ' echo si el dato anterior es root ... NOS HEMOS VUELTO LOCOS Y VAMOS A MORIR TODOS!!!!!!'
        //         sh 'hostname'
        //         sh 'docker run --name srgapp -d -p 5000:5000 srgjenkins:${GIT_COMMIT}'
        //     }
        // }
    }
}
