pipeline {
    agent {
        label "agent"; 
    }

    environment {
        BRANCH_NAME = "${GIT_BRANCH.split("/")[1]}"
        test_credentials = credentials('gcp-cloudrun-json-test')
        prod_credentials = credentials('gcp-cloudrun-json')
        region = 'us-central1'
        artifact_registry = "${region}-docker.pkg.dev"
        service_name = 'api-app'
        repo = 'jenkins-repo'
        test_path_url = '/osinfo' //Url with "/"
    }

    stages {
        stage('Preparando el entorno') {
            steps {
                script {
                    if (BRANCH_NAME == "dev") {
                        echo "Cargando credenciales de entorno de pruebas."
                        env.GOOGLE_APPLICATION_CREDENTIALS = test_credentials
                    } else if (BRANCH_NAME == "main") {
                        if (env.CHANGE_ID) {
                            echo "Cargando credenciales de entorno de producción.s"
                            env.GOOGLE_APPLICATION_CREDENTIALS = prod_credentials
                        } else {
                            error "Este cambio no es desde una pull request, por lo que la pipeline no se ejecutará. La rama main solo admitirá correr la pipeline se se hace PR"
                        }     
                    } else {
                        error "El nombre de la rama no es el correcto. Solo pueden ser 'main' o 'test'"
                    }
                    env.project_id = sh(script: 'jq -r ".project_id" $GOOGLE_APPLICATION_CREDENTIALS', returnStdout: true).trim()
                    env.dockerimg_name = "${artifact_registry}/${project_id}/${repo}/${service_name}:${GIT_COMMIT}"
                    service_account_email = sh(script: 'jq -r ".client_email" $GOOGLE_APPLICATION_CREDENTIALS', returnStdout: true).trim()
                    sh(script: 'gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS', returnStdout: true).trim()
                    sh(script: "gcloud config set account ${service_account_email}", returnStdout: true).trim()
                }
                sh 'echo Comprobando si Docker está instalado en la máquina'
                sh 'docker version'
                sh 'echo Instalando dependencias Python'
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
                sh 'echo Construyendo la imagen de Docker'
                sh 'docker build . -t ${dockerimg_name}'
                script {
                    echo "Obteniendo el puerto que utiliza la imágen para usarlo en el despliegue"
                    env.port = sh(script: "docker inspect --format='{{range \$p, \$conf := .Config.ExposedPorts}} {{\$p}} {{end}}' ${dockerimg_name} | grep -oE '[0-9]+'", returnStdout: true).trim()
                }
            }
        }

        stage('Subir artefacto a repo') {
            steps {
                sh 'echo Subiendo la imagen de Docker al "Artifact Registry" de Google Cloud'
                sh 'gcloud auth configure-docker ${artifact_registry} --quiet'
                sh 'docker push ${dockerimg_name}'
            }
        }

        stage('Desplegando la aplicación') {
            steps {
                sh 'echo Testearemos si la aplicación está ya levantada para actualizar la versión de la imagen, sino, desplegaremos el Cloud Run.'
                script {
                    def containerRunning = sh(script: "gcloud run services describe ${service_name} --format='value(status.url)' --region='us-central1' --project='${project_id}'", returnStatus: true) == 0

                    if (containerRunning) {
                        echo "El contenedor está en ejecución. Se actualizará la imagen."
                        sh("gcloud run services update ${service_name} --image='${dockerimg_name}' --region='${region}' --port='${port}' --project='${project_id}'")
                    } else {
                        echo "El contenedor no está en ejecución. Se realizará el despliegue del servicio."
                        sh("gcloud run deploy ${service_name} --image='${dockerimg_name}' --region='${region}' --port=${port} --project='${project_id}'")
                    }
                    sh 'echo Publicamos el servicio de Cloud Run para todos los usuarios'
                    sh 'gcloud run services add-iam-policy-binding ${service_name} --member="allUsers" --role="roles/run.invoker" --region="${region}" --project="${project_id}"'
                    sh 'echo Realizando test de la aplicación desplegada'

                    def url = sh(script: "gcloud run services describe ${service_name} --format='value(status.url)' --region='${region}' --project='${project_id}'", returnStdout: true).trim()
                    def responseCode = sh(script: "curl -s -o /dev/null -w '%{http_code}' ${url}${test_path_url}", returnStdout: true).trim()

                    if (responseCode == '200') {
                        echo 'El test pasó. La respuesta es 200 OK.'
                    } else {
                        error 'El test falló. La respuesta no es 200.'
                    }
                } 
            }
        }
    }
}