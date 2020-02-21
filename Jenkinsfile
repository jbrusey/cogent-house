pipeline {
    agent { dockerfile true }
    stages {
        state('build') {
	    steps {
	        sh 'make all'
		sh 'python setup.py develop'
	    }
	}
        stage('test') {
            steps {
                sh 'coverage run -m pytest --junit-xml=pytest.xml --ignore tests/test_automated_report.py --ignore tests/test_baselogger.py --ignore tests/test_baseif.py'
		sh 'coverage xml'
            }
        }
    }
    post {
        always {
            junit 'pytest.xml'
            cobertura coberturaReportFile: 'coverage.xml'
        }
    }
}
