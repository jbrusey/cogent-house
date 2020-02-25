pipeline {
    agent { dockerfile true }
    stages {
        stage('build') {
	    steps {
	        sh 'make clean'
	        sh 'make all'
	    }
	}
        stage('test') {
            steps {
	    	sh 'python -m unittest discover -s tests -p "test_base*"'
                sh 'python3.6 -m coverage run -m pytest --junit-xml=pytest.xml --ignore tests/test_automated_report.py --ignore tests/test_baselogger.py --ignore tests/test_baseif.py'
		sh 'python3.6 -m coverage xml'
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
