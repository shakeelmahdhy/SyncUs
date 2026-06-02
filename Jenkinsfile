pipeline {
    agent any
    
    environment {
        RENDER_API_KEY = credentials('render-api-key')
        
        RENDER_BACKEND_DEPLOY_HOOK = "https://api.render.com/deploy/srv-d8f6gii8qa3s738l1smg?key=BzIlVQeFRzY"
        
        RENDER_FRONTEND_DEPLOY_HOOK = "https://api.render.com/deploy/srv-d8f6kpl53gjs739ol8sg?key=qwONUKftKJo"
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
                            sh 'npm install'
                            sh 'npm run build'
                        }
                    }
                }

                stage('Backend Build') {
                    steps {
                        dir('backend') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
            }
        }

        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        python -m pytest tests/ -v
                    '''
                }
            }
        }
        
        stage('Deploy to Render') {
            steps {
                script {
                    echo "Deploying Backend to Render..."
                    sh """
                        curl -X POST "${RENDER_BACKEND_DEPLOY_HOOK}" \
                        -H "Accept: application/json" \
                        -w "HTTP Status: %{http_code}\\n"
                    """
        
                    echo "Deploying Frontend to Render..."
                    sh """
                        curl -X POST "${RENDER_FRONTEND_DEPLOY_HOOK}" \
                        -H "Accept: application/json" \
                        -w "HTTP Status: %{http_code}\\n"
                    """
                    
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