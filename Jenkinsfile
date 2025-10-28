pipeline {
    agent any

    environment {
        // Переменные окружения для путей и команд Windows
        CMD = 'C:\\Windows\\System32\\cmd.exe'
        PM2_CMD = 'C:\\Users\\Diana\\AppData\\Roaming\\npm\\pm2.cmd'
        PYTHON_EXE = 'C:\\Program Files\\Python313\\python.exe'
        // TARGET_DIR — это каталог, где лежат Django/Vue проекты (для запуска и тестов)
        TARGET_DIR = 'C:\\Users\\Diana\\OneDrive\\Desktop\\DevOps\\2LR-Server'
        REPO_URL = 'https://github.com/DianaParygina/2LR.git'
        BUILD_VERSION = "${BUILD_NUMBER}"
        REGISTRY = "localhost:5000"
    }

    triggers { 
        githubPush() 
    }

    stages {
        stage('Git Safety Configuration') {
            steps {
                bat """
                    git config --global --add safe.directory "${TARGET_DIR}"
                    git config --global --add safe.directory "*"
                """
            }
        }

        stage('Clone or Update Code') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    bat """
                        if not exist "${TARGET_DIR}\\.git" (
                            echo Cloning fresh repo...
                            rmdir /S /Q "${TARGET_DIR}" 2>nul || echo No old folder
                            git clone -b main https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git "${TARGET_DIR}"
                        ) else (
                            echo Updating existing repo...
                            cd "${TARGET_DIR}"
                            git reset --hard
                            git clean -fd
                            git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git main
                        )
                    """
                }
            }
        }

        stage('Start Backend Server') {
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    call "${PM2_CMD}" delete django || echo No existing Django process
                    call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000
                """
            }
        }

        stage('Start Frontend Server') {
            steps {
                bat """
                    cd "${TARGET_DIR}\\client"
                    call "${PM2_CMD}" delete vue || echo No existing Vue process
                    
                    :: Передаем команду 'npm run dev' в PM2 через cmd.exe, чтобы обеспечить корректный запуск
                    call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"
                    
                    echo Frontend started in background via PM2
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    try {
                        bat """
                            cd "${TARGET_DIR}"
                            "${PYTHON_EXE}" manage.py test dogs
                        """
                        echo "Tests passed! Keeping servers running."
                    } catch (err) {
                        echo "Tests failed! Stopping servers..."
                        bat """
                            "${PM2_CMD}" delete django || echo No Django process to delete
                            "${PM2_CMD}" delete vue || echo No Vue process to delete
                        """
                        error("Integration tests failed. Servers stopped.")
                    }
                }
            }
        }

        stage('Build Containers') {
            when { 
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    docker compose build
                """
            }
        }

        stage('Tag & Push Docker Images to Local Registry') {
            when { 
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    echo Tagging and pushing images to registry...

                    docker tag backend ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker tag nginx ${REGISTRY}/nginx:build-${BUILD_VERSION}

                    docker push ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker push ${REGISTRY}/nginx:build-${BUILD_VERSION}

                    echo Also update latest tags...
                    docker tag backend ${REGISTRY}/backend:latest
                    docker tag nginx ${REGISTRY}/nginx:latest
                    docker push ${REGISTRY}/backend:latest
                    docker push ${REGISTRY}/nginx:latest
                """
            }
        }

        stage('Restart Application with Docker') {
            when { 
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    docker compose down
                    docker compose up -d
                """
            }
        }
        
        stage('Merge fix into main and deploy') {
            when { 
                expression { 
                    (env.BRANCH_NAME?.contains('fix') || env.GIT_BRANCH?.contains('fix')) && 
                    currentBuild.currentResult == 'SUCCESS'
                } 
            }
            steps {
                script {
                    withCredentials([
                        usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                        string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                    ]) {
                        bat """
                            :: *** НАСТРОЙКА GIT ***
                            git config --global --add safe.directory "${TARGET_DIR}"
                            
                            git config user.name "%GIT_USER%"
                            git config user.email "%GIT_EMAIL%"

                            :: *** 1. GIT-ОПЕРАЦИИ В JENKINS WORKSPACE ***
                            
                            git checkout main
                            git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git main
                            git merge origin/fix --no-ff -m "Auto-merge from Jenkins after successful tests"
                            git push https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git main

                            git checkout fix
                            git reset --hard main
                            git push --force https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git fix

                            :: *** 2. ОБНОВЛЕНИЕ КОДА В TARGET_DIR ***
                            
                            cd "${TARGET_DIR}"
                            
                            :: Инициализация Git в целевой папке, если она еще не репозиторий
                            if not exist .git (
                                git init
                                git remote add origin https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git
                            )

                            :: Скачиваем самый свежий код из обновленной main
                            git fetch
                            git checkout main
                            git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2LR.git main 

                            :: *** 3. PM2-ОПЕРАЦИИ (ПЕРЕЗАПУСК) ***
                            
                            :: Перезапуск Django
                            call "${PM2_CMD}" delete django || echo No Django process
                            call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000

                            :: Перезапуск Vue
                            cd "${TARGET_DIR}\\client"
                            call "${PM2_CMD}" delete vue || echo No Vue process
                            call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"
                        """
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful!"
            echo "Backend and Frontend are running via PM2 with the latest code!"
            echo "Docker containers built and pushed as build-${BUILD_NUMBER}"
            echo "Backend: http://127.0.0.1:8000/"
            echo "Frontend: http://127.0.0.1:5173/"
        }
        failure {
            echo "Tests failed, merge and deployment skipped."
        }
    }
}