pipeline {
    agent any
    
    environment {
        RENDER_API_KEY = credentials('render-api-key')
        
        RENDER_BACKEND_DEPLOY_HOOK = credentials('backend-deploy-hook')
        
        RENDER_FRONTEND_DEPLOY_HOOK = credentials('frontend-deploy-hook')
    }
    
    options {
        skipDefaultCheckout()
    }
    
    tools {        
        nodejs "node"
    }


    stages {
        stage('Checkout') {
            steps {
                git branch: 'integration/dev/matching', credentialsId: 'Git token', url: 'https://github.com/shakeelmahdhy/SyncUs.git'
            }
        }
        stage('Build') {
            parallel {
                stage('Frontend Build') {
                    steps {
                        dir('frontend') {
                            bat 'npm install'
                            bat 'npm run build'
                        }
                    }
                }

                stage('Backend Build') {
                    steps {
                        dir('backend') {
                            bat '''
                                where python || (echo Python is not installed or not on PATH. & exit /b 1)
                                python -m venv venv
                                venv\\Scripts\\python -m pip install -r requirements.txt
                            '''
                        }
                    }
                }
            }
        }

        stage('Backend Test') {
            steps {
                dir('backend') {
                    bat '''
                        venv\\Scripts\\python -m pytest tests/ -v
                    '''
                }
            }
        }
        
        stage('Deploy to Render') {
            steps {
                script {
                    echo "Deploying Backend to Render..."
                    bat '''
                        curl -X POST "%RENDER_BACKEND_DEPLOY_HOOK%" -H "Accept: application/json"
                    '''
        
                    echo "Deploying Frontend to Render..."
                    bat '''
                        curl -X POST "%RENDER_FRONTEND_DEPLOY_HOOK%" -H "Accept: application/json"
                    '''
                    
                    echo "Deployment requests sent successfully!"
                }
            }
        }
    }
    post {
        success {
            // Actions after the build succeeds
            echo 'Build was successful!'
        }
        failure {
            // Actions after the build fails
            echo 'Build failed. Check logs.'
        }
    }
}