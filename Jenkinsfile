pipeline {
    agent { dockerfile true }
    stages {
        stage('build') {
            steps {
                sh 'python -m pytest --junit-xml=pytest.xml --ignore tests/test_automated_report.py --ignore tests/test_baselogger.py --ignore tests/test_baseif.py'
            }
        }
    }
    post {
        always {
            junit 'pytest.xml'
        }
    }
}
