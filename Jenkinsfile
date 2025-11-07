pipeline {
    agent any

    environment {
        // --- ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ---
        TARGET_DIR = 'C:\\Users\\Diana\\OneDrive\\Desktop\\DevOps\\2_1LR-Server'
        REPO_URL = 'https://github.com/DianaParygina/2_1LR.git'
        
        // Переменные для Docker
        BUILD_VERSION = "${BUILD_NUMBER}"
        REGISTRY = "localhost:5000"
    }

    triggers {
        // Запускает пайплайн при каждом push в репозиторий
        githubPush()
    }

    stages {
        stage('Clone Code') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    // Клонируем или обновляем код, работаем в текущей ветке 
                    // Для Docker-сборки нам нужен только актуальный код в TARGET_DIR
                    bat """
                        if not exist "${TARGET_DIR}\\.git" (
                            echo Cloning fresh repo...
                            rmdir /S /Q "${TARGET_DIR}" 2>nul || echo No old folder
                            git clone https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/2_1LR.git "${TARGET_DIR}"
                        ) else (
                            echo Updating existing repo...
                            cd "${TARGET_DIR}"
                            git fetch origin
                            git reset --hard origin/%GIT_BRANCH%
                            git clean -fd
                        )
                    """
                }
            }
        }

        stage('Build Containers and Run Tests') {
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo "Building containers (including Vue production build)..."
                    
                    // 1. Сборка контейнеров
                    docker compose build 
                    
                    echo "Running backend tests inside the 'backend' container..."
                    // 2. Запуск тестов в изолированном контейнере
                    // Примечание: Убедитесь, что ваш Docker Compose настроен для запуска тестов
                    docker compose run --rm backend python manage.py test
                """
            }
        }

        stage('Tag & Push Docker Images to Local Registry') {
            when { 
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo Tagging and pushing images to registry...

                    :: Используем короткие имена, которые Docker знает (backend:latest, nginx:latest)
                    
                    :: 1. Тегируем с версией билда
                    docker tag backend:latest ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker tag nginx:latest ${REGISTRY}/nginx:build-${BUILD_VERSION}

                    docker push ${REGISTRY}/backend:build-${BUILD_VERSION}
                    docker push ${REGISTRY}/nginx:build-${BUILD_VERSION}

                    :: 2. Обновляем тег latest для быстрого деплоя
                    docker tag backend:latest ${REGISTRY}/backend:latest
                    docker tag nginx:latest ${REGISTRY}/nginx:latest
                    
                    docker push ${REGISTRY}/backend:latest
                    docker push ${REGISTRY}/nginx:latest
                """
            }
        }

        stage('Merge fix -> main and Push') {
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
                            cd "${TARGET_DIR}"
                            git config user.name "%GIT_USER%"
                            git config user.email "%GIT_EMAIL%"

                            :: 1. Слияние и отправка в main
                            git checkout main
                            git pull origin main
                            git merge fix --no-ff -m "Auto-merge from Jenkins after successful CI (Build #${BUILD_NUMBER})"
                            git push origin main
                            
                            :: 2. Сброс ветки fix
                            git checkout fix
                            git reset --hard origin/main
                            git push --force origin fix
                        """
                    }
                }
            }
        }

        stage('Deploy Application') {
            when {
                // Деплой всегда происходит после успешной сборки и пуша образов
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    echo "Stopping and starting application with the latest images from registry..."
                    
                    // Перезапуск с принудительным пересозданием, чтобы использовать новые образы
                    docker compose up -d --force-recreate
                """
            }
        }
    }

    post {
        success {
            echo "Полный цикл CI/CD завершен успешно!"
            echo "Образы build-${BUILD_NUMBER} сохранены в локальном реестре."
            echo "Приложение перезапущено через Docker Compose."
        }
        failure {
            echo "Пайплайн завершился ошибкой. Проверьте лог сборки или Git-слияние."
        }
    }
}