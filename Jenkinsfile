pipeline {
    agent {
        label "agent"; 
    }
    environment {
        project_id = sh(script: 'gcloud config get-value project', returnStdout: true).trim()
        artifact_registry = 'us-central1-docker.pkg.dev'
        service_name = 'pythonapp'
        repo = 'jenkins-repo'
    }
    stages {
        stage('Preparando el entorno') {
            steps {
                sh 'echo Instalando dependencias del contenedor'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }
        
        stage('Calidad de código') {
            steps {
                sh 'echo Testeando la calidad del código'
                sh 'python3 -m pylint app.py > pylint_report.txt'
                sh 'cat pylint_report.txt'
            }
        }

        stage('Tests') {         
            steps {
                sh 'echo Testeando la aplicación'
                sh 'python3 -m pytest'
            }
        }

        stage('Construcción del artefacto') {
            steps {
                sh 'echo Construyendo la imágen de docker'
                sh 'docker build . -t ${artifact_registry}/${project_id}/${repo}/${service_name}:${GIT_COMMIT}'
            }
        }

        stage('Subir artefacto a repo') {
            steps {
                sh 'echo Subiendo la imágen de docker al "Artifact Registry" de Google Cloud'
                sh 'gcloud auth configure-docker ${artifact_registry} --quiet'
                sh 'docker push ${artifact_registry}/${project_id}/${repo}/${service_name}:${GIT_COMMIT}'
            }
        }

        stage('Desplegando la aplicación') {
            steps {
                sh 'echo Testearemos si la aplicación está ya levantada para actualizar la versión de la imágen, sino, desplegaremos el cloud run.'
                script {
                    def containerRunning = sh(returnStatus: true, script: "gcloud run services describe ${service_name} --format='value(status.url)' --region=\"us-central1\"") == 0

                    if (containerRunning) {
                        echo "El contenedor está en ejecución. Se actualizará la imagen."
                        sh("gcloud run services update ${service_name} --image=\"${artifact_registry}/${project_id}/${repo}/${service_name}:${GIT_COMMIT}\" --region=\"us-central1\" --port=5000")
                    } else {
                        echo "El contenedor no está en ejecución. Se realizará el despliegue del servicio."
                        sh("gcloud run deploy ${service_name} --image=\"${artifact_registry}/${project_id}/${repo}/${service_name}:${GIT_COMMIT}\" --region=\"us-central1\" --port=5000")
                    }
                }
                sh 'echo Publicamos el servicio de cloud run para todos los usuarios'
                sh 'gcloud run services add-iam-policy-binding ${service_name} --member="allUsers" --role="roles/run.invoker" --region="us-central1"'
            }
        }
    }
}
