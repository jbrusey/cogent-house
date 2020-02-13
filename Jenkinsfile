pipeline {
    agent any
    stages {
        stage('build') {
            steps {
	    	  . "/home/jamesb/miniconda3/etc/profile.d/conda.sh"
		  conda activate ch
		  python -m pytest

            }
        }
    }
}
