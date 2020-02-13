pipeline {
    agent any
    stages {
        stage('build') {
            steps {
	        sh '''
	    	  . "/home/jamesb/miniconda3/etc/profile.d/conda.sh"
		  conda activate ch
		  python -m pytest
		'''

            }
        }
    }
}
