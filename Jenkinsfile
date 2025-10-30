pipeline {
    agent any

    environment {
        // Базовые переменные для репозитория и окружения
        TARGET_DIR = 'C:\\Users\\Diana\\OneDrive\\Desktop\\DevOps\\2_1LR-Server'
        REPO_URL = 'https://github.com/DianaParygina/2_1LR.git'
        
        // Переменные для Docker
        BUILD_VERSION = "${BUILD_NUMBER}"
        REGISTRY = "localhost:5000"
    }

    // Триггер запускается при каждом push в репозиторий
    triggers {
        githubPush()
    }

    stages {
        stage('Clone and Checkout Fix Branch') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    // Используем clean checkout и fetch, чтобы гарантировать актуальность
                    // Клонируем/Обновляем в ветке 'fix' для проведения тестов
                    bat """
                        if not exist "${TARGET_DIR}\\.git" (
                            echo Cloning fresh repo (branch fix)...
                            rmdir /S /Q "${TARGET_DIR}" 2>nul || echo No old folder
                            git clone -b fix https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2_1LR.git "${TARGET_DIR}"
                        ) else (
                            echo Updating existing repo...
                            cd "${TARGET_DIR}"
                            git fetch origin
                            git checkout fix
                            git reset --hard origin/fix
                            git clean -fd
                        )
                    """
                }
            }
        }

        stage('Build & Test Containers') {
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo "Building containers for testing..."
                    
                    // 1. Сборка контейнеров для тестов
                    docker compose build 
                    
                    echo "Running backend tests inside the 'backend' container..."
                    // 2. Запуск тестов. '--rm' удаляет контейнер после завершения.
                    // Если тесты упадут, этот шаг завершится ошибкой, и пайплайн остановится.
                    docker compose run --rm backend python manage.py test
                """
            }
        }
        
        // ---
        
        stage('Merge fix -> main and Push') {
            when {
                // Выполняется только если тесты прошли успешно
                expression { currentBuild.currentResult == 'SUCCESS' } 
            }
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                    string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                ]) {
                    bat """
                        cd "${TARGET_DIR}"
                        git config user.name "%GIT_USER%"
                        git config user.email "%GIT_EMAIL%"

                        :: 1. Обновляем main и сливаем fix
                        echo Checking out and pulling main branch...
                        git checkout main
                        git pull origin main

                        echo Merging fix -> main...
                        git merge fix --no-ff -m "Auto-merge from Jenkins after successful tests (Build #${BUILD_NUMBER})"

                        echo Pushing main (triggers next full deploy)...
                        git push origin main
                        
                        :: 2. Возвращаемся в fix и сбрасываем его
                        echo Syncing fix with new main...
                        git checkout fix
                        git reset --hard origin/main
                        git push --force origin fix
                    """
                }
            }
        }
        
        // ---

        stage('Tag & Push Docker Images to Local Registry') {
            when { 
                // Выполняется только после успешного слияния (и тестов)
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo Tagging and pushing images to registry...

                    // Тегируем с версией билда
                    docker tag task-sharing-management-system-new-backend:latest ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker tag task-sharing-management-system-new-nginx:latest ${REGISTRY}/nginx:build-${BUILD_VERSION}
                    
                    docker push ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker push ${REGISTRY}/nginx:build-${BUILD_VERSION}

                    // Обновляем тег latest
                    docker tag task-sharing-management-system-new-backend:latest ${REGISTRY}/backend:latest
                    docker tag task-sharing-management-system-new-nginx:latest ${REGISTRY}/nginx:latest
                    docker push ${REGISTRY}/backend:latest
                    docker push ${REGISTRY}/nginx:latest
                    
                    // Примечание: Убедитесь, что имена образов 'task-sharing-management-system-new-backend' 
                    // и 'task-sharing-management-system-new-nginx' соответствуют именам, созданным Docker Compose.
                """
            }
        }

        stage('Restart Application') {
            when { 
                // Выполняется только после успешного пуша образов
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo "Stopping and starting application with the latest images..."
                    // Используем --force-recreate, чтобы гарантировать использование новых образов, 
                    // даже если тег 'latest' не изменился для Docker Compose
                    docker compose up -d --force-recreate
                """
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful! Code merged fix -> main."
            echo "Containers tagged and pushed as build-${BUILD_NUMBER} to ${REGISTRY}"
            echo "Application fully restarted with Docker Compose."
        }
        failure {
            echo "❌ Pipeline Failed. Check the logs for the reason (Test failure or Merge conflict)."
        }
    }
}