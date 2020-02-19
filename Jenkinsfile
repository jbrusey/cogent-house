pipeline {
    agent { dockerfile true }
    stages {
        stage('build') {
            steps {
                sh 'coverage run -m pytest --junit-xml=pytest.xml --ignore tests/test_automated_report.py --ignore tests/test_baselogger.py --ignore tests/test_baseif.py'
		sh 'coverage xml'
            }
        }
    }
    post {
        always {
            junit 'pytest.xml'
        }
    }
}
